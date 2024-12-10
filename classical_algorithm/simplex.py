# Simplex Algorithm

# the maximization problem
'''
maz Z = 2 x1 + 3 x2
s.t. x1 + 2 x2 <= 8
     4 x1 <= 16
     4 x2 <= 12
'''

# add slack variables and transform the problem into standard form
'''
maz Z = 2 x1 + 3 x2
s.t. x1 + 2 x2 + x3 == 8
     4 x1 + x4 == 16
     4 x2 + x5 == 12
'''

import numpy as np
import pandas as pd
import copy

Basic = [2, 3, 4]
Nonbasic = [0, 1]
c = np.array([2, 3, 0, 0, 0]).astype(float)
c_B = np.array([0, 0, 0]).astype(float)
c_N = np.array([2, 3]).astype(float)
A = np.array([[1, 2, 1, 0, 0]
            , [4, 0, 0, 1, 0]
            , [0, 4, 0, 0, 1]]).astype(float)
A_N = np.array([[1, 2]
              , [4, 0]
              , [0, 4]]).astype(float)
b = np.array([8, 16, 12]).astype(float)
B_inv = np.array([[1, 0, 0]
                , [0, 1, 0]
                , [0, 0, 1]]).astype(float)

x_opt = np.array([0, 0, 0, 0, 0]).astype(float)
z_opt = 0

solutionStatus = None

row_num = len(A)
column_num = len(A[0])

reducedCost = c_N - np.dot(np.dot(c_B, B_inv), A_N)
reducedCost

max_sigma = max(reducedCost)
print(np.argmax(reducedCost))
eps = 0.001

iterNum = 1
while (max_sigma >= eps):
    # indentify unbounded
    '''
    pass
    '''
    # determine the entering basic variables
    enter_var_index = Nonbasic[np.argmax(reducedCost)]
    print('enter_var_index: ', enter_var_index)

    # determine the leaving basic variable: minimum ratio test
    min_ratio = 1000000
    leave_var_index = 0
    for i in range(row_num):
        print('b: ', b[i], '\t A:', A[i][enter_var_index], '\t ratio:', b[i]/A[i][enter_var_index])
