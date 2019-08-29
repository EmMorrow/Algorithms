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
import queue as Q
from itertools import count




class TSPSolver:
    def __init__( self, gui_view ):
        self._scenario = None

    def setupWithScenario( self, scenario ):
        self._scenario = scenario


    ''' <summary>
        This is the entry point for the default solver
        which just finds a valid random tour
        </summary>
        <returns>results array for GUI that contains three ints: cost of solution, time spent to find solution, number of solutions found during search (
not counting initial BSSF estimate)</returns> '''
    def defaultRandomTour( self, start_time, time_allowance=60.0 ):

        results = {}


        # start_time = time.time()

        cities = self._scenario.getCities()
        ncities = len(cities)
        foundTour = False
        count = 0
        while not foundTour:
            # create a random permutation
            perm = np.random.permutation( ncities )

            #for i in range( ncities ):
                #swap = i
                #while swap == i:
                    #swap = np.random.randint(ncities)
                #temp = perm[i]
                #perm[i] = perm[swap]
                #perm[swap] = temp

            route = []

            # Now build the route using the random permutation
            for i in range( ncities ):
                route.append( cities[ perm[i] ] )

            bssf = TSPSolution(route)
            #bssf_cost = bssf.cost()
            #count++;
            count += 1

            #if costOfBssf() < float('inf'):
            if bssf.costOfRoute() < np.inf:
                # Found a valid route
                foundTour = True
        #} while (costOfBssf() == double.PositiveInfinity);                // until a valid route is found
        #timer.Stop();

        results['cost'] = bssf.costOfRoute() #costOfBssf().ToString();                          // load results array
        # results['time'] = time.time() - start_time
        results['count'] = count
        results['soln'] = bssf

       # return results;
        return results



    def greedy( self, start_time, time_allowance=60.0 ):
        pass

    def branchAndBound( self, start_time, time_allowance=60.0 ):
        start_time = time.time()
        tiebreaker = count()
        cities = self._scenario.getCities()
        size = len(cities)
        adjMatrix = np.zeros(shape=(size,size))
        queue = Q.PriorityQueue()

        # find the initial best solution using the default random tour algorithm
        findBssf = self.defaultRandomTour(0, 10)

        if findBssf != None:
            bssf = findBssf['soln'] # need to figure out how to set bssf
        else:
            bssf = TSPSolution(cities)
            bssf.costOfRoute = float('inf')

        pruned = 0
        stored = 0
        update = 0
        states = 0
        results = {}

        # fill the matrix with initial path weights
        for i in range(size):
            for j in range(size):
                if i != j:
                    dist = cities[i].costTo(cities[j])
                    # print("dist from ", cities[i]._name, " to ", cities[j]._name, ": ", dist)
                    adjMatrix[i][j] = dist
                else:
                    adjMatrix[i][j] = float("inf")

        # reduce the matrix to get the first states lower bound
        adjMatrix, weight = self.reduceMatrix(adjMatrix)
        my_path = []
        my_path.append(0)


        # add the state to the priority queue (priority, bound, tiebreaker, matrix, path)
        queue.put((0, weight, next(tiebreaker), adjMatrix, my_path))

        # while there are still states in the queue and we haven't passed the time allowance
        while not queue.empty() and (time.time() - start_time) < time_allowance:
            if queue.qsize() > stored:
                stored = queue.qsize()

            # get the object from the queue (by priority) and store it in a state object
            s = queue.get()
            curr_state = State(s[1], s[3], s[4], s[0])

            # only expand this state if it's bound is lower than the current bssf cost
            if curr_state.bound < bssf.costOfRoute():
                children = self.makeChildren(curr_state)
                for child in children:
                    states += 1

                    # only add child states to the priority queue if it's bound is lower than the current bssf cost
                    if child['bound'] < bssf.costOfRoute():
                        queue.put((child['priority'], child['bound'], next(tiebreaker), child['matrix'], child['path']))
                    else:
                        pruned += 1

            # if the state is a full tsp path
            if len(cities) == len(curr_state.path):
                # check if better than initial bssf
                if curr_state.bound < bssf.costOfRoute():
                    update += 1
                    route = []
                    for i in curr_state.path:
                        route.append(cities[i])

                    tbssf = TSPSolution(route)
                    if tbssf.costOfRoute() < float('inf'):
                        bssf = tbssf
                    print("NEW BSSF: ", bssf.costOfRoute(), " vs ", curr_state.bound)


        print("stored: ", stored)
        print("update: ", update)
        print("states: ", states)
        print("pruned: ", pruned)
        print("time: ", time.time() - start_time)
        pruned += queue.qsize()
        return self.getResults(bssf.costOfRoute(), time.time() - start_time, update, bssf)

            # look from the current state to see which branches can be expanded
            # expand all the branches (if finding paths from 0 -> 1) make row 0 inf and column 1 inf and row 1, column 0 inf
            # find the branch that has the lowest bound and add it to the priority queue

            # in the priority queue nodes add reduced matrix, cost, and curr city


    def getResults(self, cost, time, count, soln):
        results = {}
        results['cost'] = cost
        results['time'] = time
        results['count'] = count
        results['soln'] = soln
        return results

    # [row][column]
    # child needs path, priority, bound, matrix

    # expands a search state
    def makeChildren(self, state):
        children = []
        matrix = state.matrix
        cities = self._scenario.getCities()
        size = len(cities)
        path1 = state.path.copy()
        curr_node = path1[len(path1) - 1]
        for i in range(size):
            path = state.path.copy()
            new_len = matrix[curr_node][i]
            if new_len < float('inf'):
                # if the node where i is isn't already in the path
                # then create state that includes node i
                if i not in path:
                    path.append(i)
                    chld_matrix = matrix.copy()

                    # put inf in the places that can no longer be reached
                    chld_matrix[i][curr_node] = float('inf')
                    for j in range(size):
                        chld_matrix[curr_node][j] = float('inf')
                        chld_matrix[j][i] = float('inf')

                    # reduce the child matrix and get its lower bound
                    chld_matrix, weight = self.reduceMatrix(chld_matrix)
                    chld_bound = weight + new_len + state.bound
                    chld_path = path
                    # set the states priority by prioritizing nodes
                    # that are lower down in the tree
                    chld_priority = chld_bound / len(chld_path)

                    # put together the child object and add it to children
                    child = {}
                    child['priority'] = chld_priority
                    child['path'] = chld_path
                    child['bound'] = chld_bound
                    child['matrix'] = chld_matrix
                    children.append(child)
        return children

    # reduces rows and columns of a matrix and gets the lower bound
    def reduceMatrix(self, matrix):
        weight = 0

        # get the min values from each row
        mins = np.min(matrix,axis=1)
        for i in range(np.size(matrix,0)):
            currMin = mins[i]

            # if the min isn't infinity then subtract the min
            # from all values in the row
            if currMin != float('inf'):
                weight += currMin
                for j in range(np.size(matrix,1)):
                    matrix[i][j] = matrix[i][j] - currMin

        # get the min values from each column
        mins = np.min(matrix, axis=0)
        for j in range(np.size(matrix, 0)):
            currMin = mins[j]
            if currMin != float('inf'):
                weight += currMin

                # if the min isn't infinity then subtract the min
                # from all values in the column
                for i in range(np.size(matrix, 1)):
                    matrix[i][j] = matrix[i][j] - currMin

        return matrix, weight


    def fancy( self, start_time, time_allowance=60.0 ):
        pass


class State(object):
    priority = None
    bound = None
    matrix = None
    path = None

    def __init__(self, bound, matrix, path, priority):
        self.bound = bound
        self.matrix = matrix
        self.path = path
        self.priority = priority

    def __lt__(self, other):
        # return (self.priority > other.priority) ^ (self.priority < other.priority)
        if self.priority < other.priority: return 1
        if self.priority > other.priority: return -1
        return 0



# class State:
#     id = None
#     dist = None # this is the priority
#     bound = None
#     matrix = None
#     path = None
#
#     def __init__(self, id, dist, vertex, path, ddist):
#         self.id = id
#         self.bound = dist
#         self.matrix = vertex
#         self.path = path
#         self.dist = ddist
#
#     def updateDist(self, dist):
#         self.dist = dist

# class PriorityQueue:
#     # min heap represented as an array
#     heap = []
#     indexMap = dict()
#     index = 0
#
#     def __init__(self):
#         # add an dummy element at index 0 to make array operations easier
#         self.heap.append(-1)
#
#     # move i up in the heap until it's smaller than it's child nodes
#     def bubbleUp(self, i):
#         # while there is still a parent node
#         while i // 2 > 0:
#             parentI = i // 2
#             # if the child dist is smaller than the parent dist then swap the nodes
#             if self.heap[i].dist < self.heap[parentI].dist:
#                 self.indexMap[self.heap[i].id] = parentI
#                 self.indexMap[self.heap[parentI].id] = i
#                 tmp = self.heap[parentI]
#                 self.heap[parentI] = self.heap[i]
#                 self.heap[i] = tmp
#             i = parentI
#
#     # move i down in the heap until it's larger than it's parent nodes
#     def siftDown(self, i):
#         while (i * 2) <= len(self.heap) - 1:
#             # find the minimum child index
#             if i * 2 + 1 > len(self.heap) - 1:
#                 childI = i * 2
#             else:
#                 if self.heap[i * 2].dist < self.heap[i * 2 + 1].dist:
#                     childI = i * 2
#                 else:
#                     childI = i * 2 + 1
#             # if parent dist is bigger than child dist
#             if self.heap[i].dist > self.heap[childI].dist:
#                 # update index in the index map for nodes being swapped
#                 self.indexMap[self.heap[i].id] = childI
#                 self.indexMap[self.heap[childI].id] = i
#
#                 # swap parent and child nodes
#                 tmp = self.heap[i]
#                 self.heap[i] = self.heap[childI]
#                 self.heap[childI] = tmp
#             i = childI
#
#     # fill the queue with the vertices
#     def makeQueue(self, vertices):
#         for v in vertices:
#             node = State(v.node_id, float("inf"), v)
#             self.heap.append(node)
#             self.indexMap[node.id] = len(self.heap) - 1
#
#     # place the new element at the bottom of the tree and bubble up
#     # (if it's smaller than the parent swap the two and repeat
#     def insert(self, bound, matrix, path, dist):
#         self.heap.append(State(self.index, bound, matrix, path, dist))
#         self.indexMap[self.index] = len(self.heap) - 1
#         self.bubbleUp(len(self.heap) - 1)
#         self.index += 1
#
#     # find node to decrease and bubble it up
#     def decreaseKey(self, key, value):
#         i = self.indexMap[value]
#         self.heap[i].dist = key
#         self.bubbleUp(i)
#
#     # return the root value and adjust the tree
#     def deleteMin(self):
#         retval = self.heap[1]
#         self.heap[1] = self.heap[len(self.heap) - 1]
#         # delete the min value from index map and update bottom
#         del self.indexMap[retval.id]
#         self.indexMap[self.heap[1].id] = 1
#
#         self.heap.pop()
#         self.siftDown(1)
#         return retval
#
#     def size(self):
#         return len(self.heap) - 1





