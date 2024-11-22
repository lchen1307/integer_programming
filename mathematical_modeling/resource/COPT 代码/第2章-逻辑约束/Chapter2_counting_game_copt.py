# 设置参数取值
a = 0
b = 10
M = 10000
epsilon = 1e-10
x = [-1, 2, 5, 8, 11, 14, 17, 20]

from coptpy import *

# 创建环境
env = Envr()

# 创建模型
model = env.createModel(name="Counting example")

# 定义变量
m = len(x)
u = [[] for i in range(m)]
v = [[] for i in range(m)]
z = [[] for i in range(m)]

for i in range(m):
    u[i] = model.addVar(lb=0, ub=1
                        , vtype=COPT.BINARY
                        , name="u_" + str(i)
                        )
    v[i] = model.addVar(lb=0, ub=1
                        , vtype=COPT.BINARY
                        , name="v_" + str(i)
                        )
    z[i] = model.addVar(lb=0, ub=1
                        , vtype=COPT.BINARY
                        , name="z_" + str(i)
                        )

model.setObjective(0, COPT.MINIMIZE)

# 设置线性化约束
for i in range(m):
    model.addConstr(x[i] + epsilon - a - M * u[i] <= 0, name="u_1_" + str(i))
    model.addConstr(a - x[i] - M * (1 - u[i]) <= 0, name="u_2_" + str(i))
    model.addConstr(b - x[i] + epsilon - M * v[i] <= 0, name="v_1_" + str(i))
    model.addConstr(x[i] - b - M * (1 - v[i]) <= 0, name="v_2_" + str(i))
    model.addConstr(u[i] + v[i] - 1 <= z[i], name="z_1_" + str(i))
    model.addConstr(2 * z[i] <= u[i] + v[i], name="z_2_" + str(i))

model.solve()
count = 0
for i in range(m):
    count += z[i].x

print('The result is: {}'.format(count))