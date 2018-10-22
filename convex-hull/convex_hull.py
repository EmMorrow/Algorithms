#!/usr/bin/python3
# why the shebang here, when it's imported?  Can't really be used stand alone, right?  And fermat.py didn't have one...
# this is 4-5 seconds slower on 1000000 points than Ryan's desktop...  Why?


from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QThread, pyqtSignal
# elif PYQT_VER == 'PYQT4':
# 	from PyQt4.QtCore import QLineF, QPointF, QThread, pyqtSignal
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time



class ConvexHullSolverThread(QThread):
	def __init__( self, unsorted_points,demo):
		self.points = unsorted_points
		print(demo)
		self.pause = demo
		QThread.__init__(self)

	def __del__(self):
		self.wait()

	show_hull = pyqtSignal(list,tuple)
	display_text = pyqtSignal(str)

# some additional thread signals you can implement and use for debugging, if you like
	show_tangent = pyqtSignal(list,tuple)
	erase_hull = pyqtSignal(list)
	erase_tangent = pyqtSignal(list)
					


	def run( self):
		assert( type(self.points) == list and type(self.points[0]) == QPointF )

		n = len(self.points)
		print( 'Computing Hull for set of {} points'.format(n) )

		t1 = time.time()
		print(type(self.points))
		sortedPoints = ConvexHullSolverThread.sortPoints(self.points)

		t2 = time.time()
		print('Time Elapsed (Sorting): {:3.3f} sec'.format(t2-t1))

		t3 = time.time()
		# TODO: COMPUTE THE CONVEX HULL USING DIVIDE AND CONQUER
		print(type(sortedPoints))
		convexHull = ConvexHullSolverThread.split(sortedPoints, self)

		t4 = time.time()

		USE_DUMMY = False
		if USE_DUMMY:
			# this is a dummy polygon of the first 3 unsorted points
			polygon = [QLineF(self.points[i],self.points[(i+1)%3]) for i in range(3)]
			
			# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
			# object can be created with two QPointF objects corresponding to the endpoints
			assert( type(polygon) == list and type(polygon[0]) == QLineF )
			# send a signal to the GUI thread with the hull and its color
			self.show_hull.emit(polygon,(255,0,0))

		else:
			hullSize = len(convexHull)
			polygon = [QLineF(convexHull[i], convexHull[(i + 1) % hullSize]) for i in range(hullSize)]
			assert (type(polygon) == list and type(polygon[0]) == QLineF)
			# send a signal to the GUI thread with the hull and its color
			self.show_hull.emit(polygon, (255, 0, 0))
			pass
			
		# send a signal to the GUI thread with the time used to compute the hull
		self.display_text.emit('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
		print('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

	# finds slope between two lines
	def slope(point1, point2):
		m = (point2.y() - point1.y()) / (point2.x() - point1.x())
		return m

	# returns the right-most point in a hull
	def getRightPoint(hull):
		right = None

		for curr in hull:
			right = curr
			if curr.x() > right.x():
				right = curr
		return right

	# returns the left-most point in a hull
	def getLeftPoint(hull):
		left = None
		for curr in hull:
			left = curr
			if curr.x() < left.x():
				left = curr
		return left

	def rotateList(l, n):
		return l[n:] + l[:n]

	# helper function to find the highest left point, highest right point
	# and the lowest left point and lowest right point
	def findConnectingPoints(hull, fixedPoint, isLessThan):
		lowestPoint = None
		if isLessThan:
			slope = 10000000000000000
			for y in hull:
				currSlope = ConvexHullSolverThread.slope(y, fixedPoint)
				if currSlope < slope:
					slope = currSlope
					lowestPoint = y

		else:
			slope = -1000000000000000
			for y in hull:
				currSlope = ConvexHullSolverThread.slope(y, fixedPoint)
				if currSlope > slope:
					slope = currSlope
					lowestPoint = y
		return lowestPoint


	# removes the points in between the upper common tangent and
	# lower common tangent so two hulls can be connected
	def removePoints(highPoint, lowPoint, hull, isLeft):
		i = hull.index(highPoint)
		j = hull.index(lowPoint)

		if isLeft:
			# rotates the list representation of the hull so the low point
			# is the beginning of the list
			rotatedHull = ConvexHullSolverThread.rotateList(hull,j)
			if len(rotatedHull) == 3:
				p1 = rotatedHull[1]
				p2 = rotatedHull[2]
				if p1.y() > p2.y():
					rotatedHull[1] = p2
					rotatedHull[2] = p1


			i = rotatedHull.index(highPoint)
			return rotatedHull[:i+1]

		else:
			# rotates the list representation of the hull so the high point
			# is the beginning of the list
			rotatedHull = ConvexHullSolverThread.rotateList(hull,i)
			if len(rotatedHull) == 3:
				p1 = rotatedHull[1]
				p2 = rotatedHull[2]
				if p1.y() < p2.y():
					rotatedHull[1] = p2
					rotatedHull[2] = p1

			j = rotatedHull.index(lowPoint)
			return rotatedHull[:j+1]


	# splits the list of points in half until there are only single
	# points then it calls connect to recursively connect the points
	def split(points, self):
		if len(points) == 1:
			return points

		left = points[:len(points)//2]
		right = points[len(points)//2:]

		lHull = ConvexHullSolverThread.split(left,self)
		rHull = ConvexHullSolverThread.split(right,self)

		return ConvexHullSolverThread.connect(lHull, rHull, self)


	# connects the left hull to the right hull
	def connect(lHull, rHull, self):
		if len(lHull) == 1:
			combined = lHull + rHull

		else:
			# get right-most point of left hull
			# get left-most point of right hull
			lPoint = ConvexHullSolverThread.getRightPoint(lHull)
			rPoint = ConvexHullSolverThread.getLeftPoint(rHull)

			# fix right point and check it w points on lHull going counter-clockwise
			# to find lowest slope
			highestLPoint = ConvexHullSolverThread.findConnectingPoints(lHull,rPoint,True)

			# fix the point found on left and check it w points on rHull going clockwise
			# to find highest slope
			highestRPoint = ConvexHullSolverThread.findConnectingPoints(rHull,highestLPoint,False)

			# fix right point and check it w points on lHull going clockwise
			# to find highest slope
			lowestLPoint = ConvexHullSolverThread.findConnectingPoints(lHull,rPoint,False)

			# fix the point found on left and check it w points on rHull going counter-clockwise
			# to find lowest slope
			lowestRPoint = ConvexHullSolverThread.findConnectingPoints(rHull,lowestLPoint,True)


			# get rid of points in-between the upper common tangent and the lower common tangent
			lHull = ConvexHullSolverThread.removePoints(highestLPoint, lowestLPoint, lHull, True)
			rHull = ConvexHullSolverThread.removePoints(highestRPoint, lowestRPoint, rHull, False)

			indexLTop = lHull.index(highestLPoint)
			indexLBottom = lHull.index(lowestLPoint)

			# since the lHull and rHull got rotated in removePoints() so the lHull starts with
			# the low point and ends with the high point and the rHull starts with the high point and ends
			# with the low point they can be added together to create the new hull
			combined = lHull + rHull

			# some concave lines would still show up so this method
			# double checks and gets rid of concave lines
			topIndex = len(combined)
			pointsToRemove = []
			# go through the list and draw a line between one point and the next next point
			# and if the point in between those two points is on the inside of the line
			# then remove the intermediate point from the hull
			for y in range(0,topIndex):
				if y == len(combined)-2:
					A = combined[y]
					P = combined[y+1]
					B = combined[0]
				elif y == len(combined)-1:
					A = combined[y]
					P = combined[0]
					B = combined[1]
				else:
					A = combined[y]
					P = combined[y+1]
					B = combined[y+2]

				d = (P.x()-A.x())*(B.y()-A.y())-(P.y()-A.y())*(B.x()-A.x())
				if d > 0:
					pointsToRemove.append(P)

			for y in pointsToRemove:
				combined.remove(y)

		return combined

	def sortPoints(points):
		points.sort(key=ConvexHullSolverThread.myFunc)
		return points

	def myFunc(point):
		return point.x()

	def convexHull(self):
		return self


