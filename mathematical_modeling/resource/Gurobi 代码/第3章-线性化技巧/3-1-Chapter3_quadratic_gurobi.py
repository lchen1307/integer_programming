from gurobipy import *

#创建模型
model = Model()

#定义乘积式变量
x_1 = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name='x_1')
x_2 = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name='x_2')
y = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name='y')

model.setObjective(y, GRB.MAXIMIZE)
#设置线性化约束
model.addConstr(y <= x_1)
model.addConstr(y <= x_2)
model.addConstr(y >= x_1 + x_2 - 1)

#设置x1=1,x2=1
cons1 = model.addConstr(x_1 == 1)
cons2 = model.addConstr(x_2 == 1)

model.optimize()
print('Case 1: x1 = 1, x2 = 1 | {} = {},'.format(y.VarName, y.x))

#设置x1=0,x2=1
model.remove(cons1)
model.remove(cons2)
cons3 = model.addConstr(x_1 == 0)
cons4 = model.addConstr(x_2 == 1)

model.optimize()
print('Case 2: x1 = 0, x2 = 1 | {} = {},'.format(y.VarName, y.x))

#设置x1=0,x2=0
model.remove(cons3)
model.remove(cons4)
cons5 = model.addConstr(x_1 == 0)
cons6 = model.addConstr(x_2 == 0)

model.optimize()
print('Case 3: x1 = 0, x2 = 0 | {} = {}.'.format(y.VarName, y.x))



from gurobipy import *

#创建模型
model = Model()

#定义0-1变量
x_1 = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name='x_1')
x_2 = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name='x_2')
y = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name='y')

model.setObjective(y, GRB.MAXIMIZE)

# 添加二次约束： y = x_1 * x_2
quadexpr = QuadExpr()
quadexpr.addTerms(1, x_1, x_2)
model.addQConstr(y == quadexpr)
cons3 = model.addConstr(x_1 == 0)
cons4 = model.addConstr(x_2 == 1)

model.optimize()
print('Case 4: x1 = 0, x2 = 1 | {} = {}.'.format(y.VarName, y.x))