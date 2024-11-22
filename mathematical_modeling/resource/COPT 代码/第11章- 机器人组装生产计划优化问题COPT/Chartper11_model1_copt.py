"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 机器人组装生产计划优化问题（问题一） - COPT Python接口代码实现
author: 杉数科技
date:2022-10-11
"""

import coptpy as copt

def problem1_build_model_and_solve():
    NW = [39, 36, 38, 40, 37, 33, 40]  # WPCR需求量
    T = [4500, 2500, 2750, 2100, 2500, 2750, 1500]  # 每天工时
    t = [3, 5, 5]  # 每个工件花费的工时
    S = [120, 160, 180]  # ABC准备费
    Sz = [40, 60, 50, 80, 100, 60, 40, 70]  # 小组件准备费
    p = [2, 1.5, 1.7]  # ABC存储费
    pz = [5, 3, 6, 4, 5, 3, 2, 3]  # 小组件存储费
    Sw = 240  # WPCR准备费
    pw = 5  # WPCR存储费
    k = [3, 4, 5]  # 一个WPCR需要的ABC数量
    h = [[6, 8, 2, 0, 0, 0, 0, 0],
         [0, 0, 0, 2, 4, 0, 0, 0],
         [0, 0, 0, 0, 0, 8, 2, 12]]
    x = {}
    y = {}
    w = {}
    yw = {}
    l = {}
    lw = {}
    lz = {}
    z = {}
    yz = {}

    # 创建COPT模型
    env = copt.Envr()
    model = env.createModel()

    for i in range(7):
        for j in range(3):
            name = f'x_{i}_{j}'
            x[i, j] = model.addVar(lb=0, ub=5000, vtype=copt.COPT.INTEGER, name=name)

    for i in range(8):
        for j in range(3):
            name = f'y_{i}_{j}'
            y[i, j] = model.addVar(lb=0, ub=5000, vtype=copt.COPT.INTEGER, name=name)

    for i in range(7):
        name = f'w_{i}'
        w[i] = model.addVar(lb=0, ub=5000, vtype=copt.COPT.INTEGER, name=name)

    for i in range(8):
        name = f'yw_{i}'
        yw[i] = model.addVar(lb=0, ub=5000, vtype=copt.COPT.INTEGER, name=name)

    for i in range(7):
        for j in range(3):
            name = f'l_{i}_{j}'
            l[i, j] = model.addVar(lb=0, ub=1, vtype=copt.COPT.INTEGER, name=name)

    for i in range(7):
        name = f'lw_{i}'
        lw[i] = model.addVar(lb=0, ub=1, vtype=copt.COPT.INTEGER, name=name)

    for i in range(7):
        for j in range(8):
            name = f'lz_{i}_{j}'
            lz[i, j] = model.addVar(lb=0, ub=1, vtype=copt.COPT.INTEGER, name=name)

    for i in range(7):
        for j in range(8):
            name = f'z_{i}_{j}'
            z[i, j] = model.addVar(lb=0, ub=5000, vtype=copt.COPT.INTEGER, name=name)

    for i in range(8):
        for j in range(8):
            name = f'yz_{i}_{j}'
            yz[i, j] = model.addVar(lb=0, ub=5000, vtype=copt.COPT.INTEGER, name=name)

    # 目标函数
    obj = sum(l[i, j] * S[j] + y[i, j] * p[j] for i in range(7) for j in range(3)) + sum(
        yw[i] * pw + lw[i] * Sw for i in range(7)) + sum(
        lz[i, k] * Sz[k] + yz[i, k] * pz[k] for i in range(7) for k in range(8))
    model.setObjective(obj, copt.COPT.MINIMIZE)

    # 约束
    # 周一库存限制约束
    for j in range(3):
        model.addConstr(y[0, j] == 0)
    model.addConstr(yw[0] == 0)
    for i in range(8):
        model.addConstr(yz[0, i] == 0)

    # 周日库存限制约束
    for j in range(3):
        model.addConstr(y[7, j] == 0)
    model.addConstr(yw[7] == 0)
    for i in range(8):
        model.addConstr(yz[7, i] == 0)

    # 每日工时限制
    for i in range(7):
        model.addConstr(sum(x[i, j] * t[j] for j in range(3)) <= T[i])

    # i+1天WPCR库存公式
    for i in range(6):
        model.addConstr(yw[i + 1] == w[i] + yw[i] - NW[i])

    # 大组件库存公式
    for i in range(6):
        for j in range(3):
            model.addConstr(y[i + 1, j] == x[i, j] + y[i, j] - w[i] * k[j])

    # i+1天小组件库存公式
    for i in range(6):
        model.addConstr(yw[i + 1] == w[i] + yw[i] - NW[i])

    # 当天生产量和初始库存量之和大于需求量
    for i in range(7):
        model.addConstr(w[i] + yw[i] >= NW[i])

    # 用于生产WPCR的大组件数量限制
    for i in range(7):
        for j in range(3):
            model.addConstr(k[j] * w[i] <= x[i, j] + y[i, j])

    # 用于生产的小组件之和不得超过限制
    for i in range(7):
        for j in range(8):
            for q in range(3):
                model.addConstr(h[q][j] * x[i, q] <= z[i, j] + yz[i, j])

    # 判断是否生产大组件（线性化后）
    for i in range(7):
        for j in range(3):
            model.addConstr(x[i, j] >= 0.5 * l[i, j])
            model.addConstr(x[i, j] <= 5000 * l[i, j])

    # 判断是否生产WPCR(线性化后)
    for i in range(7):
        model.addConstr(w[i] >= 0.5 * lw[i])
        model.addConstr(w[i] <= 5000 * lw[i])

    # 判断是否生产小组件(线性化后)
    for i in range(7):
        for j in range(8):
            model.addConstr(z[i, j] >= 0.5 * lz[i, j])
            model.addConstr(z[i, j] <= 5000 * lz[i, j])

    # 小组件每天起始库存量
    for i in range(7):
        for q in range(8):
            model.addConstr(yz[i + 1, q] == z[i, q] + yz[i, q] - sum(h[j][q] * x[i, j] for j in range(3)))

    model.solve()

    print(model.objVal)
    print('w:', end=' ')
    for i in range(7):
        print(w[i].x, end='  ')
    print(sum(w[i].x for i in range(7)))

    for i in range(3):
        print(f'大组件_{i}:', end=' ')
        for j in range(7):
            print(x[j, i].x, end='  ')
        print(sum(x[j, i].x for j in range(7)))

    print('生产准备费:', end=' ')
    for i in range(7):
        obj_1 = sum(l[i, j].x * S[j] for j in range(3)) + lw[i].x * Sw + sum(lz[i, k].x * Sz[k] for k in range(8))
        print(obj_1, end='  ')
    print()
    print('库存费:', end=' ')
    for i in range(7):
        obj_2 = sum(y[i, j].x * p[j] for j in range(3)) + yw[i].x * pw + sum(yz[i, k].x * pz[k] for k in range(8))
        print(obj_2, end='  ')


problem1_build_model_and_solve()
