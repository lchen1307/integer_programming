from gurobipy import *
from random import randint
from math import floor

from gurobipy.gurobipy import GRB

# Number of diferent width products
itemNum = 3

# Set Length of the rolls
Length = 80

# Length and demands of each product
item_length = {i: randint(10, floor(Length/3)) for i in range(itemNum)}

# Demands of each product
demand = {i: randint(5, 50) for i in range(itemNum)}

# Construct the subproblem
SP = Model("SubProblem")
SPvars = SP.addVars(itemNum, obj = -1, vtype = GRB.INTEGER, name = 'w')
SP.addConstr(SPvars.prod(item_length) <= Length)
SP.update()

# Construct the master problem
MP = Model("MasterProblem")
slack = MP.addVars(itemNum, name = 'slackVar', obj = 10000)
cons = MP.addConstrs(slack[i] >= demand[i] for i in range(itemNum))
MP.write('04_initial_MP.lp')
MP.optimize()

# We will loop as long as we find interesting variables
MP.Params.OutputFlag = 0
Iter = 0
eps = -0.0001
while MP.status == GRB.OPTIMAL:
    pi = { i : -cons[i].Pi for i in range(itemNum)}
    SP.setObjective(SPvars.prod(pi))
    SP.optimize()

    if SP.status != GRB.OPTIMAL:
        raise('Unxpected optimizationn status')

    if (1 + SP.ObjVal > eps):
        break

    # print log each 10 iterations
    if Iter % 10 == 0:
        print('Iteration MasterValue PricingValue')
    print('%8d %12.5g %12.5g' % (Iter, MP.ObjVal, SP.ObjVal))
    Iter += 1

    # Using solution, build new variable
    col = Column()
    for j in range(itemNum):
        col.addTerms(SPvars[j].X, cons[j])
    MP.addVar(obj = 1, column = col, name = 'new_x' + str(Iter))
    MP.optimize()
MP.write('04_final_MP.lp')
RelaxedMP = MP.ObjVal

MP.Params.OutputFlag = 1
Mvars = MP.getVars()
for v in Mvars:
    v.Vtype = GRB.INTEGER
MP.optimize()
print('Objective = \t', MP.ObjVal)
for var in MP.getVars():
    print(var.varName, '=\t', var.x)