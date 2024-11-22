from coptpy import *

# 创建COPT环境
env = Envr()

# 创建模型
model = env.createModel('Quadratic example')

# 定义乘积式变量
x_1 = model.addVar(lb=0, ub=1, vtype=COPT.BINARY, name='x_1')
x_2 = model.addVar(lb=0, ub=1, vtype=COPT.BINARY, name='x_2')
y = model.addVar(lb=0, ub=1, vtype=COPT.BINARY, name='y')

model.setObjective(y, COPT.MAXIMIZE)

# 设置线性化约束
model.addConstr(y <= x_1)
model.addConstr(y <= x_2)
model.addConstr(y >= x_1 + x_2 - 1)

# Case1: 设置x1=1, x2=1
cons1 = model.addConstr(x_1 == 1)
cons2 = model.addConstr(x_2 == 1)

# 求解模型
model.solve()

# 输出结果
print('Case 1: x1 = 1, x2 = 1 | {} = {}'.format(y.getName(), y.x))

# Case2: 设置x1=0, x2=1
model.remove(cons1)
model.remove(cons2)
cons3 = model.addConstr(x_1 == 0)
cons4 = model.addConstr(x_2 == 1)

# 求解模型
model.solve()

# 输出结果
print('Case 2: x1 = 0, x2 = 1 | {} = {}'.format(y.getName(), y.x))

# Case3: 设置x1=0, x2=0
model.remove(cons3)
model.remove(cons4)
cons5 = model.addConstr(x_1 == 0)
cons6 = model.addConstr(x_2 == 0)

# 求解模型
model.solve()

# 输出结果
print('Case 3: x1 = 0, x2 = 0 | {} = {}'.format(y.getName(), y.x))


from coptpy import *

# 创建环境
env = Envr()

# 创建模型
model = env.createModel()
model.setParam(COPT.Param.Logging, 0)

# 定义0-1变量
x_1 = model.addVar(lb=0, ub=1, vtype=COPT.BINARY, name='x_1')
x_2 = model.addVar(lb=0, ub=1, vtype=COPT.BINARY, name='x_2')
y = model.addVar(lb=0, ub=1, vtype=COPT.BINARY, name='y')

model.setObjective(y, COPT.MAXIMIZE)

# 添加二次约束： y = x_1 * x_2
# expr = QuadExpr()
# expr.addTerm(1, x_1, x_2)
# model.addQConstr(y == expr)
model.addQConstr(y == x_1 * x_2)

# 对x1和x2赋值
model.addConstr(x_1 == 0)
model.addConstr(x_2 == 1)

model.solve()

# 输出结果
print('Case 3: x1 = 0, x2 = 0 | {} = {}'.format(y.getName(), y.x))