"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 机组排班优化问题- Gurobi Python接口代码实现
author: 王基光
date:2022-10-11
"""

# coding: utf-8
# !/usr/bin/env python
# coding: utf-8
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gurobipy import *
import csv
import copy
import random

# 设置输入参数



# 定义员工类
class Crew:

    def __init__(self):
        self.EmpNo = None
        self.is_Captain = False
        self.is_FirstOfficer = False
        self.is_Deadhead = False
        self.Base = "NKX"
        self.DutyCostPerHour = None
        self.ParingCostPerHour = None


# 定义航班类
class Flight:

    def __init__(self):
        self.FltNum = None
        self.DptrDate = None
        self.DptrTime = None
        self.DptrStn = "NKX"
        self.ArrvDate = None
        self.ArrvTime = None
        self.ArrvStn = "NKX"
        self.FltTime = None
        self.Comp = "C1F1"


# 读取数据
def read_data(file_name_1, file_name_2, crew_select_interval, flight_select_interval):
    crew_list = []
    crew_base = []
    with open(file_name_1, 'r') as f:
        reader1 = csv.reader(f)
        headings = next(reader1)
        cnt = 0
        for row in reader1:
            cnt += 1
            if (cnt % crew_select_interval == 0):
                crew = Crew()
                crew.EmpNo = row[0]
                if row[1] == 'Y':
                    crew.is_Captain = True
                if row[2] == 'Y':
                    crew.is_FirstOfficer = True
                if row[3] == 'Y':
                    crew.is_Deadhead = True
                crew.Base = row[4]
                crew_base.append(crew.Base)
                crew.DutyCostPerHour = row[5]
                crew.ParingCostPerHour = row[6]
                crew_list.append(crew)

    flight_list = []
    with open(file_name_2, 'r') as f:
        reader2 = csv.reader(f)
        headings = next(reader2)
        cnt = 0
        for row in reader2:
            cnt += 1
            if (cnt % flight_select_interval == 0):
                flight = Flight()
                flight.FltNum = row[0] + '-' + row[1].split('/')[1]
                flight.DptrDate = row[1]
                flight.DptrTime = int(row[1].split("/")[1]) * 1440 + int(row[2].split(":")[0]) * 60 + int(
                    row[2].split(":")[1])
                flight.DptrStn = row[3]
                flight.ArrvDate = row[4]
                flight.ArrvTime = int(row[4].split("/")[1]) * 1440 + int(row[5].split(":")[0]) * 60 + int(
                    row[5].split(":")[1])
                flight.ArrvStn = row[6]
                flight.FltTime = flight.ArrvTime - flight.DptrTime
                flight.Comp = row[7]
                flight_list.append(flight)

    # 随机筛选一定数量的航班和机组人员
    # flight_list_selected = random.sample(flight_list, flight_num)

    # 根据Base的数量生成虚拟的航班号
    crew_base = list(set(crew_base))
    for i in range(len(crew_base)):
        flight = Flight()
        flight.FltNum = crew_base[i]
        flight.DptrTime = 999999999999
        flight.DptrStn = crew_base[i]
        flight.ArrvTime = 0
        flight.ArrvStn = crew_base[i]
        flight.FltTime = 0
        flight_list.insert(0, flight)

    print('Selected flight :', len(flight_list))
    print('Selected crew :', len(crew_list))
    return crew_list, flight_list, crew_base


file_name_1 = "机组排班Data A-Crew.csv"
file_name_2 = "机组排班Data A-Flight.csv"

crew_select_interval = 1
flight_select_interval = 1
max_arc_num = 7000

crew_list, flight_list, crew_base = read_data(file_name_1, file_name_2, crew_select_interval,
                                              flight_select_interval)  # 读取数据

type(crew_list[0].DutyCostPerHour)


# 生成邻接矩阵
def generate_adj_matrix(flight_list, crew_base, max_arc_num, problem_ID):
    """
    参数:
    ----------
        输入: flight list
    ----------
        输出：
        the shareability network of flights
        Example : {(1, 2): 1,
                   (1, 3): 1
                   .....
                   }
    """
    Adj_matrix = {}
    Adj_matrix_hop = {}
    Adj_matrix_hop_bi = {}  # 连接跨天且i的终点是base的集合
    Adj_matrix_hop_nbi = {}  # 连接跨天且i的终点不是base的集合
    arc_num = 0
    for i in range(len(flight_list)):
        for j in range(len(flight_list)):
            if flight_list[i].ArrvStn == flight_list[j].DptrStn:
                if flight_list[i].ArrvTime < flight_list[j].DptrTime:
                    if flight_list[i].FltNum != flight_list[j].FltNum:
                        Adj_matrix[(flight_list[i].FltNum, flight_list[j].FltNum)] = 1

    if (problem_ID == 1 or problem_ID == 2):
        arc_num = len(Adj_matrix)
        while (len(Adj_matrix) > max_arc_num):  # 筛选弧段
            Adj_matrix_copy = copy.deepcopy(Adj_matrix)
            found_diff_day_departure_flight = False
            for key in Adj_matrix_copy.keys():
                if (key in Adj_matrix.keys() and key[0] not in crew_base and key[1] not in crew_base):
                    FltNum_1 = key[0]
                    FltNum_2 = key[1]
                    Flt_1_start_day_ID = (int)(FltNum_1.split('-')[-1])
                    Flt_2_start_day_ID = (int)(FltNum_2.split('-')[-1])
                    if (abs(Flt_1_start_day_ID - Flt_2_start_day_ID) > 1):
                        found_diff_day_departure_flight = True
                        del Adj_matrix[key]
            if (found_diff_day_departure_flight == False):
                """ 没有找到根据出发时间可以删除的弧，那就随机删除 """
                del_arc_ID = (int)(random.random() * len(Adj_matrix))
                if (del_arc_ID <= len(Adj_matrix)):
                    key_list = list(Adj_matrix.keys())
                    deleted_key = key_list[del_arc_ID]
                    if (deleted_key[0] not in crew_base and deleted_key[1] not in crew_base):
                        del Adj_matrix[deleted_key]

    elif (problem_ID == 3):
        pass

    for key in Adj_matrix:
        for i in range(len(crew_base)):
            if key[1].split('-')[-1] > key[0].split('-')[-1]:
                Adj_matrix_hop[key] = Adj_matrix[key]
    for i in range(len(crew_base)):  # 把和虚拟起止点相连的去掉
        for key in list(Adj_matrix_hop.keys()):
            if key[1] == crew_base[i] or key[0] == crew_base[i]:
                del Adj_matrix_hop[key]
                continue

    for i in range(len(crew_base)):
        for key in Adj_matrix_hop:
            for j in range(len(flight_list)):
                if key[0] == flight_list[j].FltNum and flight_list[j].ArrvStn == crew_base[i]:
                    Adj_matrix_hop_bi[key] = Adj_matrix_hop[key]

    Adj_matrix_hop_nbi = Adj_matrix_hop
    for key in list(Adj_matrix_hop_nbi.keys()):
        for i in range(len(crew_base)):
            for j in range(len(flight_list)):
                if key[0] == flight_list[j].FltNum and flight_list[j].ArrvStn == crew_base[i]:
                    del Adj_matrix_hop_nbi[key]
                    continue
    arc_num = len(Adj_matrix)
    print('\n\n ****  Arc Num: {}    ****\n\n'.format(arc_num))
    return Adj_matrix, Adj_matrix_hop, Adj_matrix_hop_bi, Adj_matrix_hop_nbi


problem_ID = 1
Adj_matrix, Adj_matrix_hop, Adj_matrix_hop_bi, Adj_matrix_hop_nbi = generate_adj_matrix(flight_list, crew_base,
                                                                                        max_arc_num, problem_ID)


# 生成员工角色对应的矩阵
def generate_role_matrix(crew_list):
    Role_matrix = [[] for i in range(len(crew_list))]
    for i in range(len(crew_list)):
        if crew_list[i].is_Captain == True:
            Role_matrix[i].append(1)
        else:
            Role_matrix[i].append(0)

        if crew_list[i].is_FirstOfficer == True:
            Role_matrix[i].append(1)
        else:
            Role_matrix[i].append(0)

        if crew_list[i].is_Deadhead == True:
            Role_matrix[i].append(1)
        else:
            Role_matrix[i].append(0)

    return Role_matrix


Role_matrix = generate_role_matrix(crew_list)

flightid = []
for i in range(len(flight_list)):
    flightid.append(flight_list[i].FltNum)

empid = []
for i in range(len(crew_list)):
    empid.append(crew_list[i].EmpNo)
emp1 = []
emp2 = []

for i in range(len(crew_list)):
    if crew_list[i].is_Captain == True:
        emp1.append(crew_list[i].EmpNo)
    if crew_list[i].is_FirstOfficer == True:
        emp2.append(crew_list[i].EmpNo)

flightid = []
for i in range(len(flight_list)):
    flightid.append(flight_list[i].FltNum)

empid = []
for i in range(len(crew_list)):
    empid.append(crew_list[i].EmpNo)
emp1 = []
emp2 = []

emp11 = emp1
emp22 = []
emp33 = []
for i in range(len(crew_list)):
    if crew_list[i].is_Captain == False and crew_list[i].is_FirstOfficer == True:
        emp22.append(crew_list[i].EmpNo)
    if crew_list[i].is_FirstOfficer == True and crew_list[i].is_Captain == True:
        emp33.append(crew_list[i].EmpNo)

for i in range(len(crew_list)):
    if crew_list[i].is_Captain == True:
        emp1.append(crew_list[i].EmpNo)
    if crew_list[i].is_FirstOfficer == True:
        emp2.append(crew_list[i].EmpNo)

resttime = 40  # 设置休息时间
bigM = 10000

# 开始建立模型
model = Model('Airline_Crew_Problem')
x = {}
z = {}
w = {}
# Adj_matrix = {"1,2": 1, "2,2": 1}
# 定义决策变量X  如果航班i和航班j被机组人员r连续执行
for i in flightid:
    for j in flightid:
        if i != j:
            if (i, j) in Adj_matrix:
                for r in empid:
                    name = 'x_' + str(i) + '_' + str(j) + '_' + str(r)
                    x[i, j, r] = model.addVar(0
                                              , 1
                                              , vtype=GRB.BINARY
                                              , name=name)

# 定义决策变量Z  如果机组人员r以角色k的身份执行航班i
for i in flightid:
    for r in empid:
        for k in range(1, 4):
            name = 'z_' + str(i) + '_' + str(r) + '_' + str(k)
            z[i, r, k] = model.addVar(0
                                      , 1
                                      , vtype=GRB.BINARY
                                      , name=name)
# 定义决策变量w ,如果航班i被完全执行
for i in flightid:
    name = 'w_' + str(i)
    w[i] = model.addVar(0
                        , 1
                        , vtype=GRB.BINARY
                        , name=name)

# 更新模型
model.update()

# 定义目标函数：最大化航班完成量
obj = LinExpr(0)
alpha1 = 1
for i in flightid:
    obj.addTerms(alpha1, w[i])
model.setObjective(obj, GRB.MAXIMIZE)
###约束9.7-9.9流平衡
for r in empid:
    lhs = LinExpr(0)
    for j in flightid:
        if j != crew_list[empid.index(r)].Base:
            if (crew_list[empid.index(r)].Base, j) in Adj_matrix:
                lhs.addTerms(1, x[crew_list[empid.index(r)].Base, j, r])
    model.addConstr(lhs <= 1, name='flow_out_' + str(r))  # 航班流出约束9.7
    lhs2 = LinExpr(0)
    for i in flightid:
        if i != crew_list[empid.index(r)].Base:
            if (i, crew_list[empid.index(r)].Base) in Adj_matrix:
                lhs2.addTerms(1, x[i, crew_list[empid.index(r)].Base, r])
    model.addConstr(lhs == lhs2, name='flow_in_' + str(r))  # 航班流入约束9.8

for r in empid:
    for j in flightid:
        if j != crew_list[empid.index(r)].Base:
            expr1 = LinExpr(0)
            expr2 = LinExpr(0)
            for i in flightid:
                # if i != crew_list[empid.index(r)].Base:
                if (j != i):
                    if (i, j) in Adj_matrix:
                        expr1.addTerms(1, x[i, j, r])
            for k in flightid:
                if (j != k):
                    if (j, k) in Adj_matrix:
                        # print(k)
                        expr2.addTerms(1, x[j, k, r])
            model.addConstr(expr1 == expr2, name='flow_conservation_' + str(j) + "_" + str(r))  # 航班流入流出平衡约束9.9
            expr1.clear()
            expr2.clear()

for r in empid:
    for i in flightid:
        expr1 = LinExpr(0)
        expr2 = LinExpr(0)
        for j in flightid:
            if i != j:
                if (i, j) in Adj_matrix:
                    expr1.addTerms(1, x[i, j, r])
        for k in range(1, 4):
            expr2.addTerms(1, z[i, r, k])
        model.addConstr(expr1 == expr2,
                        name="zxcons_" + str(i) + "_" + str(r))  # 约束9.10：决策变量X和决策变量Z的联系约束：保证被选择的机组人员在一次航班中必须担任且只担任一种角

for r in empid:
    for k in range(1, 4):
        for i in flightid:
            # expr1.addTerms(1,z[i,r,k])
            model.addConstr(z[i, r, k] <= int(Role_matrix[empid.index(r)][k - 1]),
                            name="empcons_" + str(r) + "_" + str(i) + "_" + str(k))  # 约束9.11保证了机组人员担任角色的条件

for i in flightid:
    expr1 = LinExpr(0)
    expr2 = LinExpr(0)
    for r in empid:
        expr1.addTerms(1, z[i, r, 1])

        expr2.addTerms(1, z[i, r, 2])

    model.addConstr(expr1 == w[i], name="emp1cons_" + str(i))  # 约束9.13：判断航班是否具备资

model.addConstr(expr2 == w[i], name="emp2cons_" + str(i))  # 约束9.14：判断航班是否具备资



# 破除对称：有效不等式，提升计算速度
for rid in range(1, len(emp11)):
    expr1 = LinExpr(0)
    expr2 = LinExpr(0)
    for i in flightid:
        for k in range(1, 4):
            if i != crew_list[empid.index(empid[rid])].Base:
                expr1.addTerms(1, z[i, empid[rid], k])

                expr2.addTerms(1, z[i, empid[rid - 1], k])

    model.addConstr(expr1 <= expr2, name="emp1cons_" + str(empid[rid]) + "_" + str(k))

# 破除对称性：有效不等式，提升计算速度
for rid in range(1, len(emp22)):
    expr1 = LinExpr(0)
    expr2 = LinExpr(0)
    for i in flightid:
        for k in range(1, 4):
            if i != crew_list[empid.index(empid[rid])].Base:
                expr1.addTerms(1, z[i, empid[rid], k])

                expr2.addTerms(1, z[i, empid[rid - 1], k])

    model.addConstr(expr1 <= expr2, name="emp1cons_" + str(empid[rid]) + "_" + str(k))

# 破除对称性：有效不等式，提升计算速度
for rid in range(1, len(emp33)):
    expr1 = LinExpr(0)
    expr2 = LinExpr(0)
    for i in flightid:
        for k in range(1, 4):
            if i != crew_list[empid.index(empid[rid])].Base:
                expr1.addTerms(1, z[i, empid[rid], k])
                expr2.addTerms(1, z[i, empid[rid - 1], k])

    model.addConstr(expr1 <= expr2, name="emp1cons_" + str(empid[rid]) + "_" + str(k))

# 求解模型
# model.setParam('Cuts', 0)
model.optimize()

# 打印求解结果
print("\n\n-----optimal value-----")
print(model.ObjVal)
