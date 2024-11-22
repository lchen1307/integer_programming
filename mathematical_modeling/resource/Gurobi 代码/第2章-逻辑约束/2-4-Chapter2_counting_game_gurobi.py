# 设置参数取值
a = 0
b = 10
M = 10000
epsilon = 1e-10
x = [-1, 2, 5, 8, 11, 14, 17, 20]

from gurobipy import *

# 创建模型
model = Model('Counting example')

# 定义变量
m = len(x)
u = [None for _ in range(m)]
v = [None for _ in range(m)]
z = [None for _ in range(m)]

for i in range(m):
    u[i] = model.addVar(lb=0, ub=1
                        , vtype=GRB.BINARY
                        , name=f'u{i}'
                        )
    v[i] = model.addVar(lb=0, ub=1
                        , vtype=GRB.BINARY
                        , name=f'v{i}'
                        )
    z[i] = model.addVar(lb=0, ub=1
                        , vtype=GRB.BINARY
                        , name=f'z{i}'
                        )

model.setObjective(0, GRB.MINIMIZE)

# 设置线性化约束
for i in range(m):
    model.addConstr(x[i] - a + M * (1 - u[i]) >= 0, name="u_1_" + str(i))
    model.addConstr(x[i] + epsilon - a <= M * u[i], name="u_2_" + str(i))
    model.addConstr(b - x[i] + M * (1 - v[i]) >= 0, name="v_1_" + str(i))
    model.addConstr(b + epsilon - x[i] <= M * v[i], name="v_2_" + str(i))
    model.addConstr(u[i] + v[i] - 1 <= M * z[i], name="z_1_" + str(i))
    model.addConstr(2 - u[i] - v[i] <= M * (1 - z[i]), name="z_2_" + str(i))

model.optimize()
count = sum(z[i].x for i in range(m))
# count = 0
# for i in range(m):
#     count += z[i].x

print('Total number is: {}'.format(count))