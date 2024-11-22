from coptpy import *

# 分断点为(0, 0) , (20, 40) , (30, 55) , (40, 67)
A_n = [0, 20, 30, 40]
B_n = [0, 40, 55, 67]
print('x_n: ', A_n)
print('y_n: ', B_n)
N = len(A_n)

# 创建环境
env = Envr()

# 创建模型
model = env.createModel('Piece-wise Linear Fucntion Example')

# 定义变量
x = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.CONTINUOUS, name='x')
y = model.addVar(lb=0, ub = COPT.INFINITY, vtype=COPT.CONTINUOUS, name='y')

# 定义权重决策变量
alpha = {}
for i in range(N):
    alpha[i] = model.addVar(lb=0, ub=1, vtype=COPT.CONTINUOUS, name='beta_' + str(i))

# 示性函数z，表示数据取值区间位置的变量
u = {}
for i in range(1, N):
    u[i] = model.addVar(lb=0, ub=1, vtype=COPT.BINARY, name='z_' + str(i))

# 添加约束条件
x_alpha_sum, y_alpha_sum, alpha_sum, u_sum = 0, 0, 0, 0
for i in range(N):
    x_alpha_sum += A_n[i] * alpha[i]
    y_alpha_sum += B_n[i] * alpha[i]
    alpha_sum += alpha[i]

for i in range(1, N):
    u_sum += u[i]

# 约束：x = b_0 * x_0 + b_1 * x_1 + ... + b_n * x_n
model.addConstr(x == x_alpha_sum)

# 约束：y = b_0 * y_0 + b_1 * y_1 + ... + b_n * y_n
model.addConstr(y == y_alpha_sum)

# 约束：beta_0 + beta_1 + ... + beta_n = 1
model.addConstr(1 == alpha_sum)

# 约束：z_0 + z_1 + ... + z_n = 1
model.addConstr(1 == u_sum)

model.addConstr(alpha[0] <= u[1], name='Logic_' + str(0))
model.addConstr(alpha[N - 1] <= u[N - 1], name='Logic_' + str(N - 1))
for i in range(1, N-1):
    model.addConstr(alpha[i] <= u[i] + u[i + 1], name='Logic_' + str(i))

model.addConstr(x == 35)

model.setObjective(y, COPT.MAXIMIZE)

# 求解模型
model.solve()

# 输出结果
print('Optimal Obj: {}'.format(model.ObjVal))
print('y = {}'.format(y.x))
print('u1 = {}'.format(u[1].x))
print('u2 = {}'.format(u[2].x))
print('u3 = {}'.format(u[3].x))
print('alpha0 = {}'.format(alpha[0].x))
print('alpha1 = {}'.format(alpha[1].x))
print('alpha2 = {}'.format(alpha[2].x))
print('alpha3 = {}'.format(alpha[3].x))
