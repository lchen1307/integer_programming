"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 配送网络规划问题--Gurobi Python接口代码实现
author: 刘兴禄
date: 2019-10-20
"""

import pandas as pd
from gurobipy import *

'''
定义OD_pair类
'''
class OD_pair(object):
    def __init__(self):
        self.org = -1
        self.des = -1
        self.distance = 0
        self.demand = 0
        self.cost = 0

'''
定义Instance类
'''
class Instance(object):
    def __init__(self):
        self.OD_set = {}
        self.cities = {1:'广东', 2:'广东', 3:'广东', 4:'广东', 5:'广东',
                       6:'湖北', 7:'湖北', 8:'湖北', 9:'湖北', 10:'湖北'}
        self.arc_dis_matrix = {}
        self.vehicle_capacity = 3600
        self.big_M = 10000

'''
读取算例数据 
'''
data = pd.read_excel("物流运输问题算例数据.xlsx")

instance = Instance()

for i in range(len(data)):
    new_OD_pair = OD_pair()
    new_OD_pair.org = data.iloc[i, 0]
    new_OD_pair.des = data.iloc[i, 1]
    new_OD_pair.distance = data.iloc[i, 2]
    new_OD_pair.demand = data.iloc[i, 3]
    new_OD_pair.cost = data.iloc[i, 4]
    instance.OD_set[i] = new_OD_pair
    instance.arc_dis_matrix[new_OD_pair.org, new_OD_pair.des] = data.iloc[i, 2]
	

"""
建立模型并求解
"""
model = Model("delivery network")


# 创建决策变量
x = {}
f = {}
y = {}
u = {}
F = {}

for i in instance.cities.keys():
    for j in instance.cities.keys():
        if(i != j):
            # 创建变量 F[i, j]
            F[i, j] = model.addVar(lb=0, ub=20000, vtype=GRB.CONTINUOUS,
                                      name='F_' + str(i) + '_' + str(j))
            # 创建变量 y[i, j]
            y[i, j] = model.addVar(lb=0, ub=10, vtype=GRB.INTEGER, name='y_' + str(i) + '_' + str(j))

            # 创建变量 x[i, j, p] 和 f[i, j, p]
            for p in instance.OD_set.keys():
                if(instance.OD_set[p].demand > 0):
                    x[i, j, p] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name='x_'+str(i)+'_'+str(j)+'_'+str(p))
                    f[i, j, p] = model.addVar(lb=0, ub=10000, vtype=GRB.CONTINUOUS,
                                              name='f_' + str(i) + '_' + str(j) + '_' + str(p))
                    u[i, p] = model.addVar(lb=0, ub=11, vtype=GRB.INTEGER,
                                              name='u_' + str(i) + '_' + str(p))

# 创建目标函数
inner_province_cost = LinExpr()
inter_province_cost = LinExpr()
for i in instance.cities.keys():
    for j in instance.cities.keys():
        if(i != j):
            if(instance.cities[i] != instance.cities[j]):
                inter_province_cost.addTerms(3.6 * instance.arc_dis_matrix[i, j] + 450, y[i, j])

            for p in instance.OD_set.keys():
                if (instance.OD_set[p].demand > 0):
                    # 如果城市 i 和城市 j 在同一个省份
                    if(instance.cities[i] == instance.cities[j]):
                        inner_province_cost.addTerms((3.6 * instance.arc_dis_matrix[i, j] + 450)/instance.vehicle_capacity, f[i, j, p])

model.setObjective(inter_province_cost + inner_province_cost, GRB.MINIMIZE)

# 添加约束 1
for p in instance.OD_set.keys():
    if (instance.OD_set[p].demand > 0):
        lhs = LinExpr()
        OD_org = instance.OD_set[p].org
        for j in instance.cities.keys():
            if(OD_org != j):
                lhs.addTerms(1, x[OD_org, j, p])
        model.addConstr(lhs == 1, name='c1_'+str(p))

# 添加约束 2
for p in instance.OD_set.keys():
    if (instance.OD_set[p].demand > 0):
        lhs = LinExpr()
        OD_des = instance.OD_set[p].des
        for j in instance.cities.keys():
            if(OD_des != j):
                lhs.addTerms(1, x[j, OD_des, p])
        model.addConstr(lhs == 1, name='c2_'+str(p))

# 添加约束 3
for p in instance.OD_set.keys():
    if (instance.OD_set[p].demand > 0):
        OD_org = instance.OD_set[p].org
        OD_des = instance.OD_set[p].des

        for j in instance.cities.keys():
            if(OD_org != j and OD_des != j):
                lhs = LinExpr()
                for i in instance.cities.keys():
                    if(i != j):
                        lhs.addTerms(1, x[i, j, p])
                for i in instance.cities.keys():
                    if(i != j):
                        lhs.addTerms(-1, x[j, i, p])

                model.addConstr(lhs == 0, name='c3_'+str(p)+'_'+str(j))


# 添加约束 4 和 5
for i in instance.cities.keys():
    for j in instance.cities.keys():
        if(i != j):
            lhs = LinExpr()
            for p in instance.OD_set.keys():
                if (instance.OD_set[p].demand > 0):
                     lhs.addTerms(1/instance.vehicle_capacity, f[i, j, p])

            model.addConstr(y[i, j] >= lhs, name='c4-1_' + str(i) + '_' + str(j))
            model.addConstr(y[i, j] - 1 <= lhs, name='c4-2_' + str(i) + '_' + str(j))

# 添加约束 6
for i in instance.cities.keys():
    for j in instance.cities.keys():
        if(i != j):
            for p in instance.OD_set.keys():
                if (instance.OD_set[p].demand > 0):
                    model.addConstr(f[i, j, p] == instance.OD_set[p].demand * x[i, j, p], name='c5_' + str(i) + '_' + str(j) + '_' + str(p))

# 添加约束 7
for p in instance.OD_set.keys():
    if (instance.OD_set[p].demand > 0): # 注意，一定判斷demand >0
        for i in instance.cities.keys():
            for j in instance.cities.keys():
                if (i != j):
                    model.addConstr(u[i, p] - u[j, p] + 1 - instance.big_M * (1 - x[i, j, p]) <= 0, name='c7_' + str(i) + '_' + str(j) + '_' + str(p))

# 添加约束 8
for i in instance.cities.keys():
    for j in instance.cities.keys():
        if(i != j):
            lhs = LinExpr()
            for p in instance.OD_set.keys():
                if (instance.OD_set[p].demand > 0):  # 注意，一定判斷demand >0
                    lhs.addTerms(1, f[i, j, p])
            model.addConstr(lhs == F[i, j])

model.optimize()
model.write('DND.lp')

# 输出求解结果
print('\n总运输费用：{}'.format(model.ObjVal))
print('\n省内总运输费用：{}'.format(inner_province_cost.getValue()))
print('\n省间总运输费用：{}'.format(inter_province_cost.getValue()))
print('\n********   Route (OD version)   ********\n')
for p in instance.OD_set.keys():
    if(instance.OD_set[p].demand > 0):
        print('\n----------------')
        print('OD pair ID: {}, org: {}, des: {}, demand: {}'.format(p,
                                                           instance.OD_set[p].org,
                                                           instance.OD_set[p].des,
                                                           instance.OD_set[p].demand,))
        for i in instance.cities.keys():
            for j in instance.cities.keys():
                if (i != j):
                    if(x[i, j, p].x > 0):
                        print('{} = {}'.format(x[i, j, p].VarName, x[i, j, p].x), end='')
                        print('  |  Load: {} = {}'.format(f[i, j, p].VarName, f[i, j, p].x), end='')
                        if((i, j) in y.keys()):
                            print('  |  Vehicle cnt: {} = {}'.format(y[i, j].VarName, y[i, j].x), end='')
                        print()

print('\n********   Flow (arc version)   ********\n')
for i in instance.cities.keys():
    for j in instance.cities.keys():
        if (i != j):
            if((i, j) in y.keys()):
                if(F[i, j].x > 0):
                    print('\n---------------------')
                    print('Arc: ({}, {}), Load: {} = {}'.format(i, j, F[i, j].VarName, F[i, j].x), end='\n')
                    print('Commodity flows')
                    for p in instance.OD_set.keys():
                        if(instance.OD_set[p].demand > 0):
                            if(x[i, j, p].x > 0):
                                print('{} = {},\t |  Load: {} = {},\t | Vehicle Cnt: {} = {}'.format(x[i, j, p].VarName, x[i, j, p].x,
                                                  f[i, j, p].VarName, f[i, j, p].x, y[i, j].VarName, y[i, j].x), end='\n')