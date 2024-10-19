# 本代码为《运筹优化常用模型、算法及案例实战》13.3.1节的示例代码
# 作用：求解定价子问题，找到检验数为负的切割方案

from gurobipy import *
from gurobipy.gurobipy import GRB

# Number of different width products
itemNum = 3

# Base width of the rolls
Length = 80

# item width and demand
l = {0: 10, 1: 19, 2: 11}
d = {0: 46, 1: 43, 2: 22}


# Construct the subproblem
SP = Model('subproblem')
SPvars = SP.addVars(itemNum, obj = -1, vtype = GRB.INTEGER, name = 'w') # set objective - a1 - a2 - a3
SP.addConstr(SPvars.prod(l) <= Length)
SP.write('03_subproblem.lp')
SP.update()


# Construct initial master problem
MP = Model('Master Problem')
x = {}
for i in range(5):
    x[i] = MP.addVar(obj = 1, vtype = GRB.CONTINUOUS, name = 'x_' + str(i))
cons = {}
cons[0] = MP.addConstr(8 * x[0] + 6 * x[1] + 6 * x[2] + 5 * x[3] + 5 * x[4] >= 46, name = 'c_1')
cons[1] = MP.addConstr(x[1] + x[3] + 2 * x[4] >= 22, name = 'c_2')
cons[2] = MP.addConstr(x[2] + x[3] >= 43, name = 'c_3')
MP.write('03_initial_MP.lp')
MP.optimize()


# We will loop as long as we find interesting variables
MP.params.OutputFlag = 0
Iter = 0
eps = -0.0001
while(MP.Status == GRB.OPTIMAL):
    pi = { i : -cons[i].Pi for i in range(itemNum)}
    SP.setObjective(SPvars.prod(pi))
    SP.optimize()

    # This should not happen, but better safe than sorry
    if SP.Status != GRB.OPTIMAL:
        raise('Unxpected optimizationn status')

    # Reduced cost is c_i - p_i * A_{*i}
    # - in our case, A_{*i} is the proposed solution in SP
    # - c_i is the cost of Master Problem for the column
    # - p_i comes from the duals in MP

    # If improvement is too small, we stop
    if (1 + SP.ObjVal > eps):
        break

    # Log
    if Iter % 10 == 0:
        print('Iteration MasterValue PricingValue')
    print('%8d %12.5g %12.5g' % (Iter, MP.ObjVal, SP.ObjVal))
    Iter += 1

    # Using the solution, build new variable
    col = Column()
    for j in range(itemNum):
        col.addTerms(SPvars[j].X, cons[j])
    MP.addVar(obj = 1, column = col, name = 'new_x' + str(Iter))
    MP.optimize()
MP.write('03_final_MP.lp')
rootbound= MP.ObjBound

MP.params.OutputFlag = 1
Mvars= MP.getVars()
for v in Mvars:
    if v.X > 0.0001:
        v.Vtype = GRB.INTEGER
MP.optimize()