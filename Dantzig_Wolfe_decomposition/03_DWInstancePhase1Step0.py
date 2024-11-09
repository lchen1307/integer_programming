from gurobipy import *
from gurobipy import GRB

RMP = Model('DW Master Problem')
# RMP.setParam('OutputFlag', 0)

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
