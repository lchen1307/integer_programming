from gurobipy import *

#创建模型
model = Model('Absolute Value Linearization example')
M = 1000

#定义变量
z = model.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='z')
x = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='z')
x_p = model.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='x_p')
x_n = model.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='x_n')
y = model.addVar(lb = 0,ub = 1,vtype = GRB.BINARY,name = "y")

#设置线性化约束
model.setObjective(z, GRB.MAXIMIZE)
model.addConstr(x == -2)
model.addQConstr(z == x_p+x_n)
model.addConstr(x == x_p-x_n)
model.addConstr(x_p <= M*y)
model.addConstr(x_n <= M*(1-y))

#设置x的取值
model.addConstr(x == -2)
model.optimize()

print('Optimal Obj: {}'.format(model.ObjVal))
print('z = {}'.format(z.x))
print('x_p = {}'.format(x_p.x))
print('x_n = {}'.format(x_n.x))