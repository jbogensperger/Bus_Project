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

class Driver(object):
    def __init__(self, driverId, maxWorkingTime):
        self._driverId = driverId
        self._maxWorkingTime = maxWorkingTime
    
    
    def getId(self):
        return(self._driverId)
    
    def getMaxWorkingTime(self):
        return(self._maxWorkingTime)    

    
