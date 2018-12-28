'''
AMMM Lab Heuristics v1.2
GRASP solver.
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

import random, time
from Solver import Solver
from Solution import Solution
from LocalSearch import LocalSearch

# Inherits from a parent abstract solver.
class Solver_GRASP(Solver):
    def selectCandidate(self, config, candidateList):
        if(len(candidateList) == 0): return(None)
        
        # sort candidate assignments by highestLoad in ascending order
        sortedCL = sorted(candidateList, key=lambda candidate: candidate.cost, reverse=False)
        
        # compute boundary highest load as a function of the minimum and maximum highest loads and the alpha parameter
        alpha = config.alpha
        minCost = sortedCL[0].cost
        maxCost = sortedCL[len(sortedCL)-1].cost
        boundaryCost = minCost + (maxCost - minCost) * alpha
        
        # find elements that fall into the RCL (those fulfilling: cost < boundaryCost)
        maxIndex = 0
        for x in sortedCL:
            if(x.cost > boundaryCost): break
            maxIndex += 1

        # create RCL and pick an element randomly
        rcl = sortedCL[0:maxIndex]          # pick first maxIndex elements starting from element 0
        if(len(rcl) == 0): return(None)
        return(random.choice(rcl))          # pick an element from rcl at random
    
    def greedyRandomizedConstruction(self, config, problem):
        # get an empty solution for the problem
        solution = Solution.createEmptySolution(config, problem)
        
        # get tasks and sort them by their total required resources in descending order
        services = problem.getServices()
        sortedServices = services #sorted(services, key=lambda service: service.getTotalResources(), reverse=True)

        iteration_elapsedEvalTime = 0
        iteration_evaluatedCandidates = 0
        
        # for each task taken in sorted order
        for service in sortedServices:
            serviceId = service.getId()

            # find assignments could be done in one function returning both drivers and buses lists
            
            # compute feasible drivers
            candidateDriversList, elapsedEvalTime, evaluatedCandidates = solution.findFeasibleDrivers(serviceId)
            iteration_elapsedEvalTime += elapsedEvalTime
            iteration_evaluatedCandidates += evaluatedCandidates

            # compute feasible buses
            candidateBusesList, elapsedEvalTime, evaluatedCandidates = solution.findFeasibleBuses(serviceId)
            iteration_elapsedEvalTime += elapsedEvalTime
            iteration_evaluatedCandidates += evaluatedCandidates
            
            # no candidate assignments => no feasible assignment found
            if(len(candidateDriversList) == 0 or len(candidateBusesList) == 0):
                solution.makeInfeasible()
                break
            
            # select an assignment
            candidateDriver = self.selectCandidate(config, candidateDriversList)
            candidateBus = self.selectCandidate(config, candidateBusesList)
            if((candidateDriver is None) or (candidateBus is None)): break

            # assign the current task to the CPU that resulted in a minimum highest load
            solution.assignDriver(serviceId, candidateDriver.assignedId)
            solution.assignBus(serviceId, candidateBus.assignedId)
            
        return(solution, iteration_elapsedEvalTime, iteration_evaluatedCandidates)

    #######  New solver   ################
    def solve(self, config, problem):
        bestSolution = Solution.createEmptySolution(config, problem)
        bestSolution.makeInfeasible() 

        bestCost = bestSolution.getCost()

        self.startTimeMeasure()
        self.writeLogLine(bestCost, 0)
        
        total_elapsedEvalTime = 0
        total_evaluatedCandidates = 0
        
        #localSearch = LocalSearch(config) ## TODO ADD LOCALSEARCH HERE..

        iteration = 0
        while(time.time() - self.startTime < config.maxExecTime):
            iteration += 1

            # force first iteration as a Greedy execution (alpha == 0)
            originalAlpha = config.alpha 
            if(iteration == 1): config.alpha = 0
            
            solution, it_elapsedEvalTime, it_evaluatedCandidates = self.greedyRandomizedConstruction(config, problem)
            total_elapsedEvalTime += it_elapsedEvalTime
            total_evaluatedCandidates += it_evaluatedCandidates
            
            # recover original alpha
            if(iteration == 1): config.alpha = originalAlpha
            
            if(not solution.isFeasible()): continue
            
            solution = localSearch.run(solution)
            
            solutionCost = solution.getCost()
            if(solutionCost < bestCost):
                bestSolution = solution
                bestCost = solutionCost
                self.writeLogLine(bestCost, iteration)
            
        self.writeLogLine(bestCost, iteration)
        
        avg_evalTimePerCandidate = 0.0
        if(total_evaluatedCandidates != 0):
            avg_evalTimePerCandidate = 1000.0 * total_elapsedEvalTime / float(total_evaluatedCandidates)
        
        print ''
        print 'GRASP Candidate Evaluation Performance:'
        print '  Num. Candidates Eval.', total_evaluatedCandidates
        print '  Total Eval. Time     ', total_elapsedEvalTime, 's'
        print '  Avg. Time / Candidate', avg_evalTimePerCandidate, 'ms'
        
        localSearch.printPerformance()
        
        return(bestSolution)



