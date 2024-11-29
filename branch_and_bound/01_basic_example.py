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
        cnt += 1

        # solve the current model
        current_node.model.optimize()
        Solution_status = current_node.model.Status

        '''
        OPTIMAL = 2
        INFEASIBLE = 3
        UNBOUNDED = 5
        '''

        # check whether the current solution is integer and execute prune step

        '''
            is_integer: mark whether the current solution is integer solution
            Is_Pruned: mark whether the current node is pruned
        '''
        is_integer = True
        Is_Pruned = False

        if Solution_status == 2:
            for var in current_node.model.getVars():
                current_node.x_sol[var.varName] = var.x
                print(var.varName, ' = ', var.x)

                # round the solution to get an integer solution
                current_node.x_int_sol[var.varName] = (int)(var.x)
                if (abs((int)(var.x) - var.x) >= eps):
                    is_integer = False
                    current_node.branch_var_list.append(var.varName) # to record the candidate branch variables

            # update the LB and UB
            if is_integer == True:
                # For integer solution node, update the LB and UB
                current_node.is_integer = True
                current_node.local_LB = current_node.model.ObjVal
                current_node.local_UB = current_node.model.ObjVal #?
                if (current_node.local_LB > global_LB):
                    global_LB = current_node.local_LB
                    incumbent_node = Node.deepcopy_node(current_node)

            if is_integer == False:
                # For non-integer solution node, update the LB and UB
                current_node.is_integer = False
                current_node.local_LB = current_node.model.ObjVal
                current_node.local_UB = 0
                for var_name in current_node.x_int_sol.keys():
                    var = current_node.model.getVarByName(var_name)
                    current_node.local_LB += current_node.x_int_sol[var_name] * var.Obj
                if (current_node.local_LB > global_LB or (
                    current_node.local_LB == global_LB and current_node.is_integer == True)):
                    global_LB = current_node.local_LB
                    incumbent_node = Node.deepcopy_node(current_node)
                    incumbent_node.local_LB = current_node.local_LB
                    incumbent_node.local_UB = current_node.local_UB
            '''
                PRUNE step
            '''
            # prune by optimality
            if (is_integer == True):
                Is_Pruned = True

            # prune by bound
            if (is_integer == False and current_node.local_UB < global_LB):
                Is_Pruned = True

            Gap = round(100 * (global_UB - global_LB)/global_LB, 2)
            print('\n ---------- \n', cnt, '\t Gap = ', Gap, ' %')

        elif (Solution_status != 2):
            # the current node is infeasible or unbounded
            is_integer = False
            '''
                PRUNE step
            '''
            # prune by infeasibility
            Is_Pruned = True
            continue

        '''
            BRANCH step
        '''
        if (Is_Pruned == False):
            # select the branching variable
            branch_var_name = current_node.branch_var_list[0]
            left_var_bound = (int)(current_node.x_sol[branch_var_name])
            right_var_bound = (int)(current_node.x_sol[branch_var_name]) + 1

            # create two child nodes
            left_node = Node.deepcopy_node(current_node)
            right_node = Node.deepcopy_node(current_node)

            # create the left child node
            temp_var = left_node.model.getVarByName(branch_var_name)
            left_node.model.addConstr(temp_var <= left_var_bound, name = 'branch_left_' + str(cnt))
            left_node.model.setParam('OutputFlag', 0)
            left_node.model.update()
            cnt += 1
            left_node.cnt = cnt

            # create the right child node
            temp_var = right_node.model.getVarByName(branch_var_name)
            right_node.model.addConstr(temp_var >= right_var_bound, name = 'branch_right_' + str(cnt))
            right_node.model.setParam('OutputFlag', 0)
            right_node.model.update()
            cnt += 1
            right_node.cnt = cnt

            Queue.append(left_node)
            Queue.append(right_node)

            # update the global UB, explor all the leaf nodes
            temp_global_UB = 0
            for node in Queue:
                node.model.optimize()
                if (node.model.status == 2):
                    if (node.model.ObjVal > temp_global_UB):
                        temp_global_UB = node.model.ObjVal

            global_UB = temp_global_UB
            Global_UB_change.append(lobal_UB)
            Global_LB_change.append(global_LB)

    # all the nodes are explored, update the LB and UB
    global_UB = global_LB
    Gap = round(100 * (global_UB - global_LB)/global_LB, 2)
    Global_UB_change.append(global_UB)
    Global_LB_change.append(global_LB)

    print('\n\n\n\n')
    print('--------------------------------------------')
    print('          Branch and Bound terminates       ')
    print('          Optimal solution found            ')
    print('--------------------------------------------')
    print('\nFinal Gap = ', Gap, ' %')
    print('Optimal solution: ', incumbent_node.x_int_sol)
    print('Optimal Obj: ', global_LB)

    return incumbent_node, Gap, Global_UB_change, Global_LB_change


# Solve the IP model by branch and bound
incumbent_node, Gap, Global_UB_change, Global_LB_change = Branch_and_bound(RLP)


# Plot the convergence curve
# fig = plt.figure(1)
# plt.figure(figsize=(15, 10))
font_dict = {"family": 'Arial',
             "style": "oblique",
             "weight": "normal",
             "color": "green",
             "size": 20
             }

plt.rcParams['figure.figsize'] = (12.0, 8.0)
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 16

x_cor = range(1, len(Global_LB_change) + 1)
plt.plot(x_cor, Global_LB_change, label = 'LB')
plt.plot(x_cor, Global_UB_change, label = 'UB')
plt.legend()
plt.xlabel('Iteration', fontdict = font_dict)
plt.ylabel('Bounds update', fontdict = font_dict)
plt.title('Bounds update during branch and bound procedure \n', fontsize = 23)
plt.show()

