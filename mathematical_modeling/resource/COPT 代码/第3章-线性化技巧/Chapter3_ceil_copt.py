from coptpy import *

# 创建环境
env = Envr()

# 创建模型
model = env.createModel('ceil example')

#定义变量
x = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.CONTINUOUS, name="x")
y = model.addVar(lb=0, ub=10, vtype=COPT.INTEGER, name="y")

model.setObjective(0, COPT.MINIMIZE)

#添加线性化约束
model.addConstr(y >= x/1800, name="ceil_1")
model.addConstr(y-1 <= x/1800, name="ceil_2")

#设置x的取值为2000
model.addConstr(x == 2000, name="ceil_3")
model.solve()

print('y is: {}'.format(y.x))