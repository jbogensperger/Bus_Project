'''
AMMM Lab Heuristics v1.2
Representation of a problem instance.
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

from Task import Task
from CPU import CPU

from Bus import Bus
from Driver import Driver
from Service import Service


class Problem(object):
    def __init__(self, inputData):
        self.inputData = inputData

        nBuses = self.inputData.nBuses;
        nDrivers = self.inputData.nDrivers;
        nServices = self.inputData.nServices;

        start = self.inputData.start
        duration = self.inputData.duration
        kms = self.inputData.kms
        passengers = self.inputData.passengers

        capacity = self.inputData.capacity
        cost_km = self.inputData.cost_km
        cost_min = self.inputData.cost_min

        maxWorkingTime = self.inputData.maxWorkingTime

        self.maxBuses = self.inputData.maxBuses
        self.BM = self.inputData.BM
        self.CBM = self.inputData.CBM
        self.CEM = self.inputData.CEM

        self.drivers = []
        self.buses = []
        self.services = []
        self.overlapping = [[0 for x in range(nServices)] for y in range(nServices)] 

        for sId in xrange(0, nServices): #hopefully really 0..(nServices-1) --> Check that
            service = Service(sId, start[sId], duration[sId], kms[sId], passengers[sId])
            self.services.append(service)

        for dId in xrange(0, nDrivers): 
            driver = Driver(dId, maxWorkingTime[dId])
            self.drivers.append(driver)

        for bId in xrange(0, nBuses):
            bus = Bus(bId, capacity[bId], cost_km[bId], cost_min[bId])
            self.buses.append(bus)

        for s1 in xrange(0, nServices):
            for s2 in xrange(0, nServices):
                if self.services[s1].getStart() < (self.services[s2].getStart() + self.services[s1].getDuration()) and (self.services[s1].getStart() + self.services[s1].getDuration()) > self.services[s2].getStart():
                    self.overlapping[s1][s2] = 1
                else:
                    self.overlapping[s1][s2] = 0

        
        ######### OLD STuff #########
        nTasks = self.inputData.nTasks
        nThreads = self.inputData.nThreads
        nCPUs = self.inputData.nCPUs
        nCores = self.inputData.nCores
        rh = self.inputData.rh
        rc = self.inputData.rc
        CK = self.inputData.CK
        TH = self.inputData.TH

        self.tasks = []                             # vector with tasks
        for tId in xrange(0, nTasks):               # tId = 0..(nTasks-1)
            task = Task(tId)
            for hId in xrange(0, nThreads):         # hId = 0..(nThreads-1)
                # if thread hId belongs to task tId
                if(TH[tId][hId]):
                    # add thread hId requiring res resources to task tId
                    resources = rh[hId]
                    task.addThreadAndResources(hId, resources)
            self.tasks.append(task)

        self.cpus = []                              # vector with cpus
        self.maxCapacityPerCPUId = [0] * nCPUs      # vector with max capacity of each CPU. initialized to nCPUs zeros [ 0 ... 0 ]
        self.maxCapacityPerCoreId = [0] * nCores    # vector with max capacity of each core. initialized to nCores zeros [ 0 ... 0 ]
        for cId in xrange(0, nCPUs):                # cId = 0..(nCPUs-1)
            cpu = CPU(cId)
            for kId in xrange(0, nCores):           # kId = 0..(nCores-1)
                # if core kId belongs to CPU cId
                if(CK[cId][kId]):
                    # add core kId with capacity to CPU cId
                    capacity = rc[cId]
                    cpu.addCoreAndCapacity(kId, capacity)
                    self.maxCapacityPerCPUId[cId] += capacity
                    self.maxCapacityPerCoreId[kId] = capacity
            self.cpus.append(cpu)


    ######### NEW STuff #########
    def getDrivers(self):
        return(self.drivers)
    def getBuses(self):
        return(self.buses)
    def getServices(self):
        return(self.services)
    def getMaxBuses(self):
        return(self.maxBuses)
    def getBM(self):
        return(self.BM)
    def getCBM(self):
        return(self.CBM)
    def getCEM(self):
        return(self.CEM)




    ######### DELETE BELOW #########
    def getTasks(self):
        return(self.tasks)

    def getCPUs(self):
        return(self.cpus)


    ######### Check the instance if feasible --> return true (We don't need to implement that, our problems will be solveable) ###
    def checkInstance(self):
        return(True)
