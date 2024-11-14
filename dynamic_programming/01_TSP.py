import copy
import re
import math
import itertools

Nodes = [1, 2, 3, 4]

nodeNum = len(Nodes)

dis_matrix = [[0, 8, 12, 17]
             , [4, 0, 10, 9]
             , [7, 14, 0, 13]
             , [9, 7, 11, 0]]

def TSP_Dynamic_Programming(Nodes, dis_matrix):
    Label_set = {}
    nodeNum = len(Nodes)
