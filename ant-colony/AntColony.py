import numpy as np
import copy
import random
from TSPClasses import *
# 28.96 28049 (for 60)
# ALPHA = 1.5
# BETA = 2.0

# 24 32542
# ALPHA = 2.0
# BETA = 2.0

#56 24281
ALPHA = 1.0
BETA = 2.0

# ALPHA = .0
# BETA = 2.0

NUM_PHEROMONES = 50.0


def choose_index(probs):
    total_prob = sum(probs)
    choice = random.uniform(0.0, total_prob)
    vals = [sum(probs[:i]) for i in range(1, len(probs) + 1)]
    for i in range(len(vals)):
        if choice <= vals[i]:
            return i
    print('aah')


class Ant(object):

    def __init__(self, cities, master_pheromone_matrix, distance_matrix, best):
        self.cities = copy.deepcopy(cities)
        self.master_pheromones = master_pheromone_matrix
        self.dist = distance_matrix
        self.tour = [self.cities.pop(random.randint(0, len(self.cities) - 1))]
        self.pherms_to_add = np.zeros(master_pheromone_matrix.shape, dtype=float)
        self.num_pheromones = NUM_PHEROMONES
        self.bssf = best

    def generate_tour(self):
        while len(self.cities) > 0:
            pherm_factors = [(self.master_pheromones[self.tour[-1]._index, city._index] ** ALPHA) for city in self.cities]
            dist_factors = [((1 / self.dist[self.tour[-1]._index, city._index]) ** BETA) for city in self.cities]
            # the probabilities are determined in part by the distances - longer distances have lower probs, unless
            # pheromones are high.
            probs = [pherm_factors[i] * dist_factors[i] for i in range(len(pherm_factors))]
            idx_to_add = choose_index(probs)
            self.tour.append(self.cities.pop(idx_to_add))
        total_cost = sum([self.tour[i].costTo(self.tour[i + 1]) for i in range(len(self.tour) - 1)])
        for i in range(len(self.tour) - 1):
            this_one = self.tour[i]
            next_one = self.tour[i + 1]
            cost = this_one.costTo(next_one)
            ratio = cost / total_cost

            # the ratio that weighted the amount of pheromones given to each path was giving more
            # pheromones to longer paths which is the opposite of what we want to do. Since we already
            # take path length into account (dist_factors) I just give each path the same amount of pheromones
            # but if the path is shorter than the bssf it gets more pheromones
            # pheromones_to_alloc = self.num_pheromones * ratio
            if total_cost < self.bssf.cost:
                pheromones_to_alloc = 20
            else:
                pheromones_to_alloc = 2
            if math.isnan(pheromones_to_alloc):
                pheromones_to_alloc = 0
            self.pherms_to_add[this_one._index, next_one._index] = pheromones_to_alloc
        return self.tour, self.pherms_to_add
