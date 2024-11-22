"""
@filename: VRP.py
@author: Long Chen
@time: 2024-11-21
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import copy
import re
import math
import itertools

class Data:
    customerNum = 0
    nodeNum = 0
    vehicleNum = 0
    capacity = 0
    cor_X = []
    cor_Y = []
    demand = []
    serviceTime = []
    readyTime = []
    dueTime = []
    disMatrix = [[]]

def readData(data, path, customerNum):
    data.customerNum = customerNum
    data.nodeNum = customerNum + 1
    f = open(path, 'r')
    lines = f.readlines()
    count = 0

    # read the info
    for line in lines:
        count = count + 1
        if (count == 5):
            line = line[:-1].strip()
            str = re.split(r" +", line)
            data.vehicleNum = int(str[0])
            data.capacity = float(str[1])
        elif (count >= 10 and count <= 10 + customerNum):
            line = line[:-1]
            str = re.split(r" +", line)
            data.cor_X.append(float(str[2]))
            data.cor_Y.append(float(str[3]))
            data.demand.apend(float(str[4]))
            data.readyTime.append(float(str[5]))
            data.dueTime.append(float(str[6]))
            data.serviceTime.append(float(str[7]))

    # compute the distance matrix
    data.disMatrix = [([0] * data.nodeNum) for p in range(data.nodeNum)] # 初始化距离矩阵的维度，防止浅拷贝
    for i in range(0, data.nodeNum):
        for j in range(0, data.nodeNum):
            temp = (data.cor_X[i] - data.cor_X[j])**2 + (data.cor_Y[i] - data.cor_Y[j])**2
            data.disMatrix[i][j] = round(math.sqrt(temp), 1)
            if (i == j):
                data.disMatrix[i][j] = 0
                print('%6.2f' % (math.sqrt(temp)), end = '')
                temp = 0
    return data

def printData(data, customerNum):
    print('下面打印数据\n')
    print('vehicle number = %4d' % data.vehicleNum)
    print('vehicle capacity = %4d' % data.capacity)
    for i in range(len(data.demand)):
        print('{0}\t{1}\t{2}\t{3}'.format(data.demand[i], data.readyTime[i], data.dueTime[i], data.serviceTime[i]))

    print('-----距离矩阵-----\n')
    for i in range(data.nodeNum):
        for j in range(data.nodeNum):
            print('%6.2f' % (data.disMatrix[i][j]), end = '')
        print()

# Read Data
data = Data()
path = 'Solomn标准VRP算例/solomon-100/In/r100.txt'
customerNum = 20
readData(data, path, customerNum)
printData(data, customerNum)

# Build Graph
# 构建有向图对象
Graph = nx.DiGraph
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
                   , ID = i
                   , node_type = node_type
                   , time_window = (data.readyTime[i], data.dueTime[i])
                   , arrive_time = 10000
                   , demand = data.demand
                   , serviceTime = data.serviceTime
                   , x_coor = X_coor
                   , y_coor = Y_coor
                   , min_dis = 0
                   , previous_node = None)

    pos_location[name] = (X_coor, Y_coor)

# add edges into graph
for i in range(data.nodeNum):
    for j in range(data.nodeNum):
        if (i != j):
            Graph.add_edge(str(i), str(j)
                           , travelTime = data.disMatrix[i][j]
                           , length = data.disMatrix[i][j])

# plt.rcParams['figure.figsize'] = (0.6 * trip_num, trip_num)
nodes_col['0'] = 'red'
# nodes_col[str(data.nodeNum - 1)] = 'red'
plt.rcParams['figure.figsize'] = (10, 10)
nx.draw(Graph
        , pos = pos_location
        , with_labels = True
        , node_size = 50
        , node_color = nodes_col.values()
        , font_size = 15
        , font_family = 'arial'
        , edge_color = 'grey'
        , edge_list = []
        , nodelist = nodeList
        )
fig_name = 'network_' + str(customerNum) + '_1000.jpg'
plt.savefig(fig_name, dpi = 600)
plt.show()

# Dynamic Programming
Nodes = list(Graph.nodes())
for i in range(len(Nodes)):
    Nodes[i] = (int)(Nodes[i]) + 1

dis_matrix = np.zeros([len(Nodes), len(Nodes)])
for i in range(len(Nodes)):
    for j in range(len(Nodes)):
        if (i != j):
            key = (str(i), str(j))
            dis_matrix[i][j] = Graph.edges[key]['length']

def TSP_Dynamic_Programming(Nodes, dis_matrix):
    Label_set = {}
    nodeNum = len(Nodes)
    org = 1
    # cycle stage: V, V-1, ..., 2
    for stage_ID in range(nodeNum, 1, -1):
        print('stage: ', stage_ID)
        for i in range(2, nodeNum + 1):
            current_node = i
            left_node_list = copy.deepcopy(Nodes)
            left_node_list.remove(i)
            if (org in left_node_list):
                left_node_list.remove(org)
            left_node_set = set(left_node_list)
            # obtain the all the subset of the left node set
            subset_all = list(map(set, itertools.combinations(left_node_set, nodeNum - stage_ID)))
            # print('current_node: ', current_node, '\t left_node_set: ', left_node_set)
            for subset in subset_all:
                if (len(subset) == 0):
                    key = (stage_ID, current_node, 'None')
                    next_node = org
                    Label_set[key] = [dis_matrix[i - 1][org - 1], next_node]
                else:
                    key = (stage_ID, current_node, str(subset))
                    min_distance = 1000000
                    for temp_next_node in subset:
                        subsub_set = copy.deepcopy(subset)
                        subsub_set.remove(temp_next_node)
                        if (subsub_set == None or len(subsub_set) == 0):
                            subsub_set = 'None'
                        sub_key = (stage_ID + 1, temp_next_node, str(subsub_set))

                        if (sub_key in Label_set.keys()):
                            if (dis_matrix[current_node - 1][temp_next_node - 1] + Label_set[sub_key][0] < min_distance):
                                min_distance = dis_matrix[current_node - 1][temp_next_node - 1] + Label_set[sub_key][0]
                                next_node = temp_next_node
                                Label_set[key] = [min_distance, next_node]

    # stage 1:
    stage_ID = 1
    current_node = org
    subset = set(copy.deepcopy(Nodes))
    subset.remove(org)
    final_key = (stage_ID, current_node, str(subset))
    min_distance = 1000000
    for temp_next_node in subset:
        subsub_set = copy.deepcopy(subset)
        subsub_set.remove(temp_next_node)
        if (subsub_set == None or len(subsub_set) == 0):
            subsub_set = 'None'
        sub_key = (stage_ID + 1, temp_next_node, str(subsub_set))
        if (sub_key in Label_set.keys()):
            if (dis_matrix[current_node - 1][temp_next_node - 1] + Label_set[sub_key][0] < min_distance):
                min_distance = dis_matrix[current_node - 1][temp_next_node - 1] + Label_set[sub_key][0]
                next_node = temp_next_node
                Label_set[final_key] = [min_distance, next_node]

    # get the optimal solution
    opt_route = [org]
    not_visited_node = set(copy.deepcopy(Nodes))
    not_visited_node.remove(org)
    next_node = Label_set[final_key][i]
    while True:
        opt_route.append(next_node)
        if (len(opt_route) == nodeNum + 1):
            break
        current_stage = len(opt_route)
        not_visited_node.remove(next_node)
        if (not_visited_node == None or len(not_visited_node) == 0):
            not_visited_node = 'None'
        next_key = (current_stage, next_node, str(not_visited_node))
        next_node = Label_set[next_key][1]

    opt_dis = Label_set[final_key][0]
    print('objective: ', Label_set[final_key][0])
    print('optimal route: ', opt_route)

    return opt_dis, opt_route

opt_dis, opt_route = TSP_Dynamic_Programming(Nodes, dis_matrix)
print('\n\n ---------- optimal solution ----------\a')
print('objective: ', opt_dis)
print('optimal route: ', opt_route)