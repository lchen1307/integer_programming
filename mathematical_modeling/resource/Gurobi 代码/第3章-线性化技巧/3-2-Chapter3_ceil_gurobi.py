from gurobipy import *

#创建模型
model = Model('Counting example')

#定义变量
x = model.addVar(lb = -GRB.INFINITY,
                 ub = GRB.INFINITY,
                 vtype = GRB.CONTINUOUS,
                 name = "x")
y = model.addVar(lb = 0,
                 ub =10,
                 vtype = GRB.INTEGER,
                 name = "y")

model.setObjective(0, GRB.MINIMIZE)

#添加线性化约束
model.addConstr(y >=x/1800, name="round_1")
model.addConstr(y-1 <= x/1800, name="round_2")

#设置x的取值为2000
model.addConstr( x == 2000, name="round_2")
model.optimize()

print('y is: {}'.format(y.x))