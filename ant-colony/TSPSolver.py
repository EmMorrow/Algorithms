#!/usr/bin/python3

from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time
import numpy as np
from TSPClasses import *
import heapq
import itertools
from branchBound import BBSolver
from ACSolver import *


class TSPSolver:
    def __init__(self, gui_view):
        self._scenario = None

    def setupWithScenario(self, scenario):
        self._scenario = scenario

    ''' <summary>
        This is the entry point for the default solver
        which just finds a valid random tour.  Note this could be used to find your
        initial BSSF.
        </summary>
        <returns>results dictionary for GUI that contains three ints: cost of solution, 
        time spent to find solution, number of permutations tried during search, the 
        solution found, and three null values for fields not used for this 
        algorithm</returns> 
    '''

    def defaultRandomTour(self, time_allowance=60.0):
        results = {}
        cities = self._scenario.getCities()
        ncities = len(cities)
        foundTour = False
        count = 0
        bssf = None
        start_time = time.time()
        while not foundTour and time.time() - start_time < time_allowance:
            # create a random permutation
            perm = np.random.permutation(ncities)
            route = []
            # Now build the route using the random permutation
            for i in range(ncities):
                route.append(cities[perm[i]])
            bssf = TSPSolution(route)
            count += 1
            if bssf.cost < np.inf:
                # Found a valid route
                foundTour = True
        end_time = time.time()
        results['cost'] = bssf.cost if foundTour else math.inf
        results['time'] = end_time - start_time
        results['count'] = count
        results['soln'] = bssf
        results['max'] = None
        results['total'] = None
        results['pruned'] = None
        return results

    ''' <summary>
        This is the entry point for the greedy solver, which you must implement for 
        the group project (but it is probably a good idea to just do it for the branch-and
        bound project as a way to get your feet wet).  Note this could be used to find your
        initial BSSF.
        </summary>
        <returns>results dictionary for GUI that contains three ints: cost of best solution, 
        time spent to find best solution, total number of solutions found, the best
        solution found, and three null values for fields not used for this 
        algorithm</returns> 
    '''

    def greedy(self, time_allowance=60.0):
        results = {}
        cities = self._scenario.getCities()
        ncities = len(cities)
        bssf = TSPSolution(cities)
        bssf.cost = math.inf
        start_time = time.time()
        for city in cities:  # All the cities
            current_city = city
            path = []
            path.append(city)
            while len(path) < ncities:
                bcsf = math.inf  # Best cost so far
                best_city = None
                has_child = False
                for child_city in cities:
                    if child_city not in path:  # See if this city has already been visited
                        has_child = True
                        cost = current_city.costTo(child_city)
                        if cost <= bcsf:
                            bcsf = cost
                            best_city = child_city
                if has_child is False:
                    break
                path.append(best_city)
                current_city = best_city
            sol = TSPSolution(path)
            if bssf.cost > sol.cost:
                bssf = TSPSolution(path)



        end_time = time.time()
        results['cost'] = bssf.cost
        results['time'] = end_time - start_time
        results['count'] = 1
        results['soln'] = bssf
        results['max'] = None
        results['total'] = None
        results['pruned'] = None
        return results

    ''' <summary>
        This is the entry point for the branch-and-bound algorithm that you will implement
        </summary>
        <returns>results dictionary for GUI that contains three ints: cost of best solution, 
        time spent to find best solution, total number solutions found during search (does
        not include the initial BSSF), the best solution found, and three more ints: 
        max queue size, total number of states created, and number of pruned states.</returns> 
    '''

    def branchAndBound(self, time_allowance=60.0):
        start_time = time.time()
        # try it a few times and take the best one
        # we want to maximize pruning
        bad_soln = self.defaultRandomTour()
        for i in range(10):
            other_soln = self.defaultRandomTour()
            if other_soln['cost'] < bad_soln['cost']:
                bad_soln = other_soln
        solver = BBSolver(self._scenario, bssf_cost=bad_soln['cost'], time_allowance=time_allowance, bssf=bad_soln['soln'].route)
        solution = solver.solve()
        end_time = time.time()
        results = solution
        results['time'] = end_time - start_time
        return results

    ''' <summary>
        This is the entry point for the algorithm you'll write for your group project.
        </summary>
        <returns>results dictionary for GUI that contains three ints: cost of best solution, 
        time spent to find best solution, total number of solutions found during search, the 
        best solution found.  You may use the other three field however you like.
        algorithm</returns> 
    '''

    def fancy(self, time_allowance=60.0):
        start_time = time.time()
        greedy_soln = self.greedy()
        solver = ACSolver(greedy_soln['soln'], self._scenario, time_allowance=time_allowance)
        soln = solver.solve()
        end_time = time.time()
        results = {}
        results['cost'] = soln.cost
        results['time'] = end_time - start_time
        results['count'] = 1
        results['soln'] = soln
        results['max'] = None
        results['total'] = None
        results['pruned'] = None
        return results
