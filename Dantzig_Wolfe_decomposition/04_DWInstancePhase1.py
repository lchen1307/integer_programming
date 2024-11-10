from gurobipy import *
from gurobipy import GRB


SP1 = Model('SubProblem 1')
x = {}
for i in range(2):
    x[i + 1] = SP1.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'x' + str(i + 1))

SP1.setObjective(0 * x[1] + 0 * x[2] + 1, GRB.MAXIMIZE)
# SP1.setObjective(90 * x[1] + 80 * x[2], GRB.MAXIMIZE)

SP1.addConstr(3 * x[1] + x[2] <= 12)
SP1.addConstr(2 * x[1] + x[2] <= 10)
SP1.optimize()
print('Objective = \t', SP1.ObjVal)
for var in SP1.getVars():
    print(var.varName, '\t', var.x)


SP2 = Model('SubProblem 2')
xx = {}
for i in range(2):
    xx[i + 1] = SP2.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'xx' + str(i + 1))

SP2.setObjective(0 * xx[1] +0 * xx[2] + 1, GRB.MAXIMIZE)
SP2.addConstr(3 * xx[1] + 2 * xx[2] <= 15)
SP2.addConstr(xx[1] + xx[2] <= 4)
SP2.optimize()
print('Objective = \t', SP2.ObjVal)
for var in SP2.getVars():
    print(var.varName, '\t', var.x)