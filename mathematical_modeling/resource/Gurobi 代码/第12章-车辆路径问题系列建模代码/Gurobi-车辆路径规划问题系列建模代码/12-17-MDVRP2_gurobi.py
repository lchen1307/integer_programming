"""
booktitle: 《数学建模与数学规划：方法、案例及编程实战 Python+COPT+Gurobi实现》
name: 多车场车辆路径规划问题（MDVRP2）- Gurobi - Python接口代码实现
author: 张一白
date: 2022-11-11
"""

import math
from gurobipy import *

# 读取算例，只取了前14个客户点
f = open('r101_MDVRP.txt', 'r')
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

# 设计车场的最大发车数量，限制第二个车场只能发一辆车
Deta = [3, 1]

# 设置前两个点为车场
D = 2

# 设置车辆集合
K = 3

# 开始在Gurobi中建模
try:
    m = Model("MDVRP2")

    # 创建变量
    x = {}
    q = {}
    # 将第一个点和第二个点作为都作为车场。节点数共有N+D个，顾客书等于N-D个
    S = N - D
    N = N + D
    for k in range(K):
        for i in range(N):
            # 创建车辆到达点i剩余容量变量q_i,是连续类型变量，算例设置的车辆容量最大为200，因只使用了其中14个点，将容量限制为80。
            q[i, k] = m.addVar(lb=0.0, ub=80, obj=0.0, vtype=GRB.CONTINUOUS, name="q_%d_%d" % (i, k))
        for i in range(N - D):
            for j in range(D, N):
                # 默认不存在点i到点i的弧。
                if i != j:
                    # 以下两个是排除车场到车场的变量
                    if i in range(D):
                        if j in range(D, N - D):
                            x[i, j, k] = m.addVar(obj=Distance[i][j], vtype=GRB.BINARY, name="x_%d_%d_%d" % (i, j, k))
                    else:
                        if j in range(D, N - D):
                            x[i, j, k] = m.addVar(obj=Distance[i][j], vtype=GRB.BINARY, name="x_%d_%d_%d" % (i, j, k))
                        else:
                            x[i, j, k] = m.addVar(obj=Distance[i][j - S - D], vtype=GRB.BINARY,
                                                  name="x_%d_%d_%d" % (i, j, k))

    # 设置目标函数(如果最大化改成-1就可以了)
    m.modelsense = 1

    # 车场的发车数量不能超过其可发车的数量
    for i in range(0, D):
        expr = LinExpr()
        for j in range(D, N - D):
            if i != j:
                for k in range(K):
                    expr.addTerms(1, x[i, j, k])
        m.addConstr(expr <= Deta[i], name="DepotCapa_%d" % (i))

    # 每个客户都必须被有且只有一辆车服务，使用可能离开点i的路径刻画
    for i in range(D, N - D):
        expr = LinExpr()
        for j in range(D, N):
            if i != j:
                for k in range(K):
                    expr.addTerms(1, x[i, j, k])
        m.addConstr(expr == 1, name="Customer_%d" % (i))

    # 配送中心或车场发出的车辆要等于回来的车辆
    for k in range(K):
        # 每个车只能调用一次
        expr = LinExpr()
        for d in range(D):
            m.addConstr(
                sum(x[d, j, k] for j in range(D, N - D)) - sum(x[i, d + S + D, k] for i in range(D, N - D)) == 0,
                "DepotFlowConstr_%d_%d" % (d, k))
            for i in range(D, N - D):
                expr.addTerms(1, x[d, i, k])
        m.addConstr(expr <= 1, "UseofVehicle_%d" % k)

    # 客户点的流平衡约束
    for k in range(K):
        for i in range(D, N - D):
            lh = LinExpr()
            rh = LinExpr()
            for j in range(D, N):
                if i != j:
                    rh.addTerms(1, x[i, j, k])
            for j in range(N - D):
                if i != j:
                    lh.addTerms(1, x[j, i, k])
            m.addConstr(lh - rh == 0, "PointFlowConstr_%d_%d" % (i, k))

    # 两种容量约束控制容量变化，并避免环路
    for k in range(K):
        for i in range(D, N - D):
            for j in range(D, N):
                if i != j:
                    m.addConstr(q[i, k] + Demand[i] - q[j, k] <= (1 - x[i, j, k]) * 200,
                                "Capacity_%d_%d_%d" % (i, j, k))

    log_file_name = 'MDVRP2.log'
    m.setParam(GRB.Param.LogFile, log_file_name)  # 设置输出路径
    m.setParam(GRB.Param.MIPGap, 0)  # 设置 MIPGap 容差为 0
    m.optimize()  # 命令求解器进行求解

    print('Obj:', m.ObjVal)  # 输出最优值
    for k in range(K):
        for i in range(N - D):
            for j in range(D, N):
                if i != j:
                    if i in range(D):
                        if j in range(D + S, N):
                            continue
                        else:
                            if x[i, j, k].x > 0.9:
                                print("Name : %s , Value : %s " % (x[i, j, k].varName, x[i, j, k].x))
                    else:
                        if x[i, j, k].x > 0.9:
                            print("Name : %s , Value : %s " % (x[i, j, k].varName, x[i, j, k].x))
    # 输出最优解
    Count = 1
    for k in range(K):
        for d in range(D):
            for i in range(D, N - D):
                A = True
                if x[d, i, k].x >= 0.9:
                    print("第%d条路径为：" % Count, end="\n")
                    print("场站%d-客户%d-" % (d, i), end="")
                    Cur = i
                    while (A):
                        I = Cur
                        for j in range(D, N):
                            if Cur != j and x[Cur, j, k].x >= 0.9:
                                if j in range(D, D + S):
                                    print("客户%d-" % j, end="")
                                    Cur = j
                                else:
                                    print("场站%d" % d, end="\n")
                                    A = False
                    Count += 1
    #  输出MDVRP2的模型
    m.write("MDVRP2.lp")
    m.write("MDVRP2.mps")

except GurobiError as e:
    print("Error code " + str(e.errno) + ": " + str(e))