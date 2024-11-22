from gurobipy import *

#创建模型
model = Model()

#定义变量
x_1 =  model.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='x_1')
x_2 =  model.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='x_2')
y =  model.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='y')

#添加线性化约束
model.addConstr(y <= x_1)
model.addConstr(y <= x_2)
model.addConstr(y <= 2)

#设置x,y的取值
model.addConstr(x_1 == 3)
model.addConstr(x_2 == 5)

model.setObjective(y, GRB.MAXIMIZE)

model.optimize()
print('Optimal Obj: {}'.format(model.ObjVal))