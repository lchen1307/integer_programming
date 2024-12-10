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
