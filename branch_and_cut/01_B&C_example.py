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