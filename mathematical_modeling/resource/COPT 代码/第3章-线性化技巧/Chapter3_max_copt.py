from coptpy import *

# 创建COPT环境
env = Envr()

# 创建模型
model = env.createModel()

# 添加决策变量
x_1 = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.CONTINUOUS, name='x_1')
x_2 = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.CONTINUOUS, name='x_2')
y = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.CONTINUOUS, name='y')

# 添加线性化约束
model.addConstr(y >= x_1)
model.addConstr(y >= x_2)
model.addConstr(y >= 2)

# 设置x, y的取值
model.addConstr(x_1 == 3)
model.addConstr(x_2 == 5)

# 设置目标
model.setObjective(y, sense=COPT.MINIMIZE)

# 求解模型
model.solve()

# 输出结果
print('Optimal Obj: {}'.format(model.ObjVal))

