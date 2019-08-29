#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import math
import numpy as np
import time

# Used to compute the bandwidth for banded version
MAXINDELS = 3

# Used to implement Needleman-Wunsch scoring
MATCH = -3
INDEL = 5
SUB = 1

class GeneSequencing:

	def __init__( self ):
		pass

	
# This is the method called by the GUI.  _sequences_ is a list of the ten sequences, _table_ is a
# handle to the GUI so it can be updated as you find results, _banded_ is a boolean that tells
# you whether you should compute a banded alignment or full alignment, and _align_length_ tells you 
# how many base pairs to use in computing the alignment

	def initialize(self, seq1, seq2):
		# seq1 polynomial
		# seq2 exponential
		ySize = len(seq2) + 1
		xSize = len(seq1) + 1
		scoreMatrix = np.zeros((ySize,xSize), dtype=int)

		# exponential
		for i in range(1, ySize):
			scoreMatrix[i][0] = scoreMatrix[i - 1][0] + INDEL

		#polynomial
		for i in range(1, xSize):
			scoreMatrix[0][i] = scoreMatrix[0][i - 1] + INDEL

		return scoreMatrix

	def fill(self, seq1, seq2, matrix):
		for i in range(1, len(seq2) + 1):
			for j in range(1, len(seq1) + 1):
				min = None
				if seq1[j-1] == seq2[i-1]:
					diag = matrix[i - 1][j - 1] + MATCH
				else:
					diag = matrix[i - 1][j - 1] + SUB

				left = matrix[i][j-1] + INDEL
				above = matrix[i - 1][j] + INDEL

				if diag < left:
					min = diag
				else:
					min = left

				if above < min:
					min = above

				matrix[i][j] = min

		return matrix

	def traceback(self, seq1, seq2, matrix):
		align1 = ""
		align2 = ""

		i = len(seq1)
		j = len(seq2)
		# print("look! ", matrix[j][i])
		while i > 0 and j > 0:
			if seq1[i - 1] == seq2[j - 1]:
				score = MATCH
			else:
				score = SUB
			if i > 0 and j > 0 and matrix[j, i] == matrix[j - 1, i - 1] + score: # if it came from diagonal
				# print("from diagonal")
				align1 = seq1[i - 1] + align1
				align2 = seq2[j - 1] + align2
				i -= 1
				j -= 1
			elif i > 0 and matrix[j, i] == matrix[j, i - 1] - INDEL:
				# print("from top")
				align1 = seq1[i - 1] + align1
				align2 = "-" + align2
				i -= 1
			else:
				# print("from side")
				align1 = "-" + align1
				align2 = seq2[j - 1] + align2
				j -= 1
			# print(align1)
			# print(align2,"\n")
			# print("next val: ", matrix[j][i])
		return align1, align2

	def notBanded(self, seq1, seq2):
		ySize = len(seq2) + 1
		xSize = len(seq1) + 1
		cameFrom = 0

		# initialize the score matrix and traceback matrix
		matrix = np.zeros((ySize, xSize), dtype=int)
		traceMatrix = np.zeros((ySize, xSize), dtype=int)

		# fill the first row and first column of the score matrix
		for i in range(1, ySize):
			matrix[i][0] = matrix[i - 1][0] + INDEL

		for i in range(1, xSize):
			matrix[0][i] = matrix[0][i - 1] + INDEL

		# fill the rest of the score and traceback matrix
		for i in range(1, len(seq2) + 1):
			for j in range(1, len(seq1) + 1):
				min = None

				# get values for if you're extracting from diag, left, or above
				if seq1[j-1] == seq2[i-1]:
					diag = matrix[i - 1][j - 1] + MATCH
				else:
					diag = matrix[i - 1][j - 1] + SUB

				left = matrix[i][j-1] + INDEL
				above = matrix[i - 1][j] + INDEL

				# determine the minimum value and keep track of where it came from
				if diag < left:
					min = diag
					cameFrom = 1 	# from diagonal
				else:
					min = left
					cameFrom = 2 	# from left

				if above < min:
					min = above
					cameFrom = 3 	# from above

				matrix[i][j] = min
				traceMatrix[i][j] = cameFrom

		align1 = ""
		align2 = ""

		i = len(seq1)
		j = len(seq2)
		score = matrix[j][i]

		# traceback through the matrix to get the alignments
		while i > 0 and j > 0:
			if traceMatrix[j][i] == 1:  	# if it came from diagonal
				align1 = seq1[i - 1] + align1
				align2 = seq2[j - 1] + align2
				i -= 1
				j -= 1
			elif traceMatrix[j][i] == 2: 	# if it came from left
				align1 = seq1[i - 1] + align1
				align2 = "-" + align2
				i -= 1
			elif traceMatrix[j][i] == 3: 	# if it came from above
				align1 = "-" + align1
				align2 = seq2[j - 1] + align2
				j -= 1

		return {'a1':align1, 'a2':align2, 'score':score}


	def bandedFill(self, seq1, seq2):
		ySize = len(seq2) + 1
		xSize = len(seq1) + 1
		cameFrom = 0

		# initialize the score matrix and traceback matrix
		matrix = np.zeros((ySize, xSize), dtype=int)
		traceMatrix = np.zeros((ySize, xSize), dtype=int)

		# fill the matrix with a large number so if it isn't in the band
		# it won't interfere with the scores
		matrix.fill(9000)
		matrix[0][0] = 0

		# fill the first row and first column of the score matrix
		for i in range(1, 4):
			matrix[i][0] = matrix[i - 1][0] + INDEL
		for i in range(1, 4):
			matrix[0][i] = matrix[0][i - 1] + INDEL

		# set the indices where we should fill in the banded matrix
		minI = 1
		maxI = 5
		down = False

		# fill the rest of the score and traceback matrix
		for i in range(1, len(seq2) + 1):
			for j in range(minI, maxI):
				min = None

				# get values for if you're extracting from diag, left, or above
				if seq1[j-1] == seq2[i-1]:
					diag = matrix[i - 1][j - 1] + MATCH
				else:
					diag = matrix[i - 1][j - 1] + SUB

				left = matrix[i][j-1] + INDEL
				above = matrix[i - 1][j] + INDEL

				# determine the minimum value and keep track of where it came from
				if diag < left:
					min = diag
					cameFrom = 1	# from diagonal
				else:
					min = left
					cameFrom = 2	# from left

				if above < min:
					min = above
					cameFrom = 3	# from above

				matrix[i][j] = min
				traceMatrix[i][j] = cameFrom

			# set the indices so banded never gets larger than 7 cells horizontal or diagonal
			if maxI - minI == 7:
				minI += 1
				down = True
			elif down:
				minI += 1
			if maxI < len(seq1) + 1:
				maxI += 1

		# traceback through the matrix to get the alignments
		align1 = ""
		align2 = ""

		i = len(seq1)
		j = len(seq2)
		score = matrix[j][i]
		while i > 0 and j > 0:
			if traceMatrix[j][i] == 1:  	# if it came from diagonal
				align1 = seq1[i - 1] + align1
				align2 = seq2[j - 1] + align2
				i -= 1
				j -= 1
			elif traceMatrix[j][i] == 2:	# if it came from left
				align1 = seq1[i - 1] + align1
				align2 = "-" + align2
				i -= 1
			elif traceMatrix[j][i] == 3:	# if it came from above
				align1 = "-" + align1
				align2 = seq2[j - 1] + align2
				j -= 1
			else:	# if the alignment can't be complete break out of loop
				i = 0
				j = 0


		return {'a1': align1, 'a2': align2, 'score': score}

	def align( self, sequences, table, banded, align_length):
		self.banded = banded
		self.MaxCharactersToAlign = align_length
		results = []

		for i in range(len(sequences)):
			jresults = []
			for j in range(len(sequences)):

				if(j < i):
					s = {}
				else:
					seq1 = sequences[i]
					seq2 = sequences[j]
					seq1 = seq1[:align_length]
					seq2 = seq2[:align_length]
					# scoreMatrix = self.initialize(seq1,seq2)
					# scoreMatrix = self.fill(seq1, seq2, scoreMatrix)
					# a1, a2 = self.traceback(seq1, seq2, scoreMatrix)
					# score = scoreMatrix[len(seq2)][len(seq1)]

					if banded:
						ans = self.bandedFill(seq1,seq2)
						a1 = ans['a1']
						a2 = ans['a2']
						score = ans['score']
					else:
						ans = self.notBanded(seq1,seq2)
						a1 = ans['a1']
						a2 = ans['a2']
						score = ans['score']



					if score == 9000:
						score = float('inf')
						a1 = "No Alignment Possible"
						a2 = "No Alignment Possible"
					s = {'align_cost':score, 'seqi_first100':a1[:100], 'seqj_first100':a2[:100]}
					table.item(i,j).setText('{}'.format(int(score) if score != math.inf else score))
					table.repaint()
				jresults.append(s)
			results.append(jresults)
		return results


