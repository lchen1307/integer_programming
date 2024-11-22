"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: M-M-PDP问题- COPT Python接口代码实现
author: 杉数科技
date:2022-10-11
institute: 杉数科技
"""

from coptpy import *
import time
import copy
import math
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


class Data(object):
    def __init__(self):
        self.customer_num = 0
        self.node_num = 0
        self.vehicle_num = 0
        self.coor_X = {}
        self.coor_Y = {}
        self.demand = {}
        self.pickdemand = {}
        self.service_time = {}
        self.ready_time = {}
        self.due_time = {}
        self.dis_matrix = {}
        self.capacity = 0
        self.arcs = {}

    def read_data(self, file_name, customer_num, vehicle_num):
        data = Data()
        np.random.seed(0)
        data.customer_num = customer_num
        data.node_num = customer_num
        f = open(file_name, "r")
        lines = f.readlines()
        cnt = 0
        for line in lines:
            cnt += 1
            if cnt == 5:
                line = line[:-1].strip()
                str_arr = re.split(r" +", line)
                data.vehicle_num = vehicle_num
                data.capacity = int(str_arr[1])

            elif (cnt >= 10 and cnt <= 10 + data.node_num - 1):
                line = line[:-1].strip()
                str_arr = re.split(r" +", line)
                node_ID = int(str_arr[0])
                data.coor_X[node_ID] = int(str_arr[1])
                data.coor_Y[node_ID] = int(str_arr[2])
                if np.random.random() > 0.5:

                    data.demand[node_ID] = int(str_arr[3])
                else:
                    data.demand[node_ID] = -int(str_arr[3])

                data.ready_time[node_ID] = int(str_arr[4])
                data.due_time[node_ID] = int(str_arr[5])
                data.service_time[node_ID] = int(str_arr[6])

        for i in range(data.node_num):
            for j in range(data.node_num):
                temp = (data.coor_X[i] - data.coor_X[j]) ** 2 + (data.coor_Y[i] - data.coor_Y[j]) ** 2
                data.dis_matrix[i, j] = round(math.sqrt(temp), 1)
                if i != j:
                    data.arcs[i, j] = 1
                else:
                    data.arcs[i, j] = 0
        return data

    def printData(self, data):
        print("------数据集 信息--------------\n")
        print("车辆数 = %4d" % data.vehicle_num)
        print("顾客数 = %4d" % data.customer_num)
        print("节点数 = %4d" % data.node_num)
        for i in data.demand.keys():
            # print("%10.0f" %(data.demand[i]),"%10.0f"%data.pickdemand[i], "%10.0f"%data.ready_time[i], "%10.0f"%data.due_time[i],"%10.0f"%data.service_time[i])

            print("%10.0f" % (data.demand[i]), "%10.0f" % data.ready_time[i],
                  "%10.0f" % data.due_time[i], "%10.0f" % data.service_time[i])
        print("-------距离矩阵-------\n")
        for i in range(data.node_num):
            for j in range(data.node_num):
                print("%6.2f" % (data.dis_matrix[i, j]), end=" ")


# 实例化一个作为参数传入模型的callback类
class CoptCallback(CallbackBase): # x 为tupledict类
    def __init__(self, x, num_nodes, num_vehicles):
        super().__init__()
        self.x = x
        self.num_nodes = num_nodes
        self.num_vehicles = num_vehicles

    def callback(self):
        if self.where() == COPT.CBCONTEXT_MIPSOL:
            sol = self.getSolution(self.x)

            # 找到所有与depot直接或间接相连的点
            isVisited = [0]
            for i in range(1, self.num_nodes):
                for k in range(self.num_vehicles):
                    if i not in isVisited and sol[0, i, k] > 0.8:
                        current_node = i
                        isVisited.append(current_node)
                        flag = True
                        while flag:
                            flag = False
                            for j in range(1, self.num_nodes):
                                if j not in isVisited and sol[current_node, j, k] > 0.8:
                                    current_node = j
                                    isVisited.append(current_node)
                                    flag = True
                                    break

                                    # 找到剩余组成回路的点，进行
            if len(isVisited) != self.num_nodes:
                S = list(set(range(self.num_nodes)) - set(isVisited))
                expr = LinExpr()
                for i in S:
                    for j in S:
                        for k in range(self.num_vehicles):
                            if i != j:
                                expr.addTerm(self.x[i, j, k], 1)
                self.addLazyConstr(expr <= len(S) - 1)

if __name__ == '__main__':
    stime = time.time()
    file_path = "c101.txt"
    data = Data()
    customer_num = 20  # 设置需求数量
    vehicle_num = 5  # 设置车辆数量
    data = data.read_data(file_name=file_path, customer_num=customer_num, vehicle_num=vehicle_num)  # 读取数据
    data.capacity = 50  # 设置车辆载荷
    print(data.demand)
    data.printData(data)

    env = Envr()
    m = env.createModel("PDVRP-COPT")

    x = tupledict()  # 设置决策变量x
    for i in range(data.node_num):
        for j in range(data.node_num):
            for k in range(vehicle_num):
                if i != j:
                    x[i, j, k] = m.addVar(obj=data.dis_matrix[i, j], vtype=COPT.BINARY,
                                              name='x_' + str(i) + '_' + str(j) + '_' + str(k))  # 设置目标函数，默认为最小化
    y = {}  # 设置决策变量y
    for i in range(data.node_num):
        for j in range(data.node_num):
            if i != j:
                y[i, j] = m.addVar(lb=0, vtype=COPT.CONTINUOUS, name='y_' + str(i) + '_' + str(j))

    for i in range(1, data.node_num):
        expr1 = LinExpr(0)
        for j in range(data.node_num):
            for k in range(vehicle_num):
                if i != j:
                    expr1.addTerm(x[i, j, k], 1)
        m.addConstr(expr1 == 1, name='cons1')

    for i in range(data.node_num):
        for k in range(vehicle_num):
            expr2 = LinExpr(0)
            for j in range(data.node_num):
                if i != j:
                    expr2.addTerm(x[i, j, k], 1)
                    expr2.addTerm(x[j, i, k], -1)
            m.addConstr(expr2 == 0, name='cons2')

    for i in range(data.node_num):
        for k in range(vehicle_num):
            expr3 = LinExpr(0)
            for j in range(data.node_num):
                if i != j:
                    expr3.addTerm(x[i, j, k], 1)
            m.addConstr(expr3 <= 1, name="cons3")

    for i in range(data.node_num):
        for j in range(data.node_num):
            if i != j:
                expr4 = LinExpr(0)
                expr4.addTerm(y[i, j], 1)
                for k in range(vehicle_num):
                    expr4.addTerm(x[i, j, k], -data.capacity)
                m.addConstr(expr4 <= 0, name='cons4')

    for i in range(1, data.node_num):
        expr5 = LinExpr(0)
        for j in range(data.node_num):
            if i != j:
                expr5.addTerm(y[i, j], -1)
                expr5.addTerm(y[j, i], 1)
        m.addConstr(expr5 == data.demand[i], name='cons5')


    cb = CoptCallback(x, data.node_num, vehicle_num)
    m.setCallback(cb, COPT.CBCONTEXT_MIPSOL)

    m.Param.lazyConstraints = 1
    m.solve()
    Slist = []
    S = []
    S.append(0)
    for i in range(data.node_num):
        for j in range(data.node_num):
            for k in range(vehicle_num):
                if i != j and x[i, j, k].x > 0.1:
                    print(x[i, j, k].getName())
    for i in range(1, data.node_num):
        for k in range(vehicle_num):
            if i not in S and x[0, i, k].x > 1 - 1e-3:
                print("[0-" + str(i), end='')
                currNode = i
                S.append(currNode)
                flag = True
                while flag:
                    flag = False
                    for j in range(1, data.node_num):
                        if j not in S and x[currNode, j, k].x > 0.8:
                            print("-" + str(j), end='')
                            currNode = j
                            S.append(currNode)
                            flag = True
                            break
                print("-0]")
                Slist.append(S)
                S = [0]

    Graph = nx.DiGraph()
    nodes_name = [0]
    cor_xy = [[data.coor_X[0], data.coor_Y[0]]]
    edges = []
    for route in Slist:
        edge = []
        edges.append([route[0], route[1]])
        for i in route[1:]:
            nodes_name.append(i)
            cor_xy.append([data.coor_X[i], data.coor_Y[i]])
            edge.append(i)
            if len(edge) == 2:
                edges.append(copy.deepcopy(edge))
                edge.pop(0)
        edge.append(0)
        edges.append(edge)
    Graph.add_nodes_from(nodes_name)
    Graph.add_edges_from(edges)

    pos_location = {nodes_name[i]: x for i, x in enumerate(cor_xy)}
    nodes_color_dict = ['r'] + ['gray'] * (data.node_num - 1)
    colorpool = ["turquoise", "slateblue", "cyan", "peru", "gold"]
    edge_color_dict0 = []
    for edge in Graph.edges():
        for typei in range(len(Slist)):
            if edge[0] in Slist[typei] and edge[1] in Slist[typei]:
                edge_color_dict0.append(colorpool[typei])

    e_labels = {}
    for edge0 in edges:
        e_labels[(edge0[0], edge0[1])] = data.dis_matrix[edge0[0], edge0[1]]
    nx.draw_networkx(Graph, pos_location, node_size=200, node_color=nodes_color_dict, edge_color=edge_color_dict0,
                     labels=None,
                     font_size=8)
    # nx.draw_networkx_edge_labels(Graph, pos=pos_location, edge_labels=e_labels,font_size=3)
    plt.savefig("figpdp40.pdf", dpi=800)
    plt.legend()
    plt.show()
