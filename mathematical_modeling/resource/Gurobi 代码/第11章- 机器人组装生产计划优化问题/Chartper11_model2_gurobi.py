"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 机器人组装生产计划优化问题（问题二） - Gurobi Python接口代码实现
author: 蔡茂华
date: 2022-8-20
"""


import gurobipy

def problem2_build_model_and_solve():
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
    model = gurobipy.Model('model')

    for i in range(7):
        for j in range(3):
            name = 'x_' + str(i) + '_' + str(j)
            x[i, j] = model.addVar(lb=0, ub=500000, vtype=gurobipy.GRB.INTEGER, name=name)

    for i in range(7):
        for j in range(3):
            name = 'y_' + str(i) + '_' + str(j)
            y[i, j] = model.addVar(lb=0, ub=500000, vtype=gurobipy.GRB.INTEGER, name=name)

    for i in range(7):
        name = 'w_' + str(i) + '_' + str(j)
        w[i] = model.addVar(lb=0, ub=500000, vtype=gurobipy.GRB.INTEGER, name=name)

    for i in range(7):
        name = 'yw_' + str(i) + '_' + str(j)
        yw[i] = model.addVar(lb=0, ub=500000, vtype=gurobipy.GRB.INTEGER, name=name)

    for i in range(7):
        for j in range(3):
            name = 'l_' + str(i) + '_' + str(j)
            l[i, j] = model.addVar(lb=0, ub=1, vtype=gurobipy.GRB.INTEGER, name=name)

    for i in range(7):
        name = 'lw_' + str(i)
        lw[i] = model.addVar(lb=0, ub=1, vtype=gurobipy.GRB.INTEGER, name=name)

    for i in range(7):
        for j in range(8):
            name = 'lz_' + str(i) + '_' + str(j)
            lz[i, j] = model.addVar(lb=0, ub=1, vtype=gurobipy.GRB.INTEGER, name=name)

    for i in range(7):
        for j in range(8):
            name = 'z_' + str(i) + '_' + str(j)
            z[i, j] = model.addVar(lb=0, ub=500000, vtype=gurobipy.GRB.INTEGER, name=name)

    for i in range(7):
        for j in range(8):
            name = 'yz_' + str(i) + '_' + str(j)
            yz[i, j] = model.addVar(lb=0, ub=500000, vtype=gurobipy.GRB.INTEGER, name=name)

    # 目标函数
    obj = sum(l[i, j] * S[j] + y[i, j] * p[j] for i in range(7) for j in range(3)) + sum(yw[i] * pw + lw[i] * Sw for i in range(7)) + sum(
        lz[i, k] * Sz[k] + yz[i, k] * pz[k] for i in range(7) for k in range(8))

    # 每日工时限制
    for i in range(7):
        name = 'c1_' + str(i)
        model.addConstr(sum(x[i, j] * t[j] for j in range(3)) <= T[i], name)


    # WPCR的组件 隔天投入生产
    for i in range(7):
        for j in range(3):
            name = 'c2_' + str(i) + '_' + str(j)
            model.addConstr(k[j] * w[i] <= y[i, j], name)
    # 大组件隔天投入生产
    for i in range(7):
        for j in range(3):
            for q in range(8):
                name = 'c2_' + str(i) + '_' + str(j) + '_' + str(q)
                model.addConstr(x[i, j] * h[j][q] <= yz[i, q], name)


    # 判断是否生产大组件（线性化后）
    for i in range(7):
        for j in range(3):
            name1 = 'c3(1)_' + str(i) + '_' + str(j)
            name2 = 'c3(2)_' + str(i) + '_' + str(j)
            model.addConstr(x[i, j] >= 0.5 * l[i, j], name1)
            model.addConstr(x[i, j] <= 500000 * l[i, j], name2)
    # 判断是否生产WPCR(线性化后)
    for i in range(7):
        name1 = 'c4(1)_' + str(i) + '_' + str(j)
        name2 = 'c4(2)_' + str(i) + '_' + str(j)
        model.addConstr(w[i] >= 0.5 * lw[i], name1)
        model.addConstr(w[i] <= 500000 * lw[i], name2)
    # 判断是否生产小组件(线性化后)
    for i in range(7):
        for j in range(8):
            name1 = 'c5(1)_' + str(i) + '_' + str(j)
            name2 = 'c5(2)_' + str(i) + '_' + str(j)
            model.addConstr(z[i, j] >= 0.5 * lz[i, j], name1)
            model.addConstr(z[i, j] <= 500000 * lz[i, j], name2)

    # i+1天WPCR库存公式
    for i in range(6):
        name = 'c6_' + str(i) + '_' + str(j)
        model.addConstr(yw[i + 1] == w[i] + yw[i] - NW[i], name)
    model.addConstr(yw[0] == w[6] + yw[6] - NW[6], 'c7(1)')

    # 大组件库存公式
    for i in range(6):
        for j in range(3):
            name = 'c7(1)_' + str(i) + '_' + str(j)
            model.addConstr(y[i + 1, j] == x[i, j] + y[i, j] - w[i] * k[j], name)
    for j in range(3):
        name = 'c7(2)_' + str(j)
        model.addConstr(y[0, j] == x[6, j] + y[6, j] - w[6] * k[j], name)

    # i+1天小组件库存公式
    for i in range(6):
        for q in range(8):
            name = 'c8(1)_' + str(i) + '_' + str(j)
            model.addConstr(yz[i + 1, q] == z[i, q] + yz[i, q] - sum(h[j][q] * x[i, j] for j in range(3)), name)
    for q in range(8):
        name = 'c8(1)_' + str(q)
        model.addConstr(yz[0, q] == yz[6, q] - sum(h[j][q] * x[6, j] for j in range(3)), name)

    # 当天生产量和初始库存量之和大于需求量
    for i in range(7):
        name = 'c9_' + str(i)
        model.addConstr(w[i] + yw[i] >= NW[i], name)

    # 用于生产WPCR的大组件数量限制
    for i in range(7):
        for j in range(3):
            name = 'c10_' + str(i) + '_' + str(j)
            model.addConstr(k[j] * w[i] <= y[i, j], name)

    model.setObjective(obj, gurobipy.GRB.MINIMIZE)
    model.Params.MipGap=0.000000001
    model.optimize()
    print(model.ObjVal)
    print('w:',end=' ')
    for i in range(7):
        print(w[i].x,end='  ')
    print(sum(w[i].x for i in range(7)))

    for i in range(3):
        print(f'大组件_{i}:',end=' ')
        for j in range(7):
            print(x[j, i].x, end='  ')
        print(sum(x[j, i].x for j in range(7)))

    print('生产准备费:', end=' ')
    for i in range(7):
        obj_1 = sum(l[i, j].x * S[j] for j in range(3)) + lw[i].x * Sw + sum(
            lz[i, k].x * Sz[k]for k in range(8))
        print(obj_1, end='  ')
    print()
    print('库存费:', end=' ')
    for i in range(7):
        obj_2 = sum(y[i, j].x * p[j] for j in range(3)) + yw[i].x * pw + sum(
            yz[i, k].x * pz[k]for k in range(8))
        print(obj_2, end='  ')

problem2_build_model_and_solve()
