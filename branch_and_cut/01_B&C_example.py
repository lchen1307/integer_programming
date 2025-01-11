from __future__ import  print_function
from gurobipy import *
import re
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import networkx as nx
import copy
import random

from holoviews.plotting.bokeh.styles import font_size
from jmespath.ast import current_node
from networkx.classes import nodes
from pylint.checkers.utils import node_type
from sympy.physics.units import length


class Data:
    def __init__(self):
        self.customerNum = 0
        self.nodeNum = 0
        self.vehicleNum = 0
        self.capacity = 0
        self.cor_X = []
        self.cor_Y = []
        self.demand = []
        self.serviceTime = []
        self.readyTime = []
        self.dueTime = []
        self.disMatrix = [[]]
        self.arcs = {}

    # function to read data from file
    def readData(data, path, customerNum):
        data.customerNum = customerNum
        data.nodeNum = customerNum + 2
        f = open(path, 'r')
        lines = f.readlines()
        count = 0

        # read the info
        for line in lines:
            count = count + 1
            if (count == 5):
                line = line[:-1].strip()
                str = re.split(r' +', line)
                data.vehicleNum = int(str[0])
                data.capacity = float(str[1])
            elif (count >= 10 and count <= 10 + customerNum):
                line = line[:-1]
                str = re.split(r' +', line)
                data.cor_X.append(float(str[2]))
                data.cor_Y.append(float(str[3]))
                data.demand.append(float(str[4]))
                data.readyTime.append(float(str[5]))
                data.dueTime.append(float(str[6]))
                data.serviceTime.append(float(str[7]))

        data.cor_X.append(data.cor_X[0])
        data.cor_Y.append(data.cor_Y[0])
        data.demand.append(data.demand[0])
        data.readyTime.append(data.readyTime[0])
        data.dueTime.append(data.dueTime[0])
        data.serviceTime.append(data.serviceTime[0])

        # compute the distance matrix
        data.disMatrix = [([0] * data.nodeNum) for p in range(data.nodeNum)]
        for i in range(0, data.nodeNum):
            for j in range(0, data.nodeNum):
                temp = (data.cor_X[i] - data.cor_X[j])**2 + (data.cor_Y[i] - data.cor_Y[j])**2
                data.disMatrix[i][j] = round(math.sqrt(temp), 1)
                temp = 0

        # initialize the arc
        for i in range(data.nodeNum):
            for j in range(data.nodeNum):
                if (i == j):
                    data.arcs[i, j] = 0
                if (i != j):
                    data.arcs[i, j] = 1
        return data

    def preprocess(data):
        # preprocessing for ARCS
        # 除去不符合时间窗和容量约束的变
        for i in range(data.nodeNum):
            for j in range(data.nodeNum):
                if (i == j):
                    data.arcs[i, j] = 0
                elif (data.readyTime[i] + data.serviceTime[i] + data.disMatrix[i][j] > data.dueTime[j]\
                        or data.demand[i] + data.demand[j] > data.capacity):
                    data.arcs[i, j] = 0
                elif (data.readyTime[0] + data.serviceTime[i] + data.disMatrix[0][i] + data.disMatrix[i][data.nodeNum-1] > data.dueTime[data.nodeNum-1]):
                    print('the calculating example is false')
                else:
                    data.arcs[i, j] = 1

        for i in range(data.nodeNum):
            data.arcs[data.nodeNum-1, i] = 0
            data.arcs[i, 0] = 0

        return data

    def printData(data, customerNum):
        print('打印下面数据：\n')
        print('vehicle number = %4d' % data.vehicleNum)
        print('vehicle capacity = %4d' % data.capacity)
        for i in range(len(data.demand)):
            print('{0}\t{1}\t{2}\t{3}'.format(data.demand[i], data.readyTime[i], data.dueTime[i], data.serviceTime[i]))

        print('---------- 距离矩阵 ----------\n')
        for i in range(data.nodeNum):
            for j in range(data.nodeNum):
                print('%6.2f' % (data.disMatrix[i][j]), end = '')
            print()

data = Data()
path = 'r101.txt'
customerNum = 100
data = Data.readData(data, path, customerNum)
data.vehicleNum = 8
Data.printData(data, customerNum)


# Build Graph
# 构建有向图对象
Graph = nx.DiGraph()
cnt = 0
pos_location = {}
nodes_col = {}
nodeList = []
for i in range(data.nodeNum):
    X_coor = data.cor_X[i]
    Y_coor = data.cor_Y[i]
    name = str(i)
    nodeList.append(name)
    nodes_col[name] = 'gray'
    node_type = 'customer'
    if (i == 0):
        node_type = 'depot'
    Graph.add_node(name
                   , ID = 1
                   , node_type = node_type
                   , time_window = (data.readyTime[i], data.dueTime[i])
                   , arrive_time = 10000
                   , demand = data.demand
                   , serviceTime = data.serviceTime
                   , x_coor = X_coor
                   , y_coor = Y_coor
                   , min_dis = 0
                   , previous_node = None
                   )

    pos_location[name] = (X_coor, Y_coor)

# add edges into the graph
for i in range(data.nodeNum):
    for j in range(data.nodeNum):
        if (i == j or (i == 0 and j == data.nodeNum - 1) or (j ==0 and i == data.nodeNum - 1)):
            pass
        else:
            Graph.add_edge(str(i), str(j)
                           , travelTime = data.disMatrix[i][j]
                           , length = data.disMatrix[i][j]
                           )

nodes_col['0'] = 'red'
nodes_col[str(data.nodeNum - 1)] = 'red'
plt.rcParams['figure.figsize'] = (10, 10)
nx.draw(Graph
        , pos = pos_location
        , with_labels = True
        , node_size = 50
        , node_color = nodes_col.values()
        , font_size = 15
        , font_family = 'arial'
        , edgelist = []
        )

fig_name = 'network_' + str(customerNum) + '_1000.jpg'
plt.savefig(fig_name, dpi = 600)
plt.show()

# Build and solve VRPTW
big_M = 100000

# create the model
model = Model('VRPTW')

# decision variables
x = {}
x_var = {}
s = {}
for i in range(data.nodeNum):
    for k in range(data.vehicleNum):
        name = 's_' + str(i) + '_' + str(k)
        s[i, k] = model.addVar(lb = data.readyTime[i]
                               , ub = data.dueTime[i]
                               , vtype = GRB.CONTINUOUS
                               , name = name
                               )
        for j in range(data.nodeNum):
            if (i != j and data.arcs[i, j] == 1):
                name = 'x_' + str(i) + '_' + str(j) + '_' + str(k)
                x[i, j, k] = model.addVar(lb = 0
                                          , ub = 1
                                          , vtype = GRB.BINARY
                                          , name = name
                                          )
                x_var[i, j, k] = model.addVar(lb = 0
                                              , ub = 1
                                              , vtype = GRB.CONTINUOUS
                                              , name = name
                                              )

# Add constraints
# create the objective expression
obj = LinExpr()
for i in range(data.nodeNum):
    for j in range(data.nodeNum):
        if (i != j and data.arcs[i, j] == 1):
            for k in range(data.vehicleNum):
                obj.addTerms(data.disMatrix[i][j], x[i, j, k])

# add the objective function into the model
model.setObjective(obj, GRB.MINIMIZE)

# constraint 1
for i in range(1, data.nodeNum - 1):
    expr = LinExpr(0)
    for j in range(data.nodeNum):
        if (i != j and data.arcs[i, j] == 1):
            for k in range(data.vehicleNum):
                if (i != 0 and i != data.nodeNum - 1):
                    expr.addTerms(1, x[i, j, k])

    model.addConstr(expr == 1, 'c1')
    expr.clear()

# constraint 2
for k in range(data.vehicleNum):
    expr = LinExpr(0)
    for i in range(1, data.nodeNum - 1):
        for j in range(data.nodeNum):
            if (i != 0 and i != data.nodeNum - 1 and i != j and data.arcs[i, j] == 1):
                expr.clear()

# constraint 3
for k in range(data.vehicleNum):
    expr = LinExpr(0)
    for j in range(1, data.nodeNum): # 需要时刻注意不能有 i = j 的情况出现
        if (data.arcs[0, j] == 1):
            expr.addTerms(1.0, x[0, j, k])
    model.addConstr(expr == 1.0, 'c3')
    expr.clear()

# constraint 4
for k in range(data.vehicleNum):
    for h in range(1, data.nodeNum - 1):
        expr1 = LinExpr(0)
        expr2 = LinExpr(0)
        for i in range(data.nodeNum):
            if (h != i and data.arcs[i, h] == 1):
                expr1.addTerms(1, x[i, h, k])

        for j in range(data.nodeNum):
            if (h != j and data.arcs[h, j] == 1):
                expr2.addTerms(1, x[h, j, k])

        model.addConstr(expr1 == expr2, 'c4')
        expr1.clear()
        expr2.clear()

# constraint 5
for k in range(data.vehicleNum):
    expr = LinExpr(0)
    for i in range(data.nodeNum - 1):
        if (data.arcs[i, data.nodeNum - 1] == 1):
            expr.addTerms(1, x[i, data.nodeNum - 1, k])
    model.addConstr(expr == 1, 'c5')
    expr.clear()

# constraint 6
big_M = 0
for i in range(data.nodeNum):
    for j in range(data.nodeNum):
        big_M = max(data.dueTime[i] + data.disMatrix[i][j] - data.readyTime[j], big_M)

for k in range(data.vehicleNum):
    for i in range(data.nodeNum):
        for j in range(data.nodeNum):
            if (i != j and data.arcs[i, j] == 1):
                model.addConstr(s[i, k] + data.disMatrix[i][j] - s[j, k] <= big_M - big_M * x[i, j, k], 'c6')

# model.setParam('MIPGap', 0)
model.optimize()

print('\n\n----- optimal value -----')
print(model.ObjVal)

edge_list = []
for key in x.keys():
    if (x[key].VarName, ' = ', x[key].x):
        arc = (str(key[0]), str(key[1]))
        edge_list.append(arc)

nodes_col['0'] = 'red'
nodes_col[str(data.nodeNum - 1)] = 'red'
plt.rcParams['figure.figsize'] = (15, 15)
nx.draw(Graph
        , pos = pos_location
        , node_size = 50
        , node_color = nodes_col.values()
        , font_size = 15
        , font_famiy = 'arial'
        , edgelist = edge_list
        )
fig_name = 'network_' + str(customerNum) + '_1000.jpg'
plt.savefig(fig_name, dpi = 600)
plt.show()


# Node Class
class Node:
    def __init__(self):
        self.local_LB = 0
        self.local_UB = np.inf
        self.x_sol = {}
        self.x_int_sol = {}
        self.branch_var_list = {}
        self.model = None
        self.cnt = None
        self.is_integer = False
        self.var_LB = {}
        self.var_UB = {}

    def deepcopy_node(node):
        new_node = None
        new_node.local_LB = 0
        new_node.local_UB = np.inf
        new_node.x_sol = copy.deepcopy(node.x_sol)
        new_node.x_int_sol = copy.deepcopy(node.x_sol)
        new_node.branch_var_list = []
        new_node.model = node.model.copy()
        new_node.cnt = node.cnt
        new_node.is_integer = node.is_integer

        return new_node

# Branch and Cut framework
def Branch_and_Cut(VRPTW_model, x_var, summary_interval):
    Relax_VRPTW_model = VRPTW_model.relax()
    # initialize the initial node
    Relax_VRPTW_model.optimize()
    global_UB = np.inf
    global_LB = Relax_VRPTW_model.ObjVal
    eps = 1e-6
    incumbent_node = None
    Gap = np.inf
    feasible_sol_cnt = 0

    # initialize the cuts poo, this dict aims to store all the cuts generated during branch and bound procedure
    Cuts_pool = {}
    Cuts_LHS = {}
    Cut_cnt = 0

    '''
        Branch and Cut starts
    '''

    #create initial node
    Queue = []
    node = Node()
    node.local_LB = global_LB
    node.local_UB = np.inf
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

        # check whether the current node is integer and execute prune step
        '''
            is_integer : mark whether the current solution is integer solution
            Is_Pruned : mark whether the current solution is pruned
        '''
        is_integer = True
        Is_Pruned = False
        if (Solution_status == 2):
            for var in current_node.model.getVars():
                if (var.VarName.startswith('x')):
                    current_node.x_sol[var.varName] = var.x
                    # record the branchable variable
                    if (abs(round(var.x, 0) - var.x) >= eps):
                        is_integer = False

            '''
                Cuts Generation
            '''
            # cut generation
            temp_cut_cnt = 0
            if (is_integer == False):
                # generate cuts
                # generate at most 5 cuts on each node
                customer_set = list(range(data.nodeNum))[1: -1] # 去掉了两个depot点

                while (temp_cut_cnt <= 5):
                    sample_num = random.choice(customer_set[3:])
                    selected_customer_set = random.sample(customer_set, sample_num)
                    estimated_veh_num = 0
                    total_demand = 0
                    for customer in selected_customer_set:
                        total_demand += data.demand[customer]
                    estimated_veh_num = math.ceil(total_demand / data.capacity)

                    current_node.model._vars = x_var
                    # create cut
                    cut_lhs = LinExpr()
                    for key in x_var.keys():
                        key_org = key[0]
                        key_des = key[1]
                        key_vehicle = key[2]
                        if (key_org not in selected_customer_set and key_des in selected_customer_set):
                            var_name = 'x_' + str(key_org) + '_' + str(key_des) + '_' + str(key_vehicle)
                            cut_lhs.addTerms(1, current_node.model.getVarByName(var_name))
                    Cut_cnt += 1
                    temp_cut_cnt += 1
                    cut_name = 'Cut_' + str(Cut_cnt)
                    Cuts_pool[cut_name] = current_node.model.addConstr(cut_lhs >= estimated_veh_num, name = cut_name)
                    Cuts_LHS[cut_name] = cut_lhs
                    Cuts_LHS[cut_name] = cut_lhs

                # lazy upload
                current_node.model.update()

            '''
                Cuts Generation ends
            '''

            # solve the added cut model
            current_node.model.optimize()
            is_integer = True
            if (current_node.model.Status == 2):
                for var in current_node.model.getVars():
                    if (var.VarName.startswith('x')):
                        current_node.x_sol[var.varName] = copy.deepcopy(current_node.model.getVarByName(var.VarName).x)
                        if (abs(round(var.x, 0) - var.x) >= eps):
                            is_integer = False
                            current_node.branch_var_list.append(var.VarName)
            else:
                continue

            if (is_integer == True):
                feasible_sol_cnt += 1
                current_node.is_integer = True
                current_node.local_LB = current_node.model.ObjVal
                current_node.local_UB = current_node.model.ObjVal
                if (current_node.local_UB < global_UB):
                    global_UB = current_node.local_UB
                    incumbent_node = Node.deepcopy_node(current_node)

            if (is_integer == False):
                # For integer solution node, update the LB and UB also
                current_node.is_integer = False
                current_node.local_UB = global_UB
                current_node.local_LB = current_node.model.ObjVal

            '''
                PRUNE step
            '''
            # prune by optimality
            if (is_integer == True):
                Is_Pruned = True

            # prune by bound
            if (is_integer == False and current_node.local_LB > global_UB):
                Is_Pruned = True

            Gap = round(100 * (global_UB - global_LB) / global_LB, 2)

        elif (Solution_status != 1):
            # the current node is infeasible or unbounded
            is_integer = False

            '''
                PRUNE step
            '''
            # prune by infeasibility
            Is_Pruned = True

            continue

        '''
            BRANCH STEP
        '''
        if (Is_Pruned == False):
            # select the branch variable: choose the value which is closest to 0.5
            branch_var_name = None

            min_diff = 100
            for var_name in current_node.branch_var_list:
                if (abs(current_node.x_sol[var_name] - 0.5) < min_diff):
                    branch_var_name = var_name
                    min_diff = abs(current_node.x_sol[var_name] - 0.5)

            if (cnt % summary_interval == 0):
                print('Branch var name: ', branch_var_name, '\t, branch var value: ', current_node.x_sol[branch_var_name])
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

            # update the global LB, explore all the leaf nodes
            temp_global_LB = np.inf
            for node in Queue:
                node.model.optimize()
                if (node.model.status == 2):
                    if (node.model.ObjVal <= temp_global_LB and node.model.ObjVal < global_UB):
                        temp_global_LB = node.model.ObjVal

            global_LB = temp_global_LB
            Global_UB_change.append(global_UB)
            Global_LB_change.append(global_LB)

        if (cnt % summary_interval == 0):
            print('\n\n====================')
            print('Queue length: ', len(Queue))
            print('\n --------------- \n', cut, 'UB = ', global_UB, 'LB = ', global_LB, 'Gap = ', Gap, '%', 'feasible_sol_cnt : ', feasible_sol_cnt)
            print('Cut pool size: ', len(Cuts_pool))
            NAME = list(Cuts_LHS.keys())[-1]
            print('RHS: ', estimated_veh_num)
            print('Cons Num: ', current_node.model.NumConstrs)

    # all the nodes are explored, update the LB and UB
    incumbent_node.model.optimize()
    global_UB = incumbent_node.model.ObjVal
    global_LB = global_UB
    Gap = round(100 * (global_UB - global_LB) / global_LB, 2)
    Global_UB_change.append(global_UB)
    Global_LB_change.append(global_LB)

    print('\n\n\n\n')
    print('-------------------------------')
    print('   Branch and Cut terminates   ')
    print('     Optimal solution found    ')
    print('-------------------------------')
    print('\n Inter cnt = ', cnt, '\n\n')
    print('\n Final Gap = ', Gap, '% \n\n')
    print(' ----- Optimal Solution ----- ')

    for key in incumbent_node.x_sol.keys():
        if (incumbent_node.x_sol[key] > 0):
            print(key, ' = ', incumbent_node.x_sol[key])
    print('\n Optimal Obj: ', global_LB)

    return incumbent_node, Gap, Global_UB_change, Global_LB_change


# Branch and Cut Solve the IP model
incumbent_node, Gap, Global_UB_change, Global_LB_change = Branch_and_Cut(model, x_var, summary_interval = 100)

for key in incumbent_node.x_sol.keys():
    if (incumbent_node.x_sol[key] > 0):
        print(key, ' = ', incumbent_node.x_sol[key])

# plot the result
font_dict = {
    'family': 'Arial',
    'style': 'oblique',
    'weight': 'normal',
    'color': 'green',
    'size': 20
}

plt.rcParams['figure.figsize'] = (12.0, 8.0)
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 16

x_cor = range(1, len(Global_LB_change) + 1)
plt.plot(x_cor, Global_LB_change, label = 'LB')
plt.plot(x_cor, Global_UB_change, label = 'UB')
plt.legend()
plt.xlabel('Iteration', fontdict = font_dict)
plt.ylabel('Bounds update', fontdict = font_dict)
plt.title('VRPTW (c101-10): Bounds update during branch and cut procedure \n', fontsize = 23)
plt.savefig('BnC_Bound_updates_VRPTW_c101_60.eps')
plt.savefig('BnC_Bound_updates_VRPTW_c101_60.pdf')
plt.show()

print('hello world')