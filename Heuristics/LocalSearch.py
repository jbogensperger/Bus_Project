'''
AMMM Lab Heuristics v1.2
Local Search algorithm.
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

# A change in a solution in the form: move taskId from curCPUId to newCPUId.
# This class is used to carry sets of modifications.
# A new solution can be created based on an existing solution and a list of
# changes can be created using the createNeighborSolution(solution, changes) function.
class Change(object):
    def __init__(self, serviceId, curAssignedId, newAssignedId):
        self.serviceId = serviceId
        self.curAssignedId = curAssignedId
        self.newAssignedId = newAssignedId

# Implementation of a local search using two neighborhoods and two different policies.
class LocalSearch(object):
    def __init__(self, config):
        self.enabled = config.localSearch
        self.nhStrategy = config.neighborhoodStrategy
        self.policy = config.policy
        
        self.elapsedTime = 0
        self.iterations = 0

    def createNeighborSolution_drivers(self, solution, changes):        
        newSolution = copy.deepcopy(solution)
        
        for change in changes:
            newSolution.unassignDriver(change.serviceId, change.curAssignedId)
        
        for change in changes:
            feasible = newSolution.assignDriver(change.serviceId, change.newAssignedId)
            if(not feasible): return(None)
        
        return(newSolution)

    def createNeighborSolution_buses(self, solution, changes):
        newSolution = copy.deepcopy(solution)
        
        for change in changes:
            newSolution.unassignBus(change.serviceId, change.curAssignedId)
        
        for change in changes:
            feasible = newSolution.assignBus(change.serviceId, change.newAssignedId)
            if(not feasible): return(None)
        
        return(newSolution)

    def evaluateNeighbor_drivers(self, solution, changes):
        newSolution = copy.deepcopy(solution)
        
        for change in changes:
            newSolution.unassignDriver(change.serviceId, change.curAssignedId)
        
        for change in changes:
            feasible = newSolution.assignDriver(change.serviceId, change.newAssignedId)
            if(not feasible): return(float('infinity'))
        
        return(newSolution.getCost())

    def evaluateNeighbor_buses(self, solution, changes):
        newSolution = copy.deepcopy(solution)
        
        for change in changes:
            newSolution.unassignBus(change.serviceId, change.curAssignedId)
        
        for change in changes:
            feasible = newSolution.assignBus(change.serviceId, change.newAssignedId)
            if(not feasible): return(float('infinity'))
        
        return(newSolution.getCost())

    def getBusAssignmentsSortedByBusCost(self, solution):
        services = solution.getServices()
        buses = solution.getBuses()

        # create vector of service assignments.
        # Each element is a tuple <service, bus> 
        assignments = []
        for service in services:
            serviceId = service.getId()
            busId = solution.getBusAssignedToService(serviceId)
            bus = buses[busId]

            busCost = bus.getCost_km() + bus.getCost_min()
            assignment = (service, bus, busCost)
            assignments.append(assignment)

        # For best improvement policy it does not make sense to sort the services since all of them must be explored.
        # However, for first improvement, we can start by the services assigned to the more currently expensive drivers.
        if(self.policy == 'BestImprovement'): return(assignments)
        
        # Sort services assignments by the current price of the assigned driver in descending order.
        sorted_assignments = sorted(assignments, key=lambda assignment:assignment[2], reverse=True)
        return(sorted_assignments)

    def getDriverAssignmentsSortedByDriverCost(self, solution):
        services = solution.getServices()
        drivers = solution.getDrivers()

        # create vector of service assignments.
        # Each element is a tuple <service, driver> 
        assignments = []
        for service in services:
            serviceId = service.getId()
            driverId = solution.getDriverAssignedToService(serviceId)
            driver = drivers[driverId]

            driverCost = solution.WBM[driverId] * solution.CBM + solution.WEM[driverId] * solution.CEM
            assignment = (service, driver, driverCost)
            assignments.append(assignment)

        # For best improvement policy it does not make sense to sort the services since all of them must be explored.
        # However, for first improvement, we can start by the services assigned to the more currently expensive drivers.
        if(self.policy == 'BestImprovement'): return(assignments)
        
        # Sort services assignments by the current price of the assigned driver in descending order.
        sorted_assignments = sorted(assignments, key=lambda assignment:assignment[2], reverse=True)
        return(sorted_assignments)
    
    def exploreNeighborhood_drivers(self, solution):        
        curCost = solution.getCost()
        bestNeighbor = solution
        
        if(self.nhStrategy == 'Reassignment'):
            drivers = solution.getDrivers()
            driverSortedAssignments = self.getDriverAssignmentsSortedByDriverCost(solution)

            for assignment in driverSortedAssignments:
                service = assignment[0]
                serviceId = service.getId()
                
                curDriver = assignment[1]
                curDriverId = curDriver.getId()
                
                for driver in drivers:
                    newDriverId = driver.getId()
                    if(newDriverId == curDriverId): continue
                    
                    changes = []
                    changes.append(Change(serviceId, curDriverId, newDriverId))
                    neighborCost = self.evaluateNeighbor_drivers(solution, changes)
                    if(curCost > neighborCost):
                        neighbor = self.createNeighborSolution_drivers(solution, changes)
                        if(neighbor is None): continue
                        if(self.policy == 'FirstImprovement'):
                            return(neighbor)
                        else:
                            bestNeighbor = neighbor
                            curCost = neighborCost
                            
        elif(self.nhStrategy == 'Exchange'):
            # For the Exchange neighborhood and first improvement policy, try exchanging
            # tasks two tasks, one from highly loaded CPU and the other from lowly loaded
            # CPU. It can be done by picking task1 from begin to end of sortedAssignments,
            # and task2 from end to begin.
            
            sortedAssignments = self.getDriverAssignmentsSortedByDriverCost(solution)
            numAssignments = len(sortedAssignments)
            
            for i in xrange(0, numAssignments):             # i = 0..(numAssignments-1)
                assignment1 = sortedAssignments[i]
                
                service1 = assignment1[0]
                serivceId1 = service1.getId()
                
                curDriver1 = assignment1[1]
                curDriverId1 = curDriver1.getId()
                
                for j in xrange(numAssignments-1, -1, -1):  # j = (numAssignments-1)..0
                    if(i >= j): continue # avoid duplicate explorations and exchange with itself. 
                    
                    assignment2 = sortedAssignments[j]
                    
                    service2 = assignment2[0]
                    serviceId2 = service2.getId()
                    
                    curDriver2 = assignment2[1]
                    curDriverId2 = curDriver2.getId()

                    # avoid exploring pairs of tasks assigned to the same CPU
                    if(curDriverId1 == curDriverId2): continue
                    
                    changes = []
                    changes.append(Change(serivceId1, curDriverId1, curDriverId2))
                    changes.append(Change(serviceId2, curDriverId2, curDriverId1))
                    neighborCost = self.evaluateNeighbor_drivers(solution, changes)
                    if(curCost > neighborCost):
                        neighbor = self.createNeighborSolution_drivers(solution, changes)
                        if(neighbor is None): continue
                        if(self.policy == 'FirstImprovement'):
                            return(neighbor)
                        else:
                            bestNeighbor = neighbor
                            curCost = neighborCost
            
        else:
            raise Exception('Unsupported NeighborhoodStrategy(%s)' % self.nhStrategy)
        
        return(bestNeighbor)
    
    def exploreNeighborhood_buses(self, solution):        
        curCost = solution.getCost()
        bestNeighbor = solution
        
        if(self.nhStrategy == 'Reassignment'):
            buses = solution.getBuses()
            busSortedAssignments = self.getBusAssignmentsSortedByBusCost(solution)

            for assignment in busSortedAssignments:
                service = assignment[0]
                serviceId = service.getId()
                
                curBus = assignment[1]
                curBusId = curBus.getId()
                
                for bus in buses:
                    newBusId = bus.getId()
                    if(newBusId == curBusId): continue
                    
                    changes = []
                    changes.append(Change(serviceId, curBusId, newBusId))
                    neighborCost = self.evaluateNeighbor_buses(solution, changes)
                    if(curCost > neighborCost):
                        neighbor = self.createNeighborSolution_buses(solution, changes)
                        if(neighbor is None): continue
                        if(self.policy == 'FirstImprovement'):
                            return(neighbor)
                        else:
                            bestNeighbor = neighbor
                            curCost = neighborCost
                            
        elif(self.nhStrategy == 'Exchange'):
            # For the Exchange neighborhood and first improvement policy, try exchanging
            # tasks two tasks, one from highly loaded CPU and the other from lowly loaded
            # CPU. It can be done by picking task1 from begin to end of sortedAssignments,
            # and task2 from end to begin.
            
            sortedAssignments = self.getDriverAssignmentsSortedByDriverCost(solution)
            numAssignments = len(sortedAssignments)
            
            for i in xrange(0, numAssignments):             # i = 0..(numAssignments-1)
                assignment1 = sortedAssignments[i]
                
                service1 = assignment1[0]
                serivceId1 = service1.getId()
                
                curBus1 = assignment1[1]
                curBusId1 = curBus1.getId()
                
                for j in xrange(numAssignments-1, -1, -1):  # j = (numAssignments-1)..0
                    if(i >= j): continue # avoid duplicate explorations and exchange with itself. 
                    
                    assignment2 = sortedAssignments[j]
                    
                    service2 = assignment2[0]
                    serviceId2 = service2.getId()
                    
                    curBus2 = assignment2[1]
                    curBusId2 = curBus2.getId()

                    # avoid exploring pairs of tasks assigned to the same CPU
                    if(curBusId1 == curBusId2): continue
                    
                    changes = []
                    changes.append(Change(serivceId1, curBusId1, curBusId2))
                    changes.append(Change(serviceId2, curBusId2, curBusId1))
                    neighborCost = self.evaluateNeighbor_buses(solution, changes)
                    if(curCost > neighborCost):
                        neighbor = self.createNeighborSolution_buses(solution, changes)
                        if(neighbor is None): continue
                        if(self.policy == 'FirstImprovement'):
                            return(neighbor)
                        else:
                            bestNeighbor = neighbor
                            curCost = neighborCost
            
        else:
            raise Exception('Unsupported NeighborhoodStrategy(%s)' % self.nhStrategy)
        
        return(bestNeighbor)

    def run(self, solution):
        if(not self.enabled): return(solution)
        if(not solution.isFeasible()): return(solution)

        bestSolution = solution
        bestCost = bestSolution.getCost()
        
        startEvalTime = time.time()
        iterations = 0
        
        # keep iterating while improvements are found
        keepIterating = True
        while(keepIterating):
            keepIterating = False
            iterations += 1
            
            neighbor_driver = self.exploreNeighborhood_drivers(bestSolution)
            neighbor_bus = self.exploreNeighborhood_buses(bestSolution)

            if (neighbor_driver.getCost() < neighbor_bus.getCost()):
                neighbor = neighbor_driver
            else:
                neighbor = neighbor_bus

            curBestCost = neighbor.getCost()
            if(bestCost > curBestCost):
                bestSolution = neighbor
                bestCost = curBestCost
                keepIterating = True
        
        self.iterations += iterations
        self.elapsedTime += time.time() - startEvalTime
        
        return(bestSolution)
    
    def printPerformance(self):
        if(not self.enabled): return
        
        avg_evalTimePerIteration = 0.0
        if(self.iterations != 0):
            avg_evalTimePerIteration = 1000.0 * self.elapsedTime / float(self.iterations)
        
        print ''
        print 'Local Search Performance:'
        print '  Num. Iterations Eval.', self.iterations
        print '  Total Eval. Time     ', self.elapsedTime, 's'
        print '  Avg. Time / Iteration', avg_evalTimePerIteration, 'ms'
