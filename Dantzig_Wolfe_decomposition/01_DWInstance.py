from gurobipy import *
from gurobipy import GRB

# Step 1: Initialize Restricted Master Problem (RMP)
RMP = Model('DW Master Problme')

# RMP.setParam('OutputFlag', 0)

# -------------- start initialize RMP --------------

# initialize column: Null column

row_num = 3

# Because vars in RMP is added into RMP dynamically,
# thus we create an array to store the variable set
rmp_vars = []
rmp_vars.append(RMP.addVar(lb = 0.0
                           , ub = 1000
                           , obj = 1
                           , vtype = GRB.CONTINUOUS  # GRB.BINARY, GRB.INTEGER
                           , name = 's_1'
                           , column = None
                           ))

rmp_cons = []
var_names = []
col = [-1, 0.001, 0.001]
var_names.append('s_0')

# column to add constraints into RMP
rmp_cons.append(RMP.addConstr(lhs = rmp_vars[0] * col[0]
                              , sense = '<='
                              , rhs = 80
                              , name = 'rmp_con_central'
                              )
                )

rmp_cons.append()