"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 带软时间窗的车辆路径规划问题（VRPSTW2）- COPT - Python接口代码实现
author: 杉数科技
date: 2022-10-11
institute: 杉数科技 
"""

from coptpy import *
import math

# 读取算例，只取了前20个客户点
f = open('r101_VRPTW.txt', 'r')
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
# 设置最大可迟到时间，及其惩罚
MAX_B = 10
Cost_B = 0.5
# 设置最大可早到并开始服务时间，及其惩罚
MAX_A = 15
Cost_A = 0.3


def VRPSTW_2(N,A,B,Demand,Distance,ST,MAX_B,Cost_B,MAX_A,Cost_A):
    try:
        env = Envr()
        m = env.createModel("VRPSTW2")

        # 创建变量
        x = {}
        q = {}
        t = {}
        Beta = {}
        Alpha = {}
        # 因为复制了配送中心点为{o，d}，所以点的总个数是N+1，默认不存在以{o}为终点和{d}为起点的弧。
        N = N + 1

        for i in range(N):
            # 创建车辆到达点i剩余容量变量q_i,是连续类型变量，算例设置的车辆容量最大为200，因只使用了其中20个点，将容量限制为100。
            q[i] = m.addVar(lb=0.0, ub=100, obj=0.0, vtype=COPT.CONTINUOUS, name="q_%d" % i)
            # 创建迟到时间变量，该变量仅与客户点相关，设定最大迟到时间为10，惩罚成本为0.5每分钟
            Beta[i] = m.addVar(lb=0, ub=MAX_B, obj=Cost_B, vtype=COPT.CONTINUOUS, name="Beta_%d" % i)
            # 同理创建早到时间变量，早到一般没有迟到成本高，而且早到比较常见，因此设置成本为0.3，时间为15
            Alpha[i] = m.addVar(lb=0, ub=MAX_A, obj=Cost_A, vtype=COPT.CONTINUOUS, name="Alpha_%d" % i)
            # 创建车辆到达时间变量，算例中给出了上下界，其中晚到的时间可以最大为10
            if i in range(1, N - 1):
                t[i] = m.addVar(lb=A[i] - MAX_A, ub=B[i] + MAX_B, obj=0.0, vtype=COPT.CONTINUOUS, name="t_%d" % i)
            else:
                t[i] = m.addVar(lb=A[0], ub=B[0], obj=0.0, vtype=COPT.CONTINUOUS, name="t_%d" % i)

            for j in range(1, N):
                # 默认不存在点i到点i的弧，也不存在点{o}到点{d}的弧。
                if i != j:
                    # 以{o}开始的弧
                    if i == 0 and j != (N - 1):
                        x[i, j] = m.addVar(obj=Distance[i][j], vtype=COPT.BINARY, name="x_%d_%d" % (i, j))
                    # 以{d}结尾的弧
                    elif i != 0 and j == (N - 1):
                        x[i, j] = m.addVar(obj=Distance[i][0], vtype=COPT.BINARY, name="x_%d_%d" % (i, j))
                    # 客户点之间的弧
                    elif i in range(1, N - 1) and j in range(1, N - 1):
                        x[i, j] = m.addVar(obj=Distance[i][j], vtype=COPT.BINARY, name="x_%d_%d" % (i, j))
        # 设置目标函数最小化
        m.setObjSense(COPT.MINIMIZE)

        # 每个客户都必须被有且只有一辆车服务，使用可能离开点i的路径刻画
        for i in range(1, N - 1):
            expr = LinExpr()
            for j in range(1, N):
                if i != j:
                    expr.addTerms(x[i, j], 1)
            m.addConstr(expr == 1, name="Customer_%d" % (i))

        # 配送中心或车场发出的车辆要等于回来的车辆
        m.addConstr(sum(x[0, j] for j in range(1, N - 1)) - sum(x[i, N - 1] for i in range(1, N - 1)) == 0,
                    "DepotFlowConstr")

        # 客户点的流平衡约束
        for j in range(1, N - 1):
            lh = LinExpr()
            rh = LinExpr()
            for i in range(N):
                if i != j:
                    if i != N - 1:
                        lh.addTerms(x[i, j], 1)
                    if i != 0:
                        rh.addTerms(x[j, i], 1)
            m.addConstr(lh - rh == 0, "PointFlowConstr_%d" % j)

        # MTZ约束控制容量变化，并避免环路
        for i in range(1, N - 1):
            for j in range(1, N):
                if i != j:
                    m.addConstr(q[i] + Demand[i] - q[j] <= (1 - x[i, j]) * 200, "Capacity_%d_%d" % (i, j))

        # 同理构建时间变化约束
        for i in range(0, N - 1):
            for j in range(1, N):
                if i != j:
                    if i == 0:
                        if j == N - 1:
                            continue
                        else:
                            m.addConstr(t[i] + ST[i] + Distance[i][j] - t[j] <= (1 - x[i, j]) * 200,
                                        "Time_%d_%d" % (i, j))
                    else:
                        if j == N - 1:
                            m.addConstr(t[i] + ST[i] + Distance[i][0] - t[j] <= (1 - x[i, j]) * 200,
                                        "Time_%d_%d" % (i, j))
                        else:
                            m.addConstr(t[i] + ST[i] + Distance[i][j] - t[j] <= (1 - x[i, j]) * 200,
                                        "Time_%d_%d" % (i, j))
        # 软时间窗上界确定（晚到）
        for i in range(1, N - 1):
            m.addConstr(t[i] - Beta[i] <= B[i], "TimeUB_%d" % i)
        # 软时间窗下界确定（早到）
        for i in range(1, N - 1):
            m.addConstr(t[i] + Alpha[i] >= A[i], "TimeLB_%d" % i)

        log_file_name = 'VRPSTW2.log'
        m.setLogFile(log_file_name)  # 设置输出路径
        m.setParam(COPT.Param.AbsGap, 0)  # 设置 AbsGap 容差为 0
        m.solve()  # 命令求解器进行求解
        print('Obj:', m.ObjVal)  # 输出最优值
        # 输出最优解
        Count = 1
        for i in range(1, N - 1):
            A = True
            if x[0, i].x >= 0.9:
                print("第%d条路径为：" % Count, end="\n")
                print("场站-客户%d" % i, end="")
                if Beta[i].x > 0:
                    print("(迟%d)-" % Beta[i].x, end="")
                elif Alpha[i].x > 0:
                    print("(早%d)-" % Alpha[i].x, end="")
                else:
                    print("-", end="")
                Cur = i
                while (A):
                    for j in range(1, N):
                        if Cur != j and x[Cur, j].x >= 0.9:
                            if j != N - 1:
                                print("客户%d" % j, end="")
                                if Beta[j].x > 0:
                                    print("(迟%d)-" % Beta[j].x, end="")
                                elif Alpha[j].x > 0:
                                    print("(早%d)-" % Alpha[j].x, end="")
                                else:
                                    print("-", end="")
                                Cur = j
                            else:
                                print("场站", end="\n")
                                A = False
                            break
                Count += 1
        #  输出VRPSTW2的模型
        m.write("VRPSTW2.lp")
        m.write("VRPSTW2.mps")
    except CoptError as e:
        print("Error code " + str(e.retcode) + ": " + str(e))


# 开始在Copt中建模
VRPSTW_2(N,A,B,Demand,Distance,ST,MAX_B,Cost_B,MAX_A,Cost_A)


