from gurobipy import *

eps = 0.00001
LB = -1000
UB = 1000

"""
测试案例 全量折扣
"""
model = Model()

x_coor = [0, 20, 30, 40]
cost = [2, 1.5, 1.2]

pi = {}
u = {}
for i in range(1, 4):
    pi[i] = model.addVar(lb=0, ub=1000, vtype=GRB.CONTINUOUS, name='pi_'+str(i))
    u[i] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name='u_' + str(i))

x = model.addVar(lb=0, ub=1000, vtype=GRB.CONTINUOUS, name='x')
y = model.addVar(lb=0, ub=1000, vtype=GRB.CONTINUOUS, name='y')

model.setObjective(0, GRB.MINIMIZE)

lhs = LinExpr()
for key in pi.keys():
    lhs.addTerms(1, pi[key])
model.addConstr(x == lhs)

lhs = LinExpr()
for key in pi.keys():
    lhs.addTerms(cost[key-1], pi[key])
model.addConstr(y == lhs)

model.addConstr(pi[1] <= x_coor[1] * u[1])

for i in range(2, 4):
    model.addConstr(x_coor[i-1] * u[i] <= pi[i])
    model.addConstr(pi[i] <= x_coor[i] * u[i])

model.addConstr(u[1] + u[2] + u[3] == 1)

model.addConstr(x == 35)

model.write('all_discount.lp')
model.optimize()
print('----------测试案例11------------')
print('{} = {}'.format(x.VarName, x.x))
print('{} = {}'.format(y.VarName, y.x))

for key in pi.keys():
    print('{} = {}'.format(pi[key].VarName, pi[key].x))