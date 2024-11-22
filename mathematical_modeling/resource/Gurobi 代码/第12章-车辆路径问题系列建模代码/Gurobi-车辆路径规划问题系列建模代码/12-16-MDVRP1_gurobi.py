"""
booktitle: 《数学建模与数学规划：方法、案例及编程实战 Python+COPT+Gurobi实现》
name: 多车场车辆路径规划问题（MDVRP1）- Gurobi - Python接口代码实现
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
K = 2

# 开始在Gurobi中建模
try:
    m = Model("MDVRP1")

    # 创建变量
    x = {}
    q = {}
    # 将第一个点和第二个点作为都作为车场。
    for i in range(N):
        # 创建车辆到达点i剩余容量变量q_i,是连续类型变量，算例设置的车辆容量最大为200，因只使用了其中14个点，将容量限制为80。
        q[i] = m.addVar(lb=0.0, ub=80, obj=0.0, vtype=GRB.CONTINUOUS, name="q_%d" % i)
        for j in range(N):
            # 默认不存在点i到点i的弧。
            if i != j:
                # 以下两个是排除车场到车场的变量
                if i + j < K:
                    continue
                # 以{d}结尾的弧
                elif i == K - 1 and j == K - 1:
                    continue
                # else的是所有可能的弧
                else:
                    x[i, j] = m.addVar(obj=Distance[i][j], vtype=GRB.BINARY, name="x_%d_%d" % (i, j))
    # 设置目标函数(如果最大化改成-1就可以了)
    m.modelsense = 1

    # 车场的发车数量不能超过其可发车的数量
    for i in range(0, K):
        expr = LinExpr()
        for j in range(K, N):
            if i != j:
                expr.addTerms(1, x[i, j])
        m.addConstr(expr <= Deta[i], name="DepotCapa_%d" % (i))

    # 每个客户都必须被有且只有一辆车服务，使用可能离开点i的路径刻画
    for i in range(K, N):
        expr = LinExpr()
        for j in range(N):
            if i != j:
                expr.addTerms(1, x[i, j])
        m.addConstr(expr == 1, name="Customer_%d" % (i))

    # 配送中心或车场发出的车辆要等于回来的车辆
    for k in range(K):
        m.addConstr(sum(x[k, j] for j in range(2, N)) - sum(x[i, k] for i in range(2, N)) == 0,
                    "DepotFlowConstr%d" % k)

    # 点的流平衡约束
    for j in range(N):
        lh = LinExpr()
        rh = LinExpr()
        for i in range(N):
            if i != j:
                if i + j < K:
                    continue
                elif i == K - 1 and j == K - 1:
                    continue
                else:
                    lh.addTerms(1, x[i, j])
                    rh.addTerms(1, x[j, i])
        m.addConstr(lh - rh == 0, "PointFlowConstr_%d" % j)

    # 两种容量约束控制容量变化，并避免环路
    for i in range(K, N):
        for j in range(K, N):
            if i != j:
                m.addConstr(q[i] + Demand[i] - q[j] <= (1 - x[i, j]) * 200, "Capacity_%d_%d" % (i, j))
    for j in range(K):
        for i in range(K, N):
            m.addConstr(q[i] + Demand[i] - 80 <= (1 - x[i, j]) * 200, "Capacity_%d_%d" % (i, j))
    log_file_name = 'MDVRP1.log'
    m.setParam(GRB.Param.LogFile, log_file_name)  # 设置输出路径
    m.setParam(GRB.Param.MIPGap, 0)  # 设置 MIPGap 容差为 0
    m.optimize()  # 命令求解器进行求解

    print('Obj:', m.ObjVal)  # 输出最优值

    # 输出最优解
    Count = 1
    for k in range(K):
        for i in range(K, N):
            A = True
            if x[k, i].x >= 0.9:
                print("第%d条路径为：" % Count, end="\n")
                print("场站%d-客户%d-" % (k, i), end="")
                Cur = i
                while (A):
                    I = Cur
                    for j in range(K, N):
                        if Cur != j and x[Cur, j].x >= 0.9:
                            print("客户%d-" % j, end="")
                            Cur = j
                    if Cur == I:
                        print("场站%d" % k, end="\n")
                        A = False
                Count += 1
    #  输出MDVRP1的模型
    m.write("MDVRP1.lp")
    m.write("MDVRP1.mps")
except GurobiError as e:
    print("Error code " + str(e.errno) + ": " + str(e))

