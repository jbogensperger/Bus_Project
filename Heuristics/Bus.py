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

class Bus(object):
    def __init__(self, busId, capacity, cost_km, cost_min):
        self._busId = busId
        self._capacity = capacity
        self._cost_km = cost_km
        self._cost_min = cost_min

    def getId(self):
        return(self._busId)
    
    def getCapacity(self):
        return(self._capacity)

    def getCost_km(self):
        return(self._cost_km)

    def getCost_min(self):
        return(self._cost_min)
    
