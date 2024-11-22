"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 数论方程的数学规划模型--Gurobi Python接口代码实现
author: 蔡茂华
date: 2022-09-08
"""


from gurobipy import *

m = Model("test")#创建模型对象
m.setParam('NonConvex', 2) #设置非凸模型求解参数为2

#创建决策变量(均为整数)
a  = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="a")
b  = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="b")
c  = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="c")
m1 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="m1")
m2 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="m2")
m3 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="m3")
m4 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="m4")
m5 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="m5")
m6 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="m6")
m7 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="m7")
u1 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="u1")
u2 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="u2")
u3 = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="u3")
abs_u1 = m.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="abs_u1")
abs_u2 = m.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="abs_u2")
abs_u3 = m.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.INTEGER,name="abs_u3")
lhs = m.addVar(vtype=GRB.INTEGER,name="lhs")
rhs = m.addVar(vtype=GRB.INTEGER,name="rhs")

#辅助变量赋值
m.addConstr(m1 == a*a)    #a*a
m.addConstr(m2 == b*b)    #b*b
m.addConstr(m3 == c*c)    #c*c
m.addConstr(m4 == a*b)    #a*b
m.addConstr(m5 == a*c)    #a*c
m.addConstr(m6==b*c)    #b*c

#约束14.65
m.addConstr(lhs==m1*(a+b+c)+3*m4*c+(a+b+c)*m2+m3*(a+b+c))    #左项式
m.addConstr(rhs==4*(m1*(b+c)+m2*(a+c)+(a+b)*m3+2*c*m4))        #右项式
m.addConstr(lhs==rhs)   #左右项式相等

#约束14.63——14.65
m.addConstr(u1 == a + b)
m.addConstr(u2 == a + c)
m.addConstr(u3 == b + c)

#约束14.66——14.68
m.addGenConstrAbs(abs_u1, u1)
m.addGenConstrAbs(abs_u2, u2)
m.addGenConstrAbs(abs_u3, u3)

#约束14.69
m.addConstr(abs_u1 >= 0.00001)
m.addConstr(abs_u2 >= 0.00001)
m.addConstr(abs_u3 >= 0.00001)

#设置目标函数
m.setObjective(1, GRB.MINIMIZE)

#求解模型
m.optimize()

#输出求解结果
print('a: ',a.x)
print('b: ',b.x)
print('c: ',c.x)