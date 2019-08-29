import copy
import numpy as np


class State(object):

    def __init__(self, tour, matrix, prev_lower_bound):
        self.tour = tour
        self.matrix = copy.deepcopy(matrix)
        self.lower_bound = prev_lower_bound
        self._row_reduce_matrix()
        self._col_reduce_matrix()

    def __lt__(self, other):
        assert type(other) == State
        if len(self.tour) < len(other.tour):
            return False
        elif len(self.tour) == len(other.tour) and self.lower_bound < other.lower_bound:
            return False
        return True

    """def __lt__(self, other):
        assert type(other) == State
        if self.lower_bound < other.lower_bound:
            return False
        elif self.lower_bound == other.lower_bound and len(self.tour) < len(other.tour):
            return False
        return True"""

    def _row_reduce_matrix(self):
        matrix = copy.deepcopy(self.matrix)
        self.lower_bound += self._do_row_reduction(matrix)
        self.matrix = matrix

    def _col_reduce_matrix(self):
        # flip for row reduction
        matrix = np.transpose(self.matrix)
        self.lower_bound += self._do_row_reduction(matrix)
        # flip back
        self.matrix = np.transpose(matrix)

    @staticmethod
    def _do_row_reduction(matrix):
        lb_add = 0
        for i, row in enumerate(matrix):
            minVal = float('inf')
            notAllInfZero = False
            for j, item in enumerate(row):
                if item == 0.0:
                    notAllInfZero = False
                    break
                elif item != float('inf'):
                    notAllInfZero = True
                    if item < minVal:
                        minVal = item
            if notAllInfZero:
                # not all zero or inf, we subtract min from row
                for j, item in enumerate(row):
                    matrix[i, j] -= minVal
                lb_add += minVal
        return lb_add
