from gurobipy import *
from gurobipy import GRB
from networkx.algorithms.bipartite.matching import INFINITY

# 1️⃣ 第一阶段
# 1 初始化主问题
RMP = Model('DW Master Problem')
# RMP.setParam('OutputFlag', 1)

#------------------------start initialization------------------------

# initialize column: Null column

row_num = 3

# Because vars in RMP is added into RMP dynamicly, thus we create an array to store the variables
rmp_vars = []
rmp_vars.append(RMP.addVar(lb = 0.0
                           ,ub = 1000
                           ,obj = 1
                           ,vtype = GRB.CONTINUOUS
                           ,name = 's_1'
                           ,column = None))

rmp_cons = []
var_names = []
col = [-1, 0.001, 0.001]
var_names.append('s_0')

# column to add constraints into RMP
rmp_cons.append(RMP.addLConstr(lhs = rmp_vars[0] * col[0]
                              ,sense = '<='
                              ,rhs = 80
                              ,name = 'rmp_con_central'
                              )
                )

rmp_cons.append(RMP.addLConstr(lhs = rmp_vars[0] * col[1]
                              ,sense = '=='
                              ,rhs = 1
                              ,name = 'rmp_con_convex_combine_mu'
                              )
                )

rmp_cons.append(RMP.addLConstr(lhs = rmp_vars[0] * col[2]
                              ,sense = '=='
                              ,rhs = 1
                              ,name = 'rmp_con_convex_combine_lam'
                              )
                )


RMP.setAttr('ModelSense', GRB.MAXIMIZE)
#------------------------end initialization------------------------
RMP.chgCoeff(rmp_cons[1], rmp_vars[0], 0.0)
RMP.chgCoeff(rmp_cons[2], rmp_vars[0], 0.0)
rmp_cons[1].setAttr('RHS', 0.0)
rmp_cons[2].setAttr('RHS', 0.0)

RMP.write('DW.lp')
RMP.optimize()
rmp_dual = RMP.getAttr('Pi', RMP.getConstrs())
print('rmp_dual =', rmp_dual)


# 2 求解定价子问题1
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


# 3 求解定价子问题2
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


# 4 求解更新后的主问题
# new_columns = [[0, 0, 1, 0]
#               ,[0, 0, 0, 1]
#               ]
# for i in range(2):
#     rmp_col = Column(new_columns[i][1:], rmp_cons)
#     rmp_vars.append(RMP.addVar(lb = 0.0
#                                , ub = GRB.INFINITY
#                                , obj = new_columns[i][0]
#                                , vtype = GRB.CONTINUOUS
#                                , name = 'y' + str(i + 1)
#                                , column = rmp_col
#                                )
#                     )
# # RMP.remove(rmp_vars[0])
# # del rmp_vars[0]
# RMP.update()
# RMP.write('DW.lp')
# RMP.optimize()
# rmp_dual = RMP.getAttr('Pi', RMP.getConstrs())
# print('rmp_dual = ', rmp_dual)
# print('Objective = \t', RMP.ObjVal)
# for var in RMP.getVars():
#     print(var.varName, '\t', var.x)


# 2️⃣ 第二阶段-第一次迭代
# 1 设置第1阶段结束时的主问题中的人工变量为0，求解该主问题
new_columns = [[0, 0, 1, 0]
              ,[0, 0, 0, 1]
              ]
for i in range(2):
    rmp_col = Column(new_columns[i][1:], rmp_cons)
    rmp_vars.append(RMP.addVar(lb = 0.0
                               , ub = 1
                               , obj = new_columns[i][0]
                               , vtype = GRB.CONTINUOUS
                               , name = 'y' + str(i + 1)
                               , column = rmp_col
                               )
                    )
# RMP.remove(rmp_vars[0])
# del rmp_vars[0]
rmp_cons[1].setAttr('RHS', 1)
rmp_cons[2].setAttr('RHS', 1)
RMP.update()
RMP.write('DW.lp')
RMP.optimize()
rmp_dual = RMP.getAttr('Pi', RMP.getConstrs())
print('rmp_dual = ', rmp_dual)
print('Objective = \t', RMP.ObjVal)
for var in RMP.getVars():
    print(var.varName, '\t', var.x)


# 2【第一次迭代】求解定价子问题1
SP1 = Model('SubProblem 1')
x = {}
for i in range(2):
    x[i + 1] = SP1.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'x' + str(i + 1))

SP1.setObjective(90 * x[1] + 80 * x[2], GRB.MAXIMIZE)
SP1.addConstr(3 * x[1] + x[2] <= 12)
SP1.addConstr(2 * x[1] + x[2] <= 10)
SP1.optimize()
print('Objective = \t', SP1.ObjVal)
for var in SP1.getVars():
    print(var.varName, '\t', var.x)


# 3【第一次迭代】求解定价子问题2
SP2 = Model('SubProblem 2')
xx = {}
for i in range(2):
    xx[i + 1] = SP2.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'xx' + str(i + 1))

SP2.setObjective(70 * xx[1] + 60 * xx[2], GRB.MAXIMIZE)
SP2.addConstr(3 * xx[1] +2 * xx[2] <= 15)
SP2.addConstr(xx[1] + xx[2] <= 4)
SP2.optimize()
print('Objective = \t', SP2.ObjVal)
for var in SP2.getVars():
    print(var.varName, '\t', var.x)

# 4【第一次迭代】求解更新后的主问题
new_columns = [[800, 60, 1, 0]
              ,[280, 28, 0, 1]
              ]
for i in range(2):
    rmp_col = Column(new_columns[i][1:], rmp_cons)
    rmp_vars.append(RMP.addVar(lb =0.0
                               , ub = 1
                               , obj = new_columns[i][0]
                               , vtype = GRB.CONTINUOUS
                               , name = 'y' + str(len(rmp_vars))
                               , column = rmp_col)
                    )
RMP.remove(rmp_vars[0])
del rmp_vars[0]
RMP.update()
RMP.write('DW.lp')
RMP.optimize()
# rmp_dual = RMP.getAttr('Pi', RMP.getConstrs())
rmp_dual = [constr.Pi for constr in RMP.getConstrs()]
print('rmp_dual = ', rmp_dual)
print('Objective = \t', RMP.ObjVal)
for var in RMP.getVars():
    print(var.varName, '\t', var.x)


# 3️⃣ 第二阶段-第二次迭代
# 1【第二次迭代】求解定价子问题1
SP1 = Model('SubProblem 1')
x = {}
for i in range(2):
    x[i + 1] = SP1.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'x' + str(i + 1))

SP1.setObjective(10 * x[1] + 20 * x[2] - 200, GRB.MAXIMIZE)
SP1.addConstr(3 * x[1] + x[2] <= 12)
SP1.addConstr(2 * x[1] + x[2] <= 10)
SP1.optimize()
print('Objective = \t', SP1.ObjVal)
for var in SP1.getVars():
    print(var.varName, '\t', var.x)

# 2【第二次迭代】求解定价子问题2
SP2 = Model('SubProblem 2')
xx = {}
for i in range(2):
    xx[i + 1] = SP2.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'xx' + str(i + 1))

SP2.setObjective(0 * xx[1] + 10 * xx[2], GRB.MAXIMIZE)
SP2.addConstr(3 * xx[1] + 2 * xx[2] <= 15)
SP2.addConstr(xx[1] + xx[2] <= 4)
SP2.optimize()
print('Objective = \t', SP2.ObjVal)
for var in SP2.getVars():
    print(var.varName, '\t', var.x)

# 3【第二次迭代】求解更新后的主问题
# new_columns = [[240, 20, 0, 1]
#               ]
# for i in range(1):
#     rmp_col = Column(new_columns[i][1:], rmp_cons)
#     rmp_vars.append(RMP.addVar(lb = 0.0
#                                , ub = 1
#                                , obj = new_columns[i][0]
#                                , vtype = GRB.CONTINUOUS
#                                , name = 'y5'
#                                , column = rmp_col
#                                )
#                     )
# # RMP.remove(rmp_vars[0])
# # del rmp_vars[0]
# RMP.update()
# RMP.write('DW.lp')
# RMP.optimize()
# rmp_dual = RMP.getAttr('Pi', RMP.getConstrs())
# print('rmp_dual = ', rmp_dual)
# print('Objective = \t', RMP.ObjVal)
# for var in RMP.getVars():
#     print(var.varName, '\t', var.x)


# 3️⃣ 第二阶段-第三次迭代
# 1【第三次迭代】求解定价子问题1
SP2 = Model('SubProblem 2')
xx = {}
for i in range(2):
    xx[i + 1] = SP2.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'xx' + str(i + 1))

SP2.setObjective(0 * xx[1] + 10 * xx[2] - 40, GRB.MAXIMIZE)
SP2.addConstr(3 * xx[1] + 2 * xx[2] <= 15)
SP2.addConstr(xx[1] + xx[2] <= 4)
SP2.optimize()
print('Objective = \t', SP2.ObjVal)
for var in SP2.getVars():
    print(var.varName, '\t', var.x)

# 2【第三次迭代】没有新列产生，求解最终的主问题
new_columns = [[240, 20, 0, 1]
              ]
for i in range(1):
    rmp_col = Column(new_columns[i][1:], rmp_cons)
    rmp_vars.append(RMP.addVar(lb = 0.0
                               , ub = INFINITY
                               , obj = new_columns[i][0]
                               , vtype = GRB.CONTINUOUS
                               , name = 'y' + str(i + 7)
                               , column = rmp_col)
                    )
# RMP.remove(rmp_vars[0])
# del rmp_vars[0]
RMP.update()
RMP.write('DW.lp')
RMP.optimize()
rmp_dual = RMP.getAttr('Pi', RMP.getConstrs())
print('rmp_dual = ', rmp_dual)
print('Objective = \t', RMP.ObjVal)
for var in RMP.getVars():
    print(var.varName, '\t', var.x)
