"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 带时间窗的多行程车辆路径问题（MTVRPTW2）- COPT - Python接口代码实现
author: 杉数科技
date: 2022-10-11
institute: 杉数科技 
"""

import math
from coptpy import *

# 读取算例，只挑选了前10个点
f = open('r101_35.txt', 'r')
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

# 读取算例中的需求列和服务时间列
Demand = [data[i][3] for i in range(N)]
ST = [data[i][6] for i in range(N)]

# 存取算例中的时间窗
A = [data[i][4] for i in range(N)]
B = [data[i][5] for i in range(N)]

# 设置车程数，最差应为N-1个，但会增加模型的对称性，这里设置的车程数小一些
R = 7
# 同理设置车辆数，车辆数应比车程数略小，这两个参数大了都会使得模型臃肿
K = 7
# 设置重新装货时间，和车辆使用成本
Tau = 1
F = 300


def MTVRPTW_2(N,A,B,Demand,Distance,ST,R,K,Tau,F):
    try:
        env = Envr()
        m = env.createModel("MTVRPTW2")

        # 创建变量
        x = {}
        z = {}
        y = {}
        f = {}
        q = {}
        t = {}
        # 因为复制了配送中心点为{o，d}，所以点的总个数是N+1，默认不存在以{o}为终点和{d}为起点的弧。
        N = N + 1

        # 创建路径决策变量x_{ijr}
        for r in range(R):
            for i in range(N - 1):
                for j in range(1, N):
                    # 默认不存在点i到点i的弧，也不存在点{o}到点{d}的弧。
                    if i != j:
                        # 以{o}开始的弧
                        if i == 0 and j != (N - 1):
                            x[i, j, r] = m.addVar(obj=Distance[i][j], vtype=COPT.BINARY, name="x_%d_%d_%d" % (i, j, r))
                        # 以{d}结尾的弧
                        elif i != 0 and j == (N - 1):
                            x[i, j, r] = m.addVar(obj=Distance[i][0], vtype=COPT.BINARY, name="x_%d_%d_%d" % (i, j, r))
                        # 客户点之间的弧
                        elif i in range(1, N - 1) and j in range(1, N - 1):
                            x[i, j, r] = m.addVar(obj=Distance[i][j], vtype=COPT.BINARY, name="x_%d_%d_%d" % (i, j, r))
        # 创建分配车程的变量y_{kr}
        for r in range(R):
            for k in range(K):
                y[k, r] = m.addVar(obj=0.0, vtype=COPT.BINARY, name="y_%d_%d" % (k, r))
        # 创建车程排序变量z_{ijk},以及车辆是否被使用的变量f_k
        for k in range(K):
            f[k] = m.addVar(obj=F, vtype=COPT.BINARY, name="f_%d" % k)
            for i in range(R):
                for j in range(R):
                    if i != j:
                        z[i, j, k] = m.addVar(obj=0.0, vtype=COPT.BINARY, name="z_%d_%d_%d" % (i, j, k))
        # 设置时间变量和剩余容量变量
        for i in range(N):
            # 创建车辆到达点i剩余容量变量q_i,是连续类型变量，算例设置的车辆容量最大为200，因只使用了其中10个点，将容量限制为75。
            q[i] = m.addVar(lb=0.0, ub=75, obj=0.0, vtype=COPT.CONTINUOUS, name="q_%d" % i)
            for r in range(R):
                # 创建车辆到达时间变量，算例中给出了上下界
                if i in range(1, N - 1):
                    t[i, r] = m.addVar(lb=A[i], ub=B[i], obj=0.0, vtype=COPT.CONTINUOUS, name="t_%d_%d" % (i, r))
                else:
                    t[i, r] = m.addVar(lb=A[0], ub=B[0], obj=0.0, vtype=COPT.CONTINUOUS, name="t_%d_%d" % (i, r))
        # 设置目标函数最小化
        m.setObjSense(COPT.MINIMIZE)

        # 每个客户都必须被有且只有一辆车服务，使用可能离开点i的路径刻画
        for i in range(1, N - 1):
            expr = LinExpr()
            for j in range(1, N):
                if i != j:
                    for r in range(R):
                        expr.addTerms(x[i, j, r], 1)
            m.addConstr(expr == 1, name="Customer_%d" % (i))

        # 配送中心或车场发出的车辆要等于回来的车辆
        for r in range(R):
            m.addConstr(sum(x[0, j, r] for j in range(1, N - 1)) - sum(x[i, N - 1, r] for i in range(1, N - 1)) == 0,
                        "DepotFlowConstr_%d" % r)

        # 客户点的流平衡约束
        for r in range(R):
            for j in range(1, N - 1):
                lh = LinExpr()
                rh = LinExpr()
                for i in range(N):
                    if i != j:
                        if i != N - 1:
                            lh.addTerms(x[i, j, r], 1)
                        if i != 0:
                            rh.addTerms(x[j, i, r], 1)
                m.addConstr(lh - rh == 0, "PointFlowConstr_%d_%d" % (j, r))

        # MTZ约束控制容量变化，并避免环路
        for r in range(R):
            for i in range(1, N - 1):
                for j in range(1, N):
                    if i != j:
                        m.addConstr(q[i] + Demand[i] - q[j] <= (1 - x[i, j, r]) * 400,
                                    "Capacity_%d_%d_%d" % (i, j, r))

        # 同理构建时间变化约束
        for r in range(R):
            for i in range(0, N - 1):
                for j in range(1, N):
                    if i != j:
                        if i == 0:
                            if j == N - 1:
                                continue
                            else:
                                m.addConstr(t[i, r] + ST[i] + Distance[i][j] - t[j, r] <= (1 - x[i, j, r]) * 300,
                                            "Time_%d_%d_%d" % (i, j, r))
                        else:
                            if j == N - 1:
                                m.addConstr(t[i, r] + ST[i] + Distance[i][0] - t[j, r] <= (1 - x[i, j, r]) * 300,
                                            "Time_%d_%d_%d" % (i, j, r))
                            else:
                                m.addConstr(t[i, r] + ST[i] + Distance[i][j] - t[j, r] <= (1 - x[i, j, r]) * 300,
                                            "Time_%d_%d_%d" % (i, j, r))
        # 定义一个车程是一条路径约束
        for r in range(R):
            lh = LinExpr()
            for j in range(1, N - 1):
                lh.addTerms(x[0, j, r], 1.0)
            m.addConstr(lh <= 1.0, "RouteBound_%d" % r)
        # 车程分配约束
        for r in range(R):
            lh = LinExpr()
            for k in range(K):
                lh.addTerms(y[k, r], 1.0)
            for j in range(1, N - 1):
                lh.addTerms(x[0, j, r], -1.0)
            m.addConstr(lh == 0, "AssignmentEqual_%d" % r)
        # 车辆使用约束
        for k in range(K):
            lh = LinExpr()
            for r in range(R):
                lh.addTerms(y[k, r], 1.0)
            m.addConstr(lh <= f[k] * 500, "UseVehicle_%d" % k)
        # 表示非紧前的M约束
        for k in range(K):
            for i in range(R):
                for j in range(R):
                    if i != j:
                        m.addConstr(t[N - 1, i] + Tau - t[0, j] <= (3 - z[i, j, k] - y[k, i] - y[k, j]) * 200,
                                    "DisjunctiveLeft_%d_%d_%d" % (i, j, k))
                        m.addConstr(t[0, i] - Tau - t[N - 1, j] >= -(2 + z[i, j, k] - y[k, i] - y[k, j]) * 200,
                                    "DisjunctiveRight_%d_%d_%d" % (i, j, k))
        log_file_name = 'MTVRPTW2.log'
        m.setLogFile(log_file_name)  # 设置输出路径
        m.setParam(COPT.Param.AbsGap, 0)  # 设置 AbsGap 容差为 0
        m.solve()  # 命令求解器进行求解

        print('Obj:', m.ObjVal)  # 输出最优值
        # 输出最优解
        for k in range(K):
            if f[k].x >= 0.9:
                print("-------------第%d辆车-------------" % k, end="\n")
                for r in range(R):
                    if y[k, r].x >= 0.9:
                        Count = 1
                        for i in range(1, N - 1):
                            A = True
                            if x[0, i, r].x >= 0.9:
                                print("第%d条路径为：" % Count, end="\n")
                                print("场站(%s)-客户%d-" % (t[0, r].x, i), end="")
                                Cur = i
                                while (A):
                                    for j in range(1, N):
                                        if Cur != j and x[Cur, j, r].x >= 0.9:
                                            if j != N - 1:
                                                print("客户%d-" % j, end="")
                                                Cur = j
                                            else:
                                                print("场站(%s)" % t[j, r].x, end="\n")
                                                A = False
                                            break
                                Count += 1
        #  输出MTVRPTW2的模型
        m.write("MTVRPTW2.mps")
        m.write("MTVRPTW2.lp")
    except CoptError as e:
        print("Error code " + str(e.retcode) + ": " + str(e))


# 开始在Copt中建模
MTVRPTW_2(N,A,B,Demand,Distance,ST,R,K,Tau,F)
