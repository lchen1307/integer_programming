"""
booktitle: 《数学建模与数学规划：方法、案例及编程实战 Python+COPT+Gurobi实现》
name: 带容量约束的车辆路径问题（CVRP1-1）- Gurobi - Python接口代码实现
author: 张一白
date: 2022-11-11
"""

import numpy as np
import math
import time
import copy
from gurobipy import *


def getRoute(x_value):
    x = copy.deepcopy(x_value)

    route_list = {}

    for k in range(K):
        Route = []
        route_list[k] = Route
        A = True
        for i in range(1, N):
            R = []
            for j in range(1, N):
                if i != j and x[i][j][k] >= 0.01:
                    R.append(i)
                    R.append(j)

                    Cur = j
                    Count = 1
                    while (A !=False):
                        for l in range(1, N + 1):
                            if Cur != l and x[Cur][l][k] >= 0.01:

                                R.append(l)
                                if R[0] == l:
                                    A = False
                                    Route.append(R)
                                    break
                                if l==N:
                                    A = False
                                    break
                                Cur = l
                        Count +=1
        route_list[k] = Route

    return route_list


def subtourlim(model, where):
    if (where == GRB.Callback.MIPSOL):
        x_value = np.zeros([N + 1, N + 1, K])
        for m in model.getVars():
            if (m.varName.startswith('x')):
                a = (int)(m.varName.split('_')[1])
                b = (int)(m.varName.split('_')[2])
                c = (int)(m.varName.split('_')[3])
                x_value[a][b][c] = model.cbGetSolution(m)
        tour = getRoute(x_value)
        print('tour = ', tour)
        for k in range(K):

            for r in range(len(tour[k])):
                tour[k][r].remove(tour[k][r][0])
                expr = LinExpr()
                for i in range(len(tour[k][r])):
                    for j in range(len(tour[k][r])):
                        if tour[k][r][i] != tour[k][r][j]:
                            expr.addTerms(1.0, x[tour[k][r][i], tour[k][r][j], k])
                model.cbLazy(expr <= len(tour[k][r]) - 1)



# 读取算例，只取了前15个点
f = open('r101_CVRP.txt', 'r')
sth = f.readlines()

# 存取数据，并打印数据
data = []
for i in sth:
    item = i.strip("\n").split()
    data.append(item)
N = len(data)
for i in range(N):
    for j in range(len(data[i])):
        print(data[i][j], end="\t\t")
        data[i][j] = int(data[i][j])
    print()
print("------------------------------------------")
# 计算距离矩阵，保留两位小数，并打印矩阵
Distance = [[round(math.sqrt(sum((data[i][k] - data[j][k]) ** 2 for k in range(1, 3))), 2) for i in range(N)]
            for j in range(N)]
for i in range(len(Distance)):
    for j in range(len(Distance[i])):
        if i != j:
            print(Distance[i][j], end="\t\t")
    print()

# 读取算例中的需求列
Demand = [data[i][3] for i in range(N)]

# 设置车辆数K
K = 3

# 开始在Gurobi中建模
try:
    m = Model("CVRP1-1")

    # 创建变量
    x = {}
    # 因为复制了配送中心点为{o，d}，所以点的总个数是N+1，默认不存在以{o}为终点和{d}为起点的弧。
    for k in range(K):
        for i in range(N):
            for j in range(1, N + 1):
                # 默认不存在点i到点i的弧，也不存在点{o}到点{d}的弧。
                if i != j:
                    # 以{o}开始的弧
                    if i == 0 and j != (N):
                        x[i, j, k] = m.addVar(obj=Distance[i][j], vtype=GRB.BINARY, name="x_%d_%d_%d" % (i, j, k))
                    # 以{d}结尾的弧
                    elif i != 0 and j == (N):
                        x[i, j, k] = m.addVar(obj=Distance[i][0], vtype=GRB.BINARY, name="x_%d_%d_%d" % (i, j, k))
                    # 客户点之间的弧
                    elif i != 0 and i != (N) and j != 0 and j != (N):
                        x[i, j, k] = m.addVar(obj=Distance[i][j], vtype=GRB.BINARY, name="x_%d_%d_%d" % (i, j, k))
    # 设置目标函数(如果最大化改成-1就可以了)
    m.modelsense = 1

    # 每个客户都必须被有且只有一辆车服务，使用可能离开点i的路径刻画
    for i in range(1, N):
        expr = LinExpr()
        for k in range(K):
            for j in range(1, N + 1):
                if i != j:
                    expr.addTerms(1, x[i, j, k])
        m.addConstr(expr == 1, name="Customer_%d_%d" % (i, k))

    # 配送中心或车场发出的车辆要等于回来的车辆
    for k in range(K):
        m.addConstr(sum(x[0, j, k] for j in range(1, N) for k in range(K)) - sum(
            x[i, N, k] for i in range(1, N) for k in range(K)) == 0,
                    "DepotFlowConstr_%d" % k)

    # 客户点的流平衡约束
    for k in range(K):
        for j in range(1, N):
            lh = LinExpr()
            rh = LinExpr()
            for i in range(N + 1):
                if i != j:
                    if i != N:
                        lh.addTerms(1, x[i, j, k])
                    if i != 0:
                        rh.addTerms(1, x[j, i, k])
            m.addConstr(lh - rh == 0, "PointFlowConstr_%d_%d" % (j, k))
    # 容量约束
    for k in range(K):
        lh = LinExpr()
        for i in range(1, N):
            for j in range(1, N + 1):
                if i != j:
                    lh.addTerms(Demand[i], x[i, j, k])
        m.addConstr(lh <= 100, "Capacity_%d" % k)
    log_file_name = 'CVRP1-1.log'
    m.setParam(GRB.Param.LogFile, log_file_name)  # 设置输出路径
    m.setParam(GRB.Param.MIPGap, 0)  # 设置 MIPGap 容差为 0
    m.Params.lazyConstraints = 1
    m.optimize(subtourlim)  # 命令求解器进行求解
    # m.computeIIS()
    # m.write("model.ilp")
    print('最优值:', m.ObjVal)  # 输出最优值
    # 输出最优解
    Count = 1
    for k in range(K):
        for i in range(1, N):
            A = True
            if x[0,i,k].x >= 0.9:
                print("第%d条路径为：" % Count, end="\n")
                print("场站-客户%d-" % i, end="")
                Cur = i
                while (A):
                    for j in range(1, N + 1):
                        if Cur != j and x[Cur,j,k].x >= 0.9:
                            if j != N:
                                print("客户%d-" % j, end="")
                                Cur = j
                            else:
                                print("场站", end="\n")
                                A = False
                            break
                Count += 1
    #  输出CVPR1-1的模型
    m.write("CVRP1-1.mps")
    m.write("CVRP1-1.lp")

except GurobiError as e:
    print("Error code " + str(e.errno) + ": " + str(e))
