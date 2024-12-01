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
