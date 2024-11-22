"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 带容量约束的车辆路径问题（CVRP1-1）- COPT - Python接口代码实现
author: 杉数科技
date: 2022-10-11
institute: 杉数科技 
"""

import numpy as np
import math
import time
import copy
from coptpy import *

def getRoute(x_values):
    x = copy.deepcopy(x_values)
    routes_by_car = {}  # 路径字典：key为车辆ID，value为路径

    for k in range(K):
        routes = []  # 路径list
        is_subtour = False    # Boolean Value: 是否为子回路
        for i in range(1, N):
            route = []
            for j in range(1, N):
                if i != j and x[i][j][k] > 0.01:
                    route.append(i)
                    route.append(j)
                    current_node = j

                    while not is_subtour:
                        for next_node in range(1, N + 1):
                            if current_node != next_node and x[current_node][next_node][k] > 0.01:
                                route.append(next_node)
                                # 如果下一个节点等于路径中的第一个节点则形成回路
                                if route[0] == next_node:
                                    is_subtour = True
                                    routes.append(route)
                                    break
                                # 如遍历完所有节点，则终止循环
                                if next_node == N:
                                    is_subtour = True
                                    break
                                current_node = next_node
        routes_by_car[k] = routes

    return routes_by_car

# 实例化一个作为参数传入模型的callback类
class CoptCallback(CallbackBase): # x 为tupledict类
    def __init__(self, x):
        super().__init__()
        self.x = x
        self.ctr = 0

    def callback(self):
        if self.where() == COPT.CBCONTEXT_MIPSOL:
            x_values = np.zeros([N + 1, N + 1, K])
            sol = self.getSolution(self.x)
            for (a, b, c) in sol:
                x_values[a][b][c] = sol[a, b, c]
            tour = getRoute(x_values)
            # 只打印非空子回路
            if sum(len(t) for t in tour.values()) > 0:
                print(f'Callback addLazyConstr No.{self.ctr} tour = {tour}')

            for k in range(K):
                for r in range(len(tour[k])):
                    tour[k][r].remove(tour[k][r][0])
                    expr = LinExpr()
                    for i in range(len(tour[k][r])):
                        for j in range(len(tour[k][r])):
                            if tour[k][r][i] != tour[k][r][j]:
                                expr.addTerms(x[tour[k][r][i], tour[k][r][j], k], 1.0)
                    self.addLazyConstr(expr <= len(tour[k][r]) - 1)
                    self.ctr += 1

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

# 开始在COPT中建模
try:
    # 创建求解环境
    env = Envr()
    # 创建模型对象
    m = env.createModel("CVRP1-1-COPT")
    # 创建变量
    x = tupledict()
    # 因为复制了配送中心点为{o，d}，所以点的总个数是N+1，默认不存在以{o}为终点和{d}为起点的弧。
    for k in range(K):
        for i in range(N):
            for j in range(1, N + 1):
                # 默认不存在点i到点i的弧，也不存在点{o}到点{d}的弧。
                if i != j:
                    # 以{o}开始的弧
                    if i == 0 and j != (N):
                        x[i, j, k] = m.addVar(obj=Distance[i][j], vtype='B', name="x_%d_%d_%d" % (i, j, k))
                    # 以{d}结尾的弧
                    elif i != 0 and j == (N):
                        x[i, j, k] = m.addVar(obj=Distance[i][0], vtype='B', name="x_%d_%d_%d" % (i, j, k))
                    # 客户点之间的弧
                    elif i != 0 and i != (N) and j != 0 and j != (N):
                        x[i, j, k] = m.addVar(obj=Distance[i][j], vtype='B', name="x_%d_%d_%d" % (i, j, k))
    # 设置目标函数
    m.ObjSense = COPT.MINIMIZE

    # 每个客户都必须被有且只有一辆车服务，使用可能离开点i的路径刻画
    for i in range(1, N):
        expr = LinExpr()
        for k in range(K):
            for j in range(1, N + 1):
                if i != j:
                    expr.addTerm(x[i, j, k], 1)
        m.addConstr(expr == 1, name="Customer_%d_%d" % (i, k))

    # 配送中心或车场发出的车辆要等于回来的车辆
    for k in range(K):
        m.addConstr(sum(x[0, j, k] for j in range(1, N) for k in range(K)) - sum(
            x[i, N, k] for i in range(1, N) for k in range(K)) == 0,
                    name="DepotFlowConstr_%d" % k)

    # 客户点的流平衡约束
    for k in range(K):
        for j in range(1, N):
            lhs = LinExpr()
            rhs = LinExpr()
            for i in range(N + 1):
                if i != j:
                    if i != N:
                        lhs.addTerm(x[i, j, k], 1)
                    if i != 0:
                        rhs.addTerm(x[j, i, k], 1)
            m.addConstr(lhs == rhs, name="PointFlowConstr_%d_%d" % (j, k))

    # 容量约束
    for k in range(K):
        lhs = LinExpr()
        for i in range(1, N):
            for j in range(1, N + 1):
                if i != j:
                    lhs.addTerm(x[i, j, k], Demand[i])
        m.addConstr(lhs <= 100, "Capacity_%d" % k)

    # 设置求解日志文件名及输出状态
    log_file_name = 'CVRP1-1.log'
    m.setLogFile(log_file_name)  # 设置输出路径
    m.setParam(COPT.Param.RelGap, 0)  # 设置整数规划最优相对容差为 0
    m.Param.LazyConstraints = 1

    # 设置自定义的callback
    cb = CoptCallback(x)
    m.setCallback(cb, COPT.CBCONTEXT_MIPSOL)
    m.solve()  # 开始求解
    print('最优值:', m.ObjVal)  # 输出最优值

    # 输出最优解
    Count = 1
    for k in range(K):
        for i in range(1, N):
            is_complete = False
            if x[0, i, k].x >= 0.9:
                print("第%d条路径为：" % Count, end="\n")
                print("场站-客户%d-" % i, end="")
                Cur = i
                while not is_complete:
                    for j in range(1, N + 1):
                        if Cur != j and x[Cur, j, k].x >= 0.9:
                            if j != N:
                                print("客户%d-" % j, end="")
                                Cur = j
                            else:
                                print("场站", end="\n")
                                is_complete = True
                            break
                Count += 1

    #  输出CVPR1-1的模型
    m.write("CVRP1-1.mps")
    m.write("CVRP1-1.lp")
except CoptError as e:
    print("Error code " + str(e.retcode) + ": " + str(e))

