import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import copy
import re
import math
import itertools

class Data:
    customerNum = 0;
    nodeNum = 0;
    vehicleNum = 0;
    capacity = 0;
    cor_X = [];
    cor_Y = [];
    demand = [];
    serviceTime = [];
    readyTime = [];
    dueTime = [];
    disMatrix = [];

def readData(data, path, customerNum):
