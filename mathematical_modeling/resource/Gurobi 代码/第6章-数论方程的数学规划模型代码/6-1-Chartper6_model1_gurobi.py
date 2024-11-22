"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 数论方程的数学规划模型--Gurobi Python接口代码实现
author: 蔡茂华
date: 2022-09-08
"""

from gurobipy import *

# 创建模型对象
m = Model("pissa")

# 设置非凸模型求解参数为2
m.setParam('NonConvex', 2)

# 创建决策变量（a,b,c为正整数）
a  = m.addVar(lb=0, vtype=GRB.INTEGER, name="a")
b  = m.addVar(lb=0, vtype=GRB.INTEGER, name="b")
c  = m.addVar(lb=0, vtype=GRB.INTEGER, name="c")
m1 = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name="m1")
m2 = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name="m2")
m3 = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name="m3")

# 添加约束
#约束14.17
m.addConstr(a >= 1, "c1")
m.addConstr(b >= 1, "c1")
m.addConstr(c >= 1, "c1")

#约束14.13—14.15
m.addConstr(a == m1 * (b + c))
m.addConstr(b == m2 * (a + c))
m.addConstr(c == m3 * (a + b))

#约束14.12
m.addConstr(m1 + m2 + m3 - 4 == 0)

# 设置目标函数
m.setObjective(1, GRB.MINIMIZE)

# 求解模型
m.optimize()

# 输出求解结果
print('a: ',a.x)
print('b: ',b.x)
print('c: ',c.x)