import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import copy
import re
import math
import itertools

# 1 readData
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
    data.readyTime.append(data.dueTime[0])
    data.dueTime.append(data.dueTime[0])
    data.serviceTime.append(data.serviceTime[0])

    # compute the distance matrix
    data.disMatrix = [([0] * data.nodeNum) for p in range(data.nodeNum)]
    for i in range(0, data.nodeNum):
        for j in range(0, data.nodeNum):
            temp = (data.cor_X[i] - data.cor_X[j])**2 + (data.cor_Y[i] - data.cor_Y[j])**2
            data.disMatrix[i][j] = math.sqrt(temp)
            # if (i == j):
            #     data.disMatrix[i][j] = 0
            #     print('%6.2f' % (math.sqrt(temp)), end = '')
            temp = 0
    return data

def printData(data, customerNum):
    print('下面打印数据\n')
    print('vehicle number = %4d' % data.vehicleNum)
    print('vehicle capacity = %4d' % data.capacity)
    for i in range(len(data.demand)):
        print('{0}\t{1}\t{2}\t{3}'.format(data.demand[i], data.readyTime[i], data.dueTime[i], data.serviceTime[i]))

    print('----------距离矩阵----------\n')
    for i in range(data.nodeNum):
        for j in range(data.nodeNum):
            # print('%d %d' % (i, j))
            print('%6.2f' % (data.disMatrix[i][j]), end = '')
        print()

# reading data
data = Data()
prth = ''
customerNum = 100
readData(data, path, customerNum)
printData(data, customerNum)


# 构建网络图
Graph = nx.DiGraph
cnt = 0
pos_location = {}
nodes_col = {}
for i in range(data.nodeNum):
    X_coor = data.cor_X[i]
    Y_coor = data.cor_Y[i]
    name = str(i)
    nodes_col[name] = 'gray'
    node_type = 'customer'
    if (i == 0):
        node_type = 'depot'
    Graph.add_node(name
                   , ID = i
                   , node_type = node_type
                   , time_window = (data.readyTime[i], data.dueTime)
                   , arrive_time = 10000
                   , demand = data.demand
                   , serviceTime = data.serviceTime
                   , x_coor = X_coor
                   , y_coor = Y_coor
                   , min_dis = 0
                   , previous_node = None)

    pos_location[name] = (X_coor, Y_coor)

# add edges into the graph
for i in range(data.nodeNum):
    for j in range(data.nodeNum):
        if (i == j or (i == 0 and j == data.nodeNum - 1) or (j == 0 and i == data.nodeNum - 1)):
            pass
        else:
            Graph.add_edge(str(i), str(j)
                           , travelTime=data.disMatrix[i][j]
                           , length=data.disMatrix[i][j])
# 画图
# plt.rcParams['figure.figsize'] = (0.6 * trip_num, trip_num)
nodes_col['0'] = 'red'
nodes_col[str(data.nodeNum - 1)] = 'red'
plc.rcParams['figure.figsize'] = (10, 10)
nx.draw(Graph
        , pos = pos_location
        , with_labels = True
        , node_size = 200
        , node_color = nodes_col.values()
        , font_size = 15
        , font_family = 'arial'
        , edge_color = 'grey'
        )
fig_name = 'network_' + str(customerNum) + '.jpg'
plt.savefig(fig_name, dpi = 600)
plt.show()

# Labelling Algorithm
class Label:
    path = []
    time = 0
    dis = 0

def labelling_SPPRC(Graph, org, des):
    # initial Queue
    Queue = []
    # create initial label
    label = Label()
    label.path = [org]
    label.dis = 0
    label.time = 0
    Queue.append(label)
    Paths = {}
    cnt = 0
    while (len(Queue) > 0):
        cnt += 1
        current_path = Queue[0]
        Queue.remove(current_path)
        # extend the label
        last_node = current_path.path[-1]
        for child in Graph.successor(last_node):
            extended_path = copy.deepcopy(current_path)
            arc_key = (last_node, child)
            # justify whether the extension is feasible
            arrive_time = current_path.time + Graph.edges[arc_key]['travelTime']
            time_window = Graph.nodes[child]['time_window']
            if ((chile not in extended_path.path) and arrive_time >= time_window[0] and arrive_time <= time_window[1]):
                # the extension is feasible
                # print('extension is feasible', 'arc: ', arc_key)
                extended_path.path.append(child)
                extended_path.dis += Graph.edges[arc_key]['length']
                extended_path.time += Graph.edges[arc_key]['travelTime']
                Queue.append(extended_path)
                print('extended_path: ', extended_path.path)
            else:
                pass
                # print('extended_path: ', extended_path.path)
        Paths[cnt] = current_path

        # dominate step
        '''
        Add dominate rule function
        '''
        Queue, Paths = dominant(Queue, Paths)

    # filtering Paths, only keep solutions from org to des, delete other paths
    PathsCopy = copy.deepcopy(Paths)
    for key in PathsCopy.keys():
        if (Paths[key].path[-1] != des):
            Paths.pop(key)

    # choose optimal solution
    opt_path = {}
    min_distance = 10000000
    for key in Paths.keys():
        if (Paths[key].dis < min_distance):
            min_distance = Paths[key].dis
            opt_path['1'] = Paths[key]

    return Graph, Queue, Paths, PathsCopy, opt_path

# dominate rule
def dominant(Queue, Paths):
    QueueCopy = copy.deepcopy(Queue)
    PathsCopy = copy.deepcopy(Paths)

    # dominate Queue
    for label in QueueCopy:
        for another_label in Queue:
            if (label.path[-1] == another_label.path[-1] and label.time < another_label.time and label.dis < another_label.dis):
                Queue.remove(another_label)
                print('dominated path (Q): ', another_label.path)

    # dominate Paths
    for key_1 in PathsCopy.keys():
        for key_2 in PathsCopy.keys():
            if (PathsCopy[key_1].path[-1] == athsCopy[key_2].path[-1]
                and PathsCopy[key_1].time < PathsCopy[key_2].time
                and PathsCopy[key_1].dis < PathsCopy[key_2].dis
                and (key_2 in Paths.keys())):
                Paths.pop(key_2)
                print('dominated path (P): ', PathsCopy[key_1].path)

    return Queue, Paths

# 算例测试
org = '0'
des = str(data.nodeNum - 1)
Graph, Queue, Paths, PathsCopy, opt_path = labelling_SPPRC(Graph, org, des)

for key in Paths.keys():
    print(Paths[key].path)

print('optimal path: ', opt_path['1'].path)
print('optimal path (distance): ', opt_path['1'].dis)
print('optimal path (time): ', opt_path['1'].time)