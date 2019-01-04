'''
AMMM Lab Heuristics v1.2
Representation of a solution instance.
Copyright 2018 Luis Velasco.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import copy, time, math
from Problem import Problem


# Assignment class stores the load of the highest loaded CPU
# when a task is assigned to a CPU.  
class Assignment(object):
    def __init__(self, serviceId, assignedId, cost):
        self.serviceId = serviceId
        self.assignedId = assignedId
        self.cost = cost

# Solution includes functions to manage the solution, to perform feasibility
# checks and to dump the solution into a string or file.
class Solution(Problem):

    @staticmethod
    def createEmptySolution(config, problem):
        solution = Solution(problem.inputData)
        solution.setVerbose(config.verbose)
        return(solution)

    def __init__(self, inputData):
        super(Solution, self).__init__(inputData)

        self.sb = {}
        self.sd = {}
        self.cost = 0.0

        self.feasible = True
        self.verbose = True

        self.used = [False] * self.inputData.nBuses
        self.WBM = [0] * self.inputData.nDrivers
        self.WEM = [0] * self.inputData.nDrivers
        
    def updateCost(self):
        newCost = 0.0
        for wMin in self.WBM:
            newCost += self.CBM * wMin
        for wMin in self.WEM:
            newCost += self.CEM * wMin

        for serviceId, busId in self.sb.iteritems():
            assignBus = self.buses[busId]
            service = self.services[serviceId]
            newCost += service.getDuration() * assignBus.getCost_min() + service.getKms() * assignBus.getCost_km()

        self.cost = newCost

    def getCost(self):
        return (self.cost)

    def getServices(self):
        return (self.services)

    def getDrivers(self):
        return (self.drivers)

    def getBuses(self):
        return (self.buses)
        
    def setVerbose(self, verbose):
        if(not isinstance(verbose, (bool)) or (verbose not in [True, False])):
            raise Exception('verbose(%s) has to be a boolean value.' % str(verbose))
        self.verbose = verbose
    
    def makeInfeasible(self):
        self.feasible = False
        self.cost = float('infinity')
    
    def isFeasible(self):
        return(self.feasible)

    def getDriverAssignedToService(self, serviceId):
        if(not self.sd.has_key(serviceId)): return(None)
        return(self.sd[serviceId])

    def getBusAssignedToService(self, busId):
        if(not self.sd.has_key(busId)): return(None)
        return(self.sd[busId])

    def isFeasibleToAssignDriverToService(self, serviceId, driverId):
        if(self.sd.has_key(serviceId)):
            if(self.verbose): print('Service(%s) already has a Driver assigned.' % str(serviceId))
            return(False)

        # check working minutes
        serviceDuration = self.inputData.duration[serviceId]
        WM = self.WBM[driverId] + self.WEM[driverId]
        remainingMinutes = self.inputData.maxWorkingTime[driverId] - (WM + serviceDuration)

        if remainingMinutes < 0:
            if(self.verbose): 
                print('Driver(%s, worked=%s) does not have enough available time for Service(%s, duration=%s)' % 
                (str(driverId), str(WM), str(serviceId), str(serviceDuration)))
            return(False)
    
        # check overlapping
        driverServices = [sId for sId, dId in self.sd.iteritems() if dId == driverId]

        for sId in driverServices:
            if self.overlapping[serviceId][sId]:
                if(self.verbose): 
                    print('Driver(%s) already operates Service(%s) which overlaps with Service(%s)' % 
                    (str(driverId), str(sId), str(serviceId)))
                return(False)

        return(True)

    def isFeasibleToAssignBusToService(self, serviceId, busId):
        if(self.sb.has_key(serviceId)):
            if(self.verbose): print('Service(%s) already has a Bus assigned.' % str(serviceId))
            return(False)

        # check max buses
        nUsedBuses = len(filter(lambda used: used == True, self.used))

        if nUsedBuses == self.maxBuses and not self.used[busId]:
            if(self.verbose): 
                print('Bus(%s) cannot be assigned to Service(%s): MAX number of buses already reached' % 
                (str(busId), str(serviceId)))
            return(False)

        # check capacity
        busCapacity = self.inputData.capacity[busId]
        passengers = self.inputData.passengers[serviceId]

        if busCapacity < passengers:
            if(self.verbose): 
                print('Bus(%s, capacity=%s) does not have enough capacity for Service(%s, passengers=%s)' % str(busId), str(busCapacity),  str(serviceId), str(passengers))
            return(False)

        # check overlapping
        busServices = [sId for sId, bId in self.sb.iteritems() if bId == busId]

        for sId in busServices:
            if self.overlapping[serviceId][sId]:
                if(self.verbose): 
                    print('Bus(%s) already operates Service(%s) which overlaps with Service(%s)' % 
                    (str(busId), str(sId), str(serviceId)))
                return(False)

        return(True)

    def assignDriver(self, serviceId, driverId):
        if(not self.isFeasibleToAssignDriverToService(serviceId, driverId)):
            if(self.verbose): print('Unable to assign Serivce(%s) to Driver(%s)' % (str(serviceId), str(driverId)))
            return(False)

        self.sd[serviceId] = driverId

        serviceDuration = self.inputData.duration[serviceId]
        remainingWBM = self.BM - self.WBM[driverId]

        WBM = min(remainingWBM, serviceDuration)
        WEM = serviceDuration - WBM

        self.WBM[driverId] += WBM
        self.WEM[driverId] += WEM

        self.updateCost()
            
        return(True)

    def assignBus(self, serviceId, busId):
        if(not self.isFeasibleToAssignBusToService(serviceId, busId)):
            if(self.verbose): print('Unable to assign Serivce(%s) to Bus(%s)' % (str(serviceId), str(busId)))
            return(False)

        self.sb[serviceId] = busId
        self.used[busId] = True

        self.updateCost()
        
        return(True)

    def isFeasibleToUnassignDriverFromService(self, serviceId, driverId):
        if(not self.sd.has_key(serviceId)):
            if(self.verbose): print('Unable to unassign Driver(%s) from Service(%s): Service(%s) has no driver assigned' % 
                str(driverId), str(serviceId), str(serviceId))
            return(False)
        
        if(self.sd[serviceId] != driverId):
            if(self.verbose): print('Unable to unassign Driver(%s) from Service(%s): Driver(%s) is not assigned to Service(%s)' % 
                str(driverId), str(serviceId), str(driverId), str(serviceId))
            return(False)

        return(True)

    def isFeasibleToUnassignBusFromService(self, serviceId, busId):
        if(not self.sb.has_key(serviceId)):
            if(self.verbose): print('Unable to unassign Bus(%s) from Service(%s): Service(%s) has no bus assigned' % 
                str(busId), str(serviceId), str(serviceId))
            return(False)
        
        if(self.sb[serviceId] != busId):
            if(self.verbose): print('Unable to unassign Bus(%s) from Service(%s): Bus(%s) is not assigned to Service(%s)' % 
                str(busId), str(serviceId), str(busId), str(serviceId))
            return(False)

        if(not self.used[busId]):
            if(self.verbose): print('Unable to unassign Bus(%s) from Service(%s): Bus(%s) is not used' % 
                str(busId), str(serviceId), str(busId))
            return(False)

        return(True)

    def unassignDriver(self, serviceId, driverId):
        if(not self.isFeasibleToUnassignDriverFromService(serviceId, driverId)):
            if(self.verbose): 
                print('Unable to unassign Driver(%s) from Service(%s)' % (str(driverId), str(serviceId)))
            return(False)

        if(self.verbose):
            print('Unassign Driver(%s) from Service(%s)' % driverId, serviceId)

        del self.sd[serviceId]

        serviceDuration = self.inputData.duration[serviceId]
        remainingWEM = self.WEM[driverId] - serviceDuration

        self.WEM[driverId] = max(0, remainingWEM)
        self.WBM[driverId] += min(0, remainingWEM)

        self.updateCost()
        return(True)

    def unassignBus(self, serviceId, busId):
        if(not self.isFeasibleToUnassignBusFromService(serviceId, busId)):
            if(self.verbose): 
                print('Unable to unassign Bus(%s) from Service(%s)' % (str(busId), str(serviceId)))
            return(False)

        if(self.verbose):
            print('Unassign Bus(%s) from Service(%s)' % busId, serviceId)

        del self.sb[serviceId]

        busServices = [sId for sId, bId in self.sb.iteritems() if bId == busId]
        if len(busServices) == 0:
            self.used[busId] = False

        self.updateCost()
        return(True)

    def findFeasibleDrivers(self, serviceId):
        startEvalTime = time.time()
        evaluatedCandidates = 0
        
        feasibleDrivers = []
        for driver in self.drivers:
            driverId = driver.getId()
            feasible = self.assignDriver(serviceId, driverId)

            evaluatedCandidates += 1
            if(not feasible): continue
            
            assignment = Assignment(serviceId, driverId, self.getCost())
            feasibleDrivers.append(assignment)
            
            self.unassignDriver(serviceId, driverId)
            
        elapsedEvalTime = time.time() - startEvalTime
        return(feasibleDrivers, elapsedEvalTime, evaluatedCandidates)

    def findFeasibleBuses(self, serviceId):
        startEvalTime = time.time()
        evaluatedCandidates = 0
        
        feasibleBuses = []
        for Bus in self.buses:
            busId = Bus.getId()
            feasible = self.assignBus(serviceId, busId)

            evaluatedCandidates += 1
            if(not feasible): continue
            
            assignment = Assignment(serviceId, busId, self.getCost())
            feasibleBuses.append(assignment)
            
            self.unassignBus(serviceId, busId)
            
        elapsedEvalTime = time.time() - startEvalTime
        return(feasibleBuses, elapsedEvalTime, evaluatedCandidates)

    # TODO refactor / remove (needed ?)
    def findBestFeasibleAssignment(self, taskId):
        bestAssignment = Assignment(taskId, None, float('infinity'))
        for cpu in self.cpus:
            cpuId = cpu.getId()
            feasible = self.assign(taskId, cpuId)
            if(not feasible): continue
            
            curHighestLoad = self.getHighestLoad()
            if(bestAssignment.highestLoad > curHighestLoad):
                bestAssignment.cpuId = cpuId
                bestAssignment.highestLoad = curHighestLoad
            
            self.unassign(taskId, cpuId)
            
        return(bestAssignment)
    
    def __str__(self):  # toString equivalent        
        strSolution = 'z = %10.8f;\n' % self.cost

        strSolution += '\n\n' + self.graphs() + '\n\n'
        
        strSolution += 'Used buses:\n'
        for busId in xrange(len(self.used)):
            if self.used[busId]:
                strSolution += 'Bus(' + str(busId) + ')    '

        strSolution += '\n\n'
        strSolution += 'Buses assignation\n'
        for serviceId, busId in self.sb.iteritems():
            strSolution += 'Service(' + str(serviceId) + ') <-> Bus(' + str(busId) + ')\n'
    
        strSolution += '\n\n'
        strSolution += 'Drivers assignation\n'
        for serviceId, driverId in self.sd.iteritems():
            strSolution += 'Service(' + str(serviceId) + ') <-> Driver(' + str(driverId) + ')\n'

        strSolution += '\n\n'
        strSolution += 'Drivers working hours\n'
        for driverId in xrange(self.inputData.nDrivers):
            strSolution += 'Driver(' + str(driverId) + ') -> WBM: ' + str(self.WBM[driverId]) + ', WEM: ' + str(self.WEM[driverId]) + '\n'
            
        return(strSolution)

    def graphs(self):
        graphs = ''
        graphs += 'Services:\n'

        for service in self.services:
            serviceId = service.getId()

            startHour = math.floor(self.inputData.start[serviceId] / 60)
            endHour = math.floor((self.inputData.start[serviceId] + self.inputData.duration[serviceId]) / 60)

            h = 0
            while h < 24:
                if (startHour <= h and h <= endHour):
                    graphs += self.num(serviceId) + ' '
                else:
                    graphs += '--' + ' '
                
                
                h += 1
            
            graphs += '\n'

        graphs += '\n\nDrivers:\n'

        for service in self.services:
            serviceId = service.getId()
            driverId = self.sd[serviceId]

            startHour = math.floor(self.inputData.start[serviceId] / 60)
            endHour = math.floor((self.inputData.start[serviceId] + self.inputData.duration[serviceId]) / 60)

            h = 0
            while h < 24:
                if (startHour <= h and h <= endHour):
                    graphs += self.num(driverId) + ' '
                else:
                    graphs += '--' + ' '
                h += 1                

            graphs += '\n'            

        graphs += '\n\nBuses:\n'            

        for service in self.services:
            serviceId = service.getId()
            busId = self.sb[serviceId]

            startHour = math.floor(self.inputData.start[serviceId] / 60)
            endHour = math.floor((self.inputData.start[serviceId] + self.inputData.duration[serviceId]) / 60)
            
            h = 0
            while h < 24:
                if (startHour <= h and h <= endHour):
                    graphs += self.num(busId) + ' '
                else:
                    graphs += '--' + ' '
                h += 1                

            graphs += '\n'

        return(graphs)            

    def num(self, num):
        if num is None:
            return ('  ')

        if num < 10:
            return (' ' + str(num))
        
        return (str(num))

    def saveToFile(self, filePath):
        f = open(filePath, 'w')
        f.write(self.__str__())
        f.close()
