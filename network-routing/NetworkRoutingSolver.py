#!/usr/bin/python3


from CS312Graph import *
import time
import itertools




# --------------------- objects ----------------------------

class Node:
    id = None
    dist = None
    vertex = None

    def __init__(self, id, dist, vertex):
        self.id = id
        self.dist = dist
        self.vertex = vertex

    def updateDist(self, dist):
        self.dist = dist

class PriorityQueue:
    def makeQueue(self, vertices):
        print("make queue")

    def insert(self, dist, vertex):
        print("insert")

    def decreaseKey(self, key, value):
        print("decrease key")

    def deleteMin(self):
        print("delete min")

    def size(self):
        print("size")


class HeapPriorityQueue(PriorityQueue):
    def makeQueue(self, vertices):
        x = None

    def insert(self, dist, vertex):
        x = None

    def decreaseKey(self, key, value):
        x = None

    def deleteMin(self):
        x = None

    def size(self):
        x = None

# return the element with the smallest key and remove it from the set

class ArrayPriorityQueue(PriorityQueue):
    nodes = []
    def makeQueue(self, vertices):
        for v in vertices:
            # node = Node(float("inf"), v)
            node = Node(v.node_id, float("inf"), v)
            self.nodes.append(node)


    def insert(self, dist, vertex):
        node = self.Node(vertex.node_id, dist, vertex)
        self.nodes.append(node)
        self.nodes.sort(key=lambda x: x.dist, reverse=False)


    def decreaseKey(self, key, value):
        for node in self.nodes:
            if node.id == value:
                node.dist = key
        self.nodes.sort(key=lambda x: x.dist, reverse=False)

    def deleteMin(self):
        minNode = self.nodes.pop(0)
        return minNode


    def size(self):
        return len(self.nodes)

    def printQ(self):
        print("printing queue")
        for n in self.nodes:
            print(n.dist, n.id)
        print("\n")






#  -------------- network routing -------------------------


class NetworkRoutingSolver:
    def __init__( self):
        pass

    def initializeNetwork( self, network ):
        assert( type(network) == CS312Graph )
        self.network = network



    def getShortestPath( self, destIndex ):
        self.dest = destIndex
        # TODO: RETURN THE SHORTEST PATH FOR destIndex
        #       INSTEAD OF THE DUMMY SET OF EDGES BELOW
        #       IT'S JUST AN EXAMPLE OF THE FORMAT YOU'LL 
        #       NEED TO USE
        path_edges = []
        total_length = 0
        node = self.network.nodes[self.source]
        edges_left = 3
        while edges_left > 0:
            edge = node.neighbors[2]
            path_edges.append( (edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)) )
            total_length += edge.length
            node = edge.dest
            edges_left -= 1
        return {'cost':total_length, 'path':path_edges}

    def computeShortestPaths( self, srcIndex, use_heap=False ):
        self.source = srcIndex
        t1 = time.time()
        # TODO: RUN DIJKSTRA'S TO DETERMINE SHORTEST PATHS.
        #       ALSO, STORE THE RESULTS FOR THE SUBSEQUENT
        #       CALL TO getShortestPath(dest_index)

        self.Dijkstra(use_heap)


        t2 = time.time()
        return (t2-t1)



    def Dijkstra(self, use_heap):
        # prioity queue operations
        # Insert: add a new element to the set
        # Decrease-key: accommodate the decrease
        #   in key value of a particular element
        # Delete-min: return the element with the
        #   smallest key, and remove it from the set
        #

        dist = dict()
        prev = dict()

        graph = self.network
        vertices = self.network.nodes
        print(graph)
        print("/n")

        # graph = (V, E)
        # finding all distances from s (starting node) to u
        for v in vertices:
            dist[v.node_id] = float("inf")
            prev[v.node_id] = None

        dist[self.source] = 0

        # if use_heap:
        #     queue = self.HeapPriorityQueue().makeQueue(dist, vertices)
        # else:
        #     queue = self.ArrayPriorityQueue().makeQueue(dist, vertices)

        queue = ArrayPriorityQueue()
        queue.makeQueue(vertices)
        queue.decreaseKey(0, self.source)
        queue.printQ()
        while queue.size() > 0:
            u = queue.deleteMin()
            for edge in u.vertex.neighbors:
                if (dist[edge.dest.node_id] > dist[edge.src.node_id] + edge.length):
                    dist[edge.dest.node_id] = dist[edge.src.node_id] + edge.length
                    prev[edge.dest.node_id] = edge.src
                    queue.decreaseKey(dist[edge.dest.node_id], edge.dest.node_id)

            queue.printQ()
            print("dist")
            for a, b in dist.items():
                print(a, b)
        # H = makequeue(V) (using dist-values as keys) <- build a priority queue out of the given elements with the given key values
        # while H is not emty:
        #   u = deletemin(H) <- return the element with the smallest key and remove it from the set
        #   for all edges (u,v) in E:
        #       if (dist(v) > dist(u) + l(u,v):
        #           dist(v) = dist(u) + l(u,v)
        #           prev(v) = u
        #           decreasekey(H,v)
        return 0

    def arrayDijkstra(self):
        return 0



