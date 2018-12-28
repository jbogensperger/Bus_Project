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

import copy, time
from Problem import Problem


# Assignment class stores the load of the highest loaded CPU
# when a task is assigned to a CPU.  
class Assignment(object):
    def __init__(self, serviceId, assignedId, cost):
        self.serviceId = serviceId
        self.id = assignedId
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

        self.used = []
        self.WBM = [0] * self.inputData.nDrivers
        self.WEM = [0] * self.inputData.nDrivers
        
    def updateCost(self):
        newCost = 0.0
        for wMin in self.WBM:
            newCost += self.CBM * wMin
        for wMin in self.WEM:
            newCost += self.CEM * wMin
        for service in self.services:
            assignBus = self.sb[service.getId]
            newCost += service.getDuration() * assignBus.getCost_min() + service.getKms() * assignBus.getCost_km() 
        self.cost = newCost


    def getCost(self):
        self.updateCost()
        return (self.cost)
        
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
        remainingMinutes = self.inputData.maxWorkingTime - (WM + serviceDuration)

        if remainingMinutes <= 0:
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
        nUsedBuses = len(filter(lambda used: used == 1, self.used))

        if nUsedBuses == self.maxBuses and self.used[busId] == 0:
            if(self.verbose): 
                print('Bus(%s) cannot be assigned to Service(%s): MAX number of buses already reached' % 
                (str(busId), str(serviceId)))
            return(False)

        # check capacity
        busCapacity = self.inputData.capacity[busId]
        passengers = self.inputData.passengers[serviceId]

        if busCapacity < passengers:
            if(self.verbose): 
                print('Bus(%s, capacity=%s) does not have enough capacity for Service(%s, passengers=%s)' % 
                (str(busId), str(busCapacity),  str(serviceId), str(passengers))
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
        self.used[busId] = 1

        self.updateCost()
        
        return(True)

    def isFeasibleToUnassignDriverFromService(self, serviceId, driverId):
        # TODO implement
        return(True)

    def isFeasibleToUnassignBusFromService(self, serviceId, busId):
        # TODO implement
        return(True)

    # TODO remove
    def isFeasibleToUnassignTaskFromCPU(self, taskId, cpuId):
        if(not self.taskIdToCPUId.has_key(taskId)):
            if(self.verbose): print('Task(%s) is not assigned to any CPU.' % str(taskId))
            return(False)
        
        if(not self.cpuIdToListTaskId.has_key(cpuId)):
            if(self.verbose): print('CPU(%s) is not used by any Task.' % str(cpuId))
            return(False)

        if(taskId not in self.cpuIdToListTaskId[cpuId]):
            if(self.verbose): print('CPU(%s) is not used by Task(%s).' % (str(cpuId), str(taskId)))
            return(False)

        return(True)

    # TODO remove
    def isFeasibleToUnassignThreadFromCore(self, taskId, threadId, cpuId, coreId):
        if(not self.threadIdToCoreId.has_key(threadId)):
            if(self.verbose): print('Thread(%s) does not has a Core assigned.' % str(threadId))
            return(False)
        
        task = self.tasks[taskId]
        resources = task.getResourcesByThread(threadId)
        availCapacity = self.availCapacityPerCoreId[coreId]
        maxCapacity = self.maxCapacityPerCoreId[coreId]
        if((availCapacity + resources) > maxCapacity):
            if(self.verbose): print('Core(%s) will exceed its maximum capacity after releasing Thread(%s)' % (str(coreId), str(threadId)))
            return(False)
        
        return(True)

    def unassignDriver(self, serviceId, driverId):
        # TODO implement
        return(True)

    def unassignBus(self, serviceId, busId):
        # TODO implement
        return(True)

    # TODO remove
    def unassign(self, taskId, cpuId):
        if(not self.isFeasibleToUnassignTaskFromCPU(taskId, cpuId)):
            if(self.verbose): print('Unable to unassign Task(%s) from CPU(%s)' % (str(taskId), str(cpuId)))
            return(False)
        
        task = self.tasks[taskId]
        taskThreadIds = task.getThreadIds()
        
        cpu = self.cpus[cpuId]

        assignment = {}     # hash table threadId => coreId assigned
        
        # recover the assignment of threads to cores
        # check that cores belong to specified CPU
        for threadId in taskThreadIds:
            coreId = self.threadIdToCoreId[threadId]
            if(not cpu.hasCore(coreId)):
                raise Exception('CoreId(%d) does not belong to CPUId(%d)' % (coreId, cpu.getCPUId()))
            
            if(self.isFeasibleToUnassignThreadFromCore(taskId, threadId, cpuId, coreId)):
                assignment[threadId] = coreId 
            else:
                if(self.verbose):
                    print('Unable to unassign Thread(%s) belonging to Task(%s) to Core(%s) belonging to CPU(%s)' % (
                        str(threadId), str(taskId), str(coreId), str(cpuId)))
        
        if(self.verbose):
            print 'Solution', 'unassign', 'assignment', assignment
            print 'Solution', 'unassign', 'taskThreadIds', taskThreadIds
        
        # if there is some thread not assigned to a core: not feasible 
        if(len(assignment) != len(taskThreadIds)):
            return(False)
        
        # otherwise: deallocate the resources
        if(self.verbose): print('Unassign Task(%s) to CPU(%s)' % (str(taskId), str(cpuId)))
        del self.taskIdToCPUId[taskId]
        self.cpuIdToListTaskId[cpuId].remove(taskId)
        
        for threadId,coreId in assignment.iteritems():  # iterate over the hash table.
                                                        # each entry is a pair (key<coreId> => value<threadId>)
            if(self.verbose):
                print('\tUnassign Thread(%s) belonging to Task(%s) to Core(%s) belonging to CPU(%s)' % (
                        str(threadId), str(taskId), str(coreId), str(cpuId)))
            
            del self.threadIdToCoreId[threadId]
            self.coreIdToListThreadId[coreId].remove(threadId)
            resources = task.getResourcesByThread(threadId)
            self.availCapacityPerCoreId[coreId] += resources
            self.availCapacityPerCPUId[cpuId] += resources

        self.updateHighestLoad()
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
    
    # TODO refactor
    def __str__(self):  # toString equivalent
        nTasks = self.inputData.nTasks
        nThreads = self.inputData.nThreads
        nCPUs = self.inputData.nCPUs
        nCores = self.inputData.nCores
        
        strSolution = 'z = %10.8f;\n' % self.highestLoad
        
        # Xhk: decision variable containing the assignment of threads to cores
        # pre-fill with no assignments (all-zeros)
        xhk = []
        for h in xrange(0, nThreads):   # h = 0..(nThreads-1)
            xhkEntry = [0] * nCores     # results in a vector of 0's with nCores elements
            xhk.append(xhkEntry)

        # iterate over hash table threadIdToCoreId and fill in xhk
        for threadId,coreId in self.threadIdToCoreId.iteritems():
            xhk[threadId][coreId] = 1

        strSolution += 'xhk = [\n'
        for xhkEntry in xhk:
            strSolution += '\t[ '
            for xhkValue in xhkEntry:
                strSolution += str(xhkValue) + ' '
            strSolution += ']\n'
        strSolution += '];\n'
        
        # Xtc: decision variable containing the assignment of tasks to CPUs
        # pre-fill with no assignments (all-zeros)
        xtc = []
        for t in xrange(0, nTasks):     # t = 0..(nTasks-1)
            xtcEntry = [0] * nCPUs      # results in a vector of 0's with nCPUs elements
            xtc.append(xtcEntry)
        
        # iterate over hash table taskIdToCPUId and fill in xtc
        for taskId,cpuId in self.taskIdToCPUId.iteritems():
            xtc[taskId][cpuId] = 1
        
        strSolution += 'xtc = [\n'
        for xtcEntry in xtc:
            strSolution += '\t[ '
            for xtcValue in xtcEntry:
                strSolution += str(xtcValue) + ' '
            strSolution += ']\n'
        strSolution += '];\n'
        
        return(strSolution)

    def saveToFile(self, filePath):
        f = open(filePath, 'w')
        f.write(self.__str__())
        f.close()
