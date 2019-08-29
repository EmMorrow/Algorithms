from State import State
from heapq import heappush, heappop
from TSPClasses import TSPSolution
import copy
import numpy as np
import time


class BBSolver(object):

    def __init__(self, scenario, bssf_cost=float('inf'), bssf=None, time_allowance=60):
        self.initial = bssf
        self.bssfCost = bssf_cost
        self.bssf = None
        self.scenario = scenario
        self.heap = []
        self.time = time_allowance

    def solve(self):
        start_time = time.time()
        initial_matrix = np.zeros([len(self.scenario.getCities()), len(self.scenario.getCities())], dtype=float)
        cities = self.scenario.getCities()
        for i, city in enumerate(cities):
            for j, city2 in enumerate(cities):
                initial_matrix[i, j] = city.costTo(city2)
        initial_state = State([cities[0]], initial_matrix, 0)
        heappush(self.heap, initial_state)
        pruned = 0
        solns = 0
        max_heap_size = 1
        total = 1
        while len(self.heap) != 0:
            this_one = heappop(self.heap)
            if this_one.lower_bound > self.bssfCost:
                # prune these branches
                pruned += 1
                continue
            # get the ones we haven't visited yet
            not_visited = [city for city in cities if city not in this_one.tour]
            for city in not_visited:
                # make a child
                new_tour = [city for city in this_one.tour]
                new_tour.append(city)
                new_matrix = copy.deepcopy(this_one.matrix)
                frm = this_one.tour[-1]._index
                to = city._index
                new_bound = this_one.lower_bound + new_matrix[frm, to]
                # inf out the ones we don't want
                self._disable(new_matrix, frm, to)
                # row reduce and make the new state
                child_state = State(new_tour, new_matrix, new_bound)
                total += 1
                if len(cities) == len(child_state.tour):
                    # this is a solution
                    if child_state.lower_bound <= self.bssfCost:
                        solns += 1
                        self.bssf = child_state
                        self.bssfCost = child_state.lower_bound
                    else:
                        pruned += 1
                else:
                    # not a solution yet, put it on the heap if it's a good one
                    if child_state.lower_bound <= self.bssfCost:
                        heappush(self.heap, child_state)
                        if len(self.heap) > max_heap_size:
                            max_heap_size = len(self.heap)
                    else:
                        pruned += 1
            now = time.time()
            if now - start_time >= self.time:
                break
        retval = {}
        if self.bssf is None:
            retval['soln'] = TSPSolution(self.initial)
        else:
            retval['soln'] = TSPSolution(self.bssf.tour)
        retval['cost'] = self.bssfCost
        retval['pruned'] = pruned
        retval['max'] = max_heap_size
        retval['total'] = total
        retval['count'] = solns
        return retval

    @staticmethod
    def _disable(matrix, frm, to):
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if i == frm:
                    matrix[i, j] = float('inf')
                if j == to:
                    matrix[i, j] = float('inf')
        matrix[to, frm] = float('inf')
