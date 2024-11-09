from gurobipy import *
from gurobipy import GRB

DW_model = Model('DW Decomposition')
mu = {}
lam = {}
s = {}

# Add variables
s[1] = DW_model.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 's_1')

for i in range(4):
    mu[i + 1] = DW_model.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'mu_' + str(i + 1))

for i in range(3):
    lam[i + 1] = DW_model.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'lam_' + str(i + 1))

# Add objective function
obj = LinExpr(0)
obj = 360 * mu[2] + 660 * mu[3] + 800 * mu[4] + 280 * lam[2] + 240 * lam[3]
DW_model.setObjective(obj, GRB.MAXIMIZE)

# Add constraints
DW_model.addConstr(32 * mu[2] + 52 * mu[3] + 60 * mu[4] + 27 * lam[2] + 20 * lam[3] + s[1] == 80, name = 'c1')
DW_model.addConstr(mu[1] + mu[2] + mu[3] + mu[4] == 1, name = 'c2')
DW_model.addConstr(lam[1] + lam[2] + lam[3] == 1, name = 'c3')

# Solve model
DW_model.optimize()

for var in DW_model.getVars():
    if (var.x > 0):
        print(var.varName, ':', var.x)