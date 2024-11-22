from coptpy import *

# 分断点为(0, 0) , (20, 40) , (30, 55) , (40, 67)
x_n = [0, 20, 30, 40]
y_n = [0, 40, 55, 67]
print('x_n: ', x_n)
print('y_n: ', y_n)
N = len(x_n)

# 创建环境
env = Envr()

# 创建模型
model = env.createModel('Piece-wise Linear Function Example')

# 定义变量
x = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.CONTINUOUS, name='x')
y = model.addVar(lb=0, ub = COPT.INFINITY, vtype=COPT.CONTINUOUS, name='y')

# 设置目标函数
model.setObjective(y, COPT.MAXIMIZE)

# 添加分段线性函数约束
model.addGenConstrPWL(x, y, x_n, y_n, name="Pwl_constr")

model.addConstr(x == 35)

# 求解模型
model.solve()

# 输出结果
print('Optimal Obj: {}'.format(model.ObjVal))
print('y = {}'.format(y.x))