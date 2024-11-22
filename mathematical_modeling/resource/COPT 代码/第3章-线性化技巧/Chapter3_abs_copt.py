from coptpy import *

# 创建COPT环境
env = Envr()

# 创建模型
model = env.createModel("Absolute Value Linearization example")
M = 1000

# 定义变量
z = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.CONTINUOUS, name='z')
x = model.addVar(lb=-COPT.INFINITY, ub=COPT.INFINITY, vtype=COPT.CONTINUOUS, name='x')
x_p = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.CONTINUOUS, name='x_p')
x_n = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.CONTINUOUS, name='x_n')
y = model.addVar(lb=0, ub=1, vtype=COPT.BINARY, name='y')

# 设置线性化约束
model.setObjective(0, COPT.MAXIMIZE)
model.addQConstr(z == x_p + x_n)
model.addConstr(x == x_p - x_n)
model.addConstr(x_p <= M*y)
model.addConstr(x_n <= M*(1 - y))

# 设置x的取值
model.addConstr(x == -2)

# 求解模型
model.solve()

# 输出结果
print('Optimal Obj: {}'.format(model.objval))
print('z = {}'.format(z.x))
print('x_p = {}'.format(x_p.x))
print('x_n = {}'.format(x_n.x))

