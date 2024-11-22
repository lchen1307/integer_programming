"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 带容量约束的车辆路径问题（CVRP1-2）- COPT - Python接口代码实现
author: 杉数科技
date: 2022-10-11
institute: 杉数科技 
"""

import math
from coptpy import *


# 读取算例，只取了前15个客户点
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


def CVRP1_2(N,K,Demand,Distance):
    try:
        env = Envr()
        m = env.createModel("CVRP1-2")
        # 创建变量
        x = {}
        q = {}
        # 因为复制了配送中心点为{o，d}，所以点的总个数是N+1，默认不存在以{o}为终点和{d}为起点的弧。
        for k in range(K):
            for i in range(N + 1):
                # 创建车辆到达点i剩余容量变量q_i,是连续类型变量，算例设置的车辆容量最大为200，因只使用了其中15个点，将容量限制为100。
                q[i, k] = m.addVar(lb=0.0, ub=100, obj=0.0, vtype=COPT.CONTINUOUS, name="q_%d_%d" % (i, k))
            for i in range(N):
                for j in range(1, N + 1):
                    # 默认不存在点i到点i的弧，也不存在点{o}到点{d}的弧。
                    if i != j:
                        # 以{o}开始的弧
                        if i == 0 and j != (N):
                            x[i, j, k] = m.addVar(obj=Distance[i][j], vtype=COPT.BINARY, name="x_%d_%d_%d" % (i, j, k))
                        # 以{d}结尾的弧
                        elif i != 0 and j == (N):
                            x[i, j, k] = m.addVar(obj=Distance[i][0], vtype=COPT.BINARY, name="x_%d_%d_%d" % (i, j, k))
                        # 客户点之间的弧
                        elif i != 0 and i != (N) and j != 0 and j != (N):
                            x[i, j, k] = m.addVar(obj=Distance[i][j], vtype=COPT.BINARY, name="x_%d_%d_%d" % (i, j, k))
        # 设置目标函数最小化
        m.setObjSense(COPT.MINIMIZE)

        # 每个客户都必须被有且只有一辆车服务，使用可能离开点i的路径刻画
        for i in range(1, N):
            expr = LinExpr()
            for k in range(K):
                for j in range(1, N + 1):
                    if i != j:
                        expr.addTerms(x[i, j, k], 1)
            m.addConstr(expr == 1, "Customer_%d" % i)

        # 配送中心或车场发出的车辆要等于回来的车辆，当然可以直接写两次循环啦
        for k in range(K):
            m.addConstr(sum(x[0, j, k] for j in range(1, N)) - sum(
                x[i, N, k] for i in range(1, N)) == 0,
                        "DepotFlowConstr_%d" % k)

        # 客户点的流平衡约束
        for k in range(K):
            for j in range(1, N):
                lh = LinExpr()
                rh = LinExpr()
                for i in range(N + 1):
                    if i != j:
                        if i != N:
                            lh.addTerms(x[i, j, k], 1)
                        if i != 0:
                            rh.addTerms(x[j, i, k], 1)
                m.addConstr(lh - rh == 0, "PointFlowConstr_%d_%d" % (j, k))

        # MTZ约束控制容量变化，并避免环路
        for k in range(K):
            for i in range(1, N):
                for j in range(1, N + 1):
                    if i != j:
                        m.addConstr(q[i, k] + Demand[i] - q[j, k] <= (1 - x[i, j, k]) * 200,
                                    "Capacity_%d_%d_%d" % (i, j, k))

        log_file_name = 'CVRP1-2.log'
        m.setLogFile(log_file_name)  # 设置输出路径
        m.setParam(COPT.Param.AbsGap, 0)  # 设置 AbsGap 容差为 0
        m.solve()  # 命令求解器进行求解

        print('Obj:', m.ObjVal)  # 输出最优值

        # 输出最优解
        Count = 1
        for k in range(K):
            for i in range(1, N):
                A = True
                if x[0, i, k].x >= 0.9:
                    print("第%d条路径为：" % Count, end="\n")
                    print("场站-客户%d-" % i, end="")
                    Cur = i
                    while (A):
                        for j in range(1, N + 1):
                            if Cur != j and x[Cur, j, k].x >= 0.9:
                                if j != N:
                                    print("客户%d-" % j, end="")
                                    Cur = j
                                else:
                                    print("场站", end="\n")
                                    A = False
                                break
                    Count += 1
        #  输出CVPR1-2的模型
        m.write("CVRP1-2.lp")
        m.write("CVRP1-2.mps")
    except CoptError as e:
        print("Error code " + str(e.retcode) + ": " + str(e))


# 开始在Copt中建模
CVRP1_2(N,K,Demand,Distance)
