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
