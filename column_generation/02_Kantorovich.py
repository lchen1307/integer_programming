# 下料问题的经典整数规划模型

import gurobipy as gp
from gurobipy import GRB


def cutting_stock_problem(W, d, w):
    """
    解决下料问题的 Python+Gurobi 实现。

    参数：
    W: 原材料的宽度 (单一值)
    d: 每个需求项的需求量 (列表)
    w: 每个需求项的长度 (列表)

    返回：
    优化的解，包括使用的原材料数量以及每种需求的切割数量。
    """

    I = range(len(d))  # 成品板材的种类集合
    J = range(120)  # 假设最多使用100块原材料，可以根据需求修改这个值

    # 创建模型
    model = gp.Model("Kantorovich")

    # 决策变量
    x = model.addVars(I, J, vtype=GRB.INTEGER, name="x")  # x_ij: number of times item i is cut on roll k
    y = model.addVars(J, vtype=GRB.BINARY, name="y")  # y_j: if roll j is cut, 0 otherwise

    # 目标函数：最小化使用的原材料数量
    model.setObjective(gp.quicksum(y[j] for j in J), GRB.MINIMIZE)

    # 约束条件1：满足每个成品板材的需求量
    for i in I:
        model.addConstr(gp.quicksum(x[i, j] for j in J) >= d[i], name=f"demand_{i}")

    # 约束条件2：每块原材料的切割长度不能超过其最大长度 W
    for j in J:
        model.addConstr(gp.quicksum(w[i] * x[i, j] for i in I) <= W * y[j], name=f"capacity_{j}")

    # 优化模型
    model.optimize()

    # 输出结果
    if model.status == GRB.OPTIMAL:
        print(f"最优目标值：{model.objVal}")
        for j in J:
            if y[j].x > 0.5:  # 如果y_j为1，表示该原材料被使用
                print(f"原材料 {j} 被使用:")
                for i in I:
                    if x[i, j].x > 0:
                        print(f"  切割 {x[i, j].x} 个长度为 {w[i]} 的需求 {i}")
    else:
        print("没有找到最优解")

    # 打印全部决策变量的取值（检查模型时使用，一般可以直接注释掉）
    # for v in model.getVars():
    #     print('%s %g' % (v.varName, v.x))

# 示例输入
W = 100  # 原材料的长度
d = [50, 40, 36, 20]  # 每个成品板材的需求数量
w = [51, 21, 54, 53]  # 每个成品板材的长度

# 调用函数求解
cutting_stock_problem(W, d, w)
