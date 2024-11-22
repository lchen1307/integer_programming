from gurobipy import *
import numpy as np
#创建模型
model = Model()

#定义变量
x = {}
y = {}

cost_matrix = np.array([[2, 2, 12],
                        [6, 7, 8],
                        [11, 13, 1]])
fixed_cost = [6, 7, 6]

for j in range(3):
    y[j] = model.addVar(lb = 0,ub = 1
                            ,vtype = GRB.BINARY   # decision variable type
                            ,name = "y_" + str(j)
                            )
    for i in range(3):
        x[i,j] = model.addVar(lb = 0,ub = 1
                            ,vtype = GRB.CONTINUOUS   # decision variable type
                            ,name = "x_" + str(i)+"_" + str(j)
                            )

obj = LinExpr(0)
for j in range(3):
    obj.addTerms(fixed_cost[j], y[j])
    for i in range(3):
        obj.addTerms(cost_matrix[i][j], x[i,j])
model.setObjective(obj, GRB.MINIMIZE)

#设置约束
for i in range(3):
    model.addConstr(x[i,0]+x[i,1]+x[i,2] ==1)
    for j in range(3):
        model.addConstr(y[j] - x[i,j] >=0)

model.write('UFLP.lp')
model.optimize()
print('Optimal Obj: {}'.format(model.ObjVal))
for key in y.keys():
            if (y[key].x > 0):
                print('y_{} = {}'.format(key, y[key].x))
for key in x.keys():
            if (x[key].x > 0):
                print('x_{} = {}'.format(key, x[key].x))