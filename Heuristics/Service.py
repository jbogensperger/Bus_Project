'''
AMMM Lab Heuristics v1.2
Representation of a Task.
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

class Service(object):
    def __init__(self, serviceId, start, duration, kms, passengers):
        self._serviceId = serviceId
        self._start = start
        self._duration = duration
        self._kms = kms
        self._passengers = passengers

    
    def getId(self):
        return(self._serviceId)
    def getStart(self):
        return(self._start)
    def getDuration(self):
        return(self._duration)
    def getKms(self):
        return(self._kms)
    def getPassengers(self):
        return(self._passengers)