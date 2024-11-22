"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 数论方程的数学规划模型--COPT Python接口代码实现
author: 杉数科技
date: 2022-10-11
"""

from coptpy import *

# 创建环境
env = Envr()

# 创建模型
m = env.createModel(name="number equation")

# 创建决策变量（a,b,c为正整数）
a  = m.addVar(lb=0, vtype=COPT.INTEGER, name="a")
b  = m.addVar(lb=0, vtype=COPT.INTEGER, name="b")
c  = m.addVar(lb=0, vtype=COPT.INTEGER, name="c")
m1 = m.addVar(lb=0, vtype=COPT.CONTINUOUS, name="m1")
m2 = m.addVar(lb=0, vtype=COPT.CONTINUOUS, name="m2")
m3 = m.addVar(lb=0, vtype=COPT.CONTINUOUS, name="m3")

# 添加约束
#约束14.17
m.addConstr(a >= 1, "c1")
m.addConstr(b >= 1, "c1")
m.addConstr(c >= 1, "c1")

#约束14.13—14.15
m.addQConstr(a == m1 * (b + c))
m.addQConstr(b == m2 * (a + c))
m.addQConstr(c == m3 * (a + b))

#约束14.12
m.addConstr(m1 + m2 + m3 - 4 == 0)

# 设置目标函数
m.setObjective(1, COPT.MINIMIZE)

# 求解模型
m.solve()

# 输出求解结果
print('a: ',a.x)
print('b: ',b.x)
print('c: ',c.x)