# Branch and Bound Algorithm
# max 100 x1 + 150 x2
# 2 x1 + x2 <= 10
# 3 x1 + 6 x2 <= 40
# x1, x2 >= 0, and integer

# Create LP
from gurobipy import *
import numpy as np
import copy
import matplotlib.pyplot as plt

RLP = Model('relaxed MIP')
x = {}

for i in range(2):
    x[i] = RLP.addVar(lb = 0
                      , ub = GRB.INFINITY
                      , vtype = GRB.CONTINUOUS
                      , name = 'x_' + str(i)
                      )

RLP.setObjective(100 * x[0] + 150 * x[1], GRB.MAXIMIZE)
RLP.addConstr(2 * x[0] + x[1] <= 10, name = 'c_1')
RLP.addConstr(3 * x[0] + 6 * x[1] <= 40, name = 'c_2')

RLP.optimize()

# Node class
class Node:
    # this class defines the node
    def __init__(self):
        self.local_LB = 0
        self.local_UB = np.inf
        self.x_sol = {}
        self.x_int_sol = {}
        self.branch_var_list = []
        self.model = None
        self.cnt = None
        self.is_integer = False

    def deepcopy_node(node):
        new_node = Node()
        new_node.local_LB = 0
        new_node.local_UB = np.inf
        new_node.x_sol = copy.deepcopy(node.x_sol)
        new_node.x_int_sol = copy.deepcopy(node.x_int_sol)
        new_node.branch_var_list = []
        new_node.model = node.model.copy()
        new_node.cnt = node.cnt
        new_node.is_integer = node.is_integer

        return new_node

# Branch and Bound Algorithm
def Branch_and_bound(RLP):
    # initialize the initial node
    RLP.optimize()
    global_UB = RLP.ObjVal
    global_LB = 0
    eps = 1e-3
    incumbent_node = None
    Gap = np.inf

    '''
        Branch and Bound starts
    '''
    # create initial node
    Queue = []
    node = Node()
    node.local_LB = 0
    node.local_UB = global_UB
    node.model = RLP.copy()
    node.model.setParam('OutputFlag', 0)
    node.cnt = 0
    Queue.append(node)

    cnt = 0
    Global_UB_change = []
    Global_LB_change = []
    while (len(Queue) > 0 and global_UB - global_LB > eps):
        # select the current node
        current_node = Queue.pop()

