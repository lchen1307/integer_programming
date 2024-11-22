"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 带时间窗的电动车辆路径规划问题（EVRPTW）- COPT - Python接口代码实现
author: 杉数科技
date: 2022-10-11
institute: 杉数科技 
"""

import math
from coptpy import *

# 读取EVRPTW的算例，有15个客户点
f = open('r102C15.txt', 'r')
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
# 计算距离矩阵，保留两位小数，并打印矩阵，默认行驶时间和电量消耗就是距离矩阵
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

# 令第16个点为充电站点，并复制多份
C = 15

# = 设置充电速率，假定充满要20分
g = 0.2


def EVRPTW(N,A,B,Demand,Distance,ST,C,g):
    try:
        env = Envr()
        m = env.createModel("EVRPTW")
        # 创建变量
        x = {}
        q = {}
        y = {}
        t = {}
        # 因为复制了配送中心点为{o，d}，并复制了S-1份充电任务，所以点的总个数是N+S，即2N-2个点。
        N = 2 * N - 2
        print(N)
        for i in range(N):
            # 创建车辆到达点i剩余容量变量q_i,是连续类型变量，算例设置的车辆容量最大为200，因只有15个客户点，将容量限制为50。
            q[i] = m.addVar(lb=0.0, ub=50, obj=0.0, vtype=COPT.CONTINUOUS, name="q_%d" % i)
            # 创建车辆到达点i已消耗的电量,电量为0-100
            y[i] = m.addVar(lb=0.0, ub=100, obj=0.0, vtype=COPT.CONTINUOUS, name="y_%d" % i)
            # 创建车辆到达点i的时间变量
            if i in range(0, C):
                t[i] = m.addVar(lb=A[i], ub=B[i], obj=0.0, vtype=COPT.CONTINUOUS, name="t_%d" % i)
            elif i in range(C, N - 1):
                t[i] = m.addVar(lb=A[C], ub=B[C], obj=0.0, vtype=COPT.CONTINUOUS, name="t_%d" % i)
            else:
                t[i] = m.addVar(lb=A[0], ub=B[0], obj=0.0, vtype=COPT.CONTINUOUS, name="t_%d" % i)

            for j in range(1, N):
                # 默认不存在点i到点i的弧，也不存在点{o}到点{d}的弧。
                if i != j:
                    # 以{o}开始的弧
                    if i == 0:
                        # 以客户点为终点
                        if j < C:
                            x[i, j] = m.addVar(obj=Distance[0][j], vtype=COPT.BINARY, name="x_%d_%d" % (i, j))
                        # 以充电站为终点
                        elif j < N - 1:
                            x[i, j] = m.addVar(obj=Distance[0][C], vtype=COPT.BINARY, name="x_%d_%d" % (i, j))
                    # 以客户点开始的弧
                    elif i in range(1, C):
                        # 以客户点为终点
                        if j < C:
                            x[i, j] = m.addVar(obj=Distance[i][j], vtype=COPT.BINARY, name="x_%d_%d" % (i, j))
                        # 以充电站为终点
                        elif j in range(C, N - 1):
                            x[i, j] = m.addVar(obj=Distance[i][C], vtype=COPT.BINARY, name="x_%d_%d" % (i, j))
                        # 以场站为终点
                        elif j == N - 1:
                            x[i, j] = m.addVar(obj=Distance[i][0], vtype=COPT.BINARY, name="x_%d_%d" % (i, j))
                    # 以充电站开始的弧
                    elif i in range(C, N - 1):
                        # 以客户点为终点
                        if j in range(1, C):
                            x[i, j] = m.addVar(obj=Distance[C][j], vtype=COPT.BINARY, name="x_%d_%d" % (i, j))
                        # 以场站为终点
                        elif j == N - 1:
                            x[i, j] = m.addVar(obj=Distance[C][0], vtype=COPT.BINARY, name="x_%d_%d" % (i, j))
        # 设置目标函数最小化
        m.setObjSense(COPT.MINIMIZE)

        # 每个客户都必须被有且只有一辆车服务，使用可能离开点i的路径刻画
        for i in range(1, C):
            expr = LinExpr()
            for j in range(1, N):
                if i != j:
                    expr.addTerms(x[i, j], 1)
            m.addConstr(expr == 1, name="Customer_%d" % (i))

        # 配送中心或车场发出的车辆要等于回来的车辆
        m.addConstr(sum(x[0, j] for j in range(1, N - 1)) - sum(x[i, N - 1] for i in range(1, N - 1)) == 0,
                    "DepotFlowConstr")

        # 流平衡约束
        for j in range(1, N - 1):
            lh = LinExpr()
            rh = LinExpr()
            # 流量平衡点是客户点
            if j < C:
                for i in range(N):
                    if i != j:
                        if i != N - 1:
                            lh.addTerms(x[i, j], 1)
                        if i != 0:
                            rh.addTerms(x[j, i], 1)
                m.addConstr(lh - rh == 0, "PointFlowConstr_%d" % j)
            # 流量平衡点是充电站
            else:
                for i in range(1, C):
                    lh.addTerms(x[i, j], 1)
                    rh.addTerms(x[j, i], 1)
                m.addConstr(lh + x[0, j] == rh + x[j, N - 1], "PointFlowConstr_%d" % j)

        # MTZ约束控制容量变化，并避免环路
        for i in range(0, N - 1):
            for j in range(1, N):
                if i != j:
                    # 如果是客户开始的弧：
                    if i in range(1, C):
                        m.addConstr(q[i] + Demand[i] - q[j] <= (1 - x[i, j]) * 500, "Capacity_%d_%d" % (i, j))
                    # 如果是充电站开始的弧：
                    elif i >= C and j in range(1, C):
                        m.addConstr(q[i] + Demand[C] - q[j] <= (1 - x[i, j]) * 500, "Capacity_%d_%d" % (i, j))
                    # 容量约束只包含上述两类有效约束

        # 同理构建时间变化约束
        for i in range(0, N - 1):
            for j in range(1, N):
                if i != j:
                    # 如果是车场开始的弧：
                    if i == 0:
                        if j < C:
                            m.addConstr(Distance[i][j] - t[j] <= (1 - x[i, j]) * 500, "Time_%d_%d" % (i, j))
                        elif j in range(C, N - 1):
                            m.addConstr(Distance[i][C] - t[j] <= (1 - x[i, j]) * 500, "Time_%d_%d" % (i, j))
                    # 如果是客户点开始的弧：
                    elif i in range(1, C):
                        if j in range(1, C):
                            m.addConstr(t[i] + ST[i] + Distance[i][j] - t[j] <= (1 - x[i, j]) * 500,
                                        "Time_%d_%d" % (i, j))
                        elif j in range(C, N - 1):
                            m.addConstr(t[i] + ST[i] + Distance[i][C] - t[j] <= (1 - x[i, j]) * 500,
                                        "Time_%d_%d" % (i, j))
                        else:
                            m.addConstr(t[i] + ST[i] + Distance[i][0] - t[j] <= (1 - x[i, j]) * 500,
                                        "Time_%d_%d" % (i, j))
                    # 如果是充电站开始的弧：
                    elif i in range(C, N - 1):
                        if j in range(1, C):
                            m.addConstr(t[i] + y[i] * g + Distance[C][j] - t[j] <= (1 - x[i, j]) * 500,
                                        "Time_%d_%d" % (i, j))
                        elif j == N - 1:
                            m.addConstr(t[i] + y[i] * g + Distance[C][0] - t[j] <= (1 - x[i, j]) * 500,
                                        "Time_%d_%d" % (i, j))
        # 同理构建电量变化约束：
        for i in range(0, N - 1):
            for j in range(1, N):
                if i != j:
                    # 如果是场站开始的弧：
                    if i == 0:
                        if j in range(1, C):
                            m.addConstr(Distance[i][j] - y[j] <= (1 - x[i, j]) * 500, "Ele_%d_%d" % (i, j))
                        elif j in range(C, N - 1):
                            m.addConstr(Distance[i][C] - y[j] <= (1 - x[i, j]) * 500, "Ele_%d_%d" % (i, j))
                    # 如果是客户点开始的弧：
                    elif i in range(1, C):
                        if j in range(1, C):
                            m.addConstr(y[i] + Distance[i][j] - y[j] <= (1 - x[i, j]) * 500, "Ele_%d_%d" % (i, j))
                        elif j in range(C, N - 1):
                            m.addConstr(y[i] + Distance[i][C] - y[j] <= (1 - x[i, j]) * 500, "Ele_%d_%d" % (i, j))
                        else:
                            m.addConstr(y[i] + Distance[i][0] - y[j] <= (1 - x[i, j]) * 500, "Ele_%d_%d" % (i, j))
                    # 如果是充电站开始的弧：
                    elif i in range(C, N - 1):
                        if j in range(1, C):
                            m.addConstr(Distance[C][j] - y[j] <= (1 - x[i, j]) * 500, "Ele_%d_%d" % (i, j))
                        elif j == N - 1:
                            m.addConstr(Distance[C][0] - y[j] <= (1 - x[i, j]) * 500, "Ele_%d_%d" % (i, j))
        log_file_name = 'EVRPTW.log'
        m.setLogFile(log_file_name)  # 设置输出路径
        m.setParam(COPT.Param.AbsGap, 0)  # 设置 AbsGap 容差为 0
        m.solve()  # 命令求解器进行求解
        print('Obj:', m.ObjVal)  # 输出最优值
        # 输出最优解
        Count = 1
        for i in range(1, N - 1):
            A = True
            if x[0, i].x >= 0.9:
                if i in range(1, C):
                    print("第%d条路径为：" % Count, end="\n")
                    print("场站-客户%d-" % i, end="")
                else:
                    print("第%d条路径为：" % Count, end="\n")
                    print("场站-充电任务%d-" % i, end="")
                Cur = i
                while (A):
                    for j in range(1, N):
                        if Cur != j and x[Cur, j].x >= 0.9:
                            if j in range(1, C):
                                print("客户%d-" % j, end="")
                                Cur = j
                            elif j in range(C, N - 1):
                                print("充电任务%d-" % j, end="")
                                Cur = j
                            else:
                                print("场站", end="\n")
                                A = False
                            break
                Count += 1
        #  输出EVRPTW的模型
        m.write("EVRPTW.lp")
        m.write("EVRPTW.mps")
    except CoptError as e:
        print("Error code " + str(e.retcode) + ": " + str(e))


# 开始在Copt中建模
EVRPTW(N,A,B,Demand,Distance,ST,C,g)
