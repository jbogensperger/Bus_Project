'''
AMMM Instance Generator v1.0
Instance Generator class.
Copyright 2016 Luis Velasco and Lluis Gifre.

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

import os, random

# Generate instances based on read configuration. 
class InstanceGenerator(object):
    def __init__(self, config):
        self.config = config
    
    def generate(self):
        instancesDirectory = self.config.instancesDirectory
        fileNamePrefix = self.config.fileNamePrefix
        fileNameExtension = self.config.fileNameExtension
        numInstances = self.config.numInstances
        
        nDrivers = self.config.nDrivers

        nBuses = self.config.nBuses
        minCapacity = self.config.minCapacity
        maxCapacity = self.config.maxCapacity

        nServices = self.config.nServices
        minDuration = self.config.minDuration
        maxDuration = self.config.maxDuration
        minPassengers = self.config.minPassengers
        maxPassengers = self.config.maxPassengers

        if(not os.path.isdir(instancesDirectory)):
            raise Exception('Directory(%s) does not exist' % instancesDirectory)

        for i in xrange(0, numInstances):
            instancePath = os.path.join(instancesDirectory, '%s_%d.%s' % (fileNamePrefix, i, fileNameExtension))
            fInstance = open(instancePath, 'w')

            durations = [];
            starts = [];
            kms = [];
            passengers = [];
            for service in xrange(0, nServices):
                start = random.randint(0, 24 * 60) # one day services
                starts.append(start)

                duration = random.randint(minDuration, maxDuration)
                durations.append(duration)

                km = random.randint(duration, duration * 2) # 60km/h <-> 120km/h
                kms.append(km)

                passenger = random.randint(minPassengers, maxPassengers)
                passengers.append(passenger)
            
            capacities = []
            cost_kms = []
            cost_mins = []
            for bus in xrange(0, nBuses):
                capacity = random.randint(minCapacity, maxCapacity)
                capacities.append(capacity)

                cost_km = random.uniform(0.01, 0.2)
                cost_kms.append(cost_km)

                cost_min = random.uniform(0.01, 0.2)
                cost_mins.append(cost_min)

            maxWorkingTimes = []
            for driver in xrange(0, nDrivers):
                maxWorkingTime = nServices * random.randint(((minDuration + maxDuration) / 2), round(maxDuration * 1.5)) / nDrivers  # sensible to make instance unresolvable!!!!!! CHANGE JOHANNES!!!!!!! Added 25% to maxDuration
                maxWorkingTimes.append(maxWorkingTime) 

            maxBuses = nServices * random.randint(((minDuration + maxDuration) / 2), maxDuration) / 24 # sensible to make instance unresolvable

            BM = 200
            CBM = 0.2
            CEM = 0.3

            fInstance.write('nDrivers = %d;\n' % nDrivers)
            fInstance.write('nBuses = %d;\n' % nBuses)
            fInstance.write('nServices = %d;\n\n' % nServices)

            fInstance.write('start = [%s];\n' % (' '.join(map(str, starts))))
            fInstance.write('duration = [%s];\n' % (' '.join(map(str, durations))))
            fInstance.write('kms = [%s];\n' % (' '.join(map(str, kms))))
            fInstance.write('passengers = [%s];\n\n' % (' '.join(map(str, passengers))))

            fInstance.write('capacity = [%s];\n' % (' '.join(map(str, capacities))))
            fInstance.write('cost_km = [%s];\n' % (' '.join(map(str, cost_kms))))
            fInstance.write('cost_min = [%s];\n\n' % (' '.join(map(str, cost_mins))))

            fInstance.write('maxWorkingTime = [%s];\n' % (' '.join(map(str, maxWorkingTimes))))
            fInstance.write('maxBuses = %d;\n\n' % maxBuses)

            fInstance.write('BM = %s;\n' % str(BM))
            fInstance.write('CBM = %s;\n' % str(CBM))
            fInstance.write('CEM = %s;\n' % str(CEM))

            fInstance.close()
