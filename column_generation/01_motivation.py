# 此算例来自《运筹优化常用模型、算法及案例实战》
# 第13章 列生成算法
# 13.1 为什么使用列生成算法

from gurobipy import *
import pandas as pd
import numpy as np

# 1 一个满秩的线性规划问题求解过程
model = Model('LP')
X = {}
for i in range(2):
    X[i + 1] = model.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'x' + str(i + 1))

model.setObjective(7 * X[1] + 5 * X[2], GRB.MAXIMIZE)
model.addConstr(X[1] + X[2] <= 5)
model.addConstr(7 * X[1] + 3 * X[2] <= 21)
model.optimize()

print('Objective =', model.ObjVal)
for var in model.getVars():
    print(var.varName, '=', var.x)


# 2 另一个变量个数远大于约数个数的LP
# 这也是列生成算法提出的动机
model = Model('LP2')
X = {}
for i in range(6):
    X[i + 1] = model.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'x' + str(i + 1))

model.setObjective(7 * X[1] + 5 * X[2] - X[3] - X[4] - X[5] - X[6], GRB.MAXIMIZE)
model.addConstr(X[1] + X[2] + X[3] + X[5] <= 5)
model.addConstr(7 * X[1] + 3 * X[2] + X[4] + X[6] <= 21)
model.optimize()

print('Objective =', model.ObjVal)
for var in model.getVars():
    print(var.varName, '=', var.x)