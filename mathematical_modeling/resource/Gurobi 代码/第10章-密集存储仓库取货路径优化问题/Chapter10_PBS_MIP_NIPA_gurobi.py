"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 密集存储仓库取货路径优化问题（NIPA模型）- Gurobi Python接口代码实现
author: 刘兴禄
date:2020-11-25
"""

import numpy as np
import pandas as pd

# 定义密集存储仓库的规模（用数组表示）
row_num = 4  # 定义行数
col_num = 4  # 定义列数

# 生成邻居字典和邻接字典
def init_PBS_warehouse(row_num, col_num):
    """
    该函数用来生成定义密集存储仓库的形状以及后续需要用的参数。

    :param row_num: 行数，默认为3
    :param col_num: 列数，默认为3
    :return: Puzzle_grid, Neighbor_dict, Adj_dict
        Puzzle_grid:        array类型
        Neighbor_dict:      dict类型
        Adj_dict:           dict类型
    """
    PBS_warehouse = np.ones([row_num, col_num])

    Neighbor_dict = {}  # dict类型; key: 数字; value: 邻居集合
    # 遵循上下左右的顺序原则
    for i in range(row_num):
        for j in range(col_num):
            pos_ID = col_num * i + j  # 注意位置ID的计算： col_num * i + j

            if (i == 0 and j == 0):             # 左上角
                Neighbor_dict[pos_ID] = [1, col_num - 1 + 1]
            elif (i == 0 and j == col_num - 1):  # 右上角
                Neighbor_dict[pos_ID] = [pos_ID - 1, pos_ID + col_num]
            elif (i == row_num - 1 and j == 0):  # 左下角
                Neighbor_dict[pos_ID] = [pos_ID - row_num, pos_ID + 1]
            elif (i == row_num - 1 and j == col_num - 1):           # 右下角
                Neighbor_dict[pos_ID] = [pos_ID - col_num, pos_ID - 1]
            elif (i == 0 and j > 0 and j != col_num - 1):           # 第一行
                Neighbor_dict[pos_ID] = [pos_ID - 1, pos_ID + 1, pos_ID + col_num]
            elif (i == row_num - 1 and j > 0 and j != col_num - 1):  # 最后一行
                Neighbor_dict[pos_ID] = [pos_ID - 1, pos_ID + 1, pos_ID - col_num]
            elif (i > 0 and i < row_num - 1 and j == 0):            # 最左一列
                Neighbor_dict[pos_ID] = [pos_ID + 1, pos_ID - col_num, pos_ID + col_num]
            elif (i > 0 and i < row_num - 1 and j == col_num - 1):  # 最右一列
                Neighbor_dict[pos_ID] = [pos_ID - 1, pos_ID - col_num, pos_ID + col_num]
            elif (i > 0 and i < row_num - 1 and j > 0 and j < col_num - 1):     # 其它位置
                Neighbor_dict[pos_ID] = [pos_ID - 1, pos_ID + 1, pos_ID - col_num, pos_ID + col_num]

    # 生成邻接字典，key: (pos_A, pos_B); value: 0或者1
    Adj_dict = {}
    for key_1 in Neighbor_dict.keys():
        for key_2 in Neighbor_dict.keys():
            if (key_1 == key_2 or (key_2 not in Neighbor_dict[key_1])):
                Adj_dict[key_1, key_2] = 0
            else:
                Adj_dict[key_1, key_2] = 1

    return PBS_warehouse, Neighbor_dict, Adj_dict

PBS_warehouse, Neighbor_dict, Adj_dict = init_PBS_warehouse(row_num=row_num, col_num=col_num)

print("\n密集存储仓库形状\n", PBS_warehouse)
print("\n邻居位置字典\n", Neighbor_dict)
print("\n邻接字典\n", Adj_dict)


'''
定义IO口的位置，以及最大允许的步数
  4 * 4 的仓库
'''
IO_points_ID = [0, 3]
IO_point_set = [0, 3]
IO_points = [[0, 0], [0, 3]]


'''
读取测试算例
'''
instance_set = pd.read_excel('422_improved_RL.xlsx')            # 读取测试算例
instance_set['步数'] = instance_set['步数'].fillna(40)          # 将所用最大步数为空的算例对应的数字填充为40

'''
提取算例信息
'''
instance_ID = 0
# 提取目标货物在仓库中的坐标，例如[[1, 2], [2, 1]]
desired_items_pos = [[instance_set.iloc[instance_ID, 0], instance_set.iloc[instance_ID, 1]],
                     [instance_set.iloc[instance_ID, 2], instance_set.iloc[instance_ID, 3]]]

# 提取空格的位置在仓库中的坐标，例如[[0, 0], [0, 1]]
empty_cells = [[instance_set.iloc[instance_ID, 4], instance_set.iloc[instance_ID, 5]],
               [instance_set.iloc[instance_ID, 6], instance_set.iloc[instance_ID, 7]]]


# 将目标货物和空格的坐标转化为位置编号，并且初始化仓库的状态
# 0: 空格；1：被非目标物体占用；2：被目标物体占用
empty_cell_pos = []
for i in range(len(empty_cells)):
    row = empty_cells[i][0]
    column = empty_cells[i][1]
    PBS_warehouse[row][column] = 0
    empty_cell_pos.append(row * col_num + column)
    # set the desired item poition
for i in range(len(desired_items_pos)):
    row = desired_items_pos[i][0]
    column = desired_items_pos[i][1]
    PBS_warehouse[row][column] = 2

print(PBS_warehouse)
print(empty_cell_pos)

# 生成item_set, position_set, desired_item_set, init_occupy_state
# 其中，init_occupy_state是字典类型，key为(item_ID, pos_ID)， value为0或1
item_ID = 0
item_set = []
pos_set = []
desired_item_set = []
desired_item_dict = {}
init_occupy_state = {}
for i in range(len(PBS_warehouse)):
    for j in range(len(PBS_warehouse[0])):
        pos_ID = i * col_num + j
        pos_set.append(pos_ID)
        if (PBS_warehouse[i][j] > 0):
            item_set.append(item_ID)
            init_occupy_state[item_ID, pos_ID] = 1
            for k in range(len(desired_items_pos)):
                desired_item = desired_items_pos[k]
                if (desired_item[0] == i and desired_item[1] == j):
                    desired_item_dict[k] = item_ID
            item_ID += 1

for i in range(len(desired_item_dict)):
    desired_item_set.append(desired_item_dict[i])

print("\n货物编号集合\n", item_set)
print("\n位置编号集合\n", pos_set)
print("\n目标货物编号集合\n", desired_item_set)
print("\n仓库的初始占用状态\n", init_occupy_state)



"""
建立模型并求解
"""
import time
from gurobipy import *
# 定义建立NIPA模型，求解NIPA模型，然后输出运行结果的函数
def build_and_solve_PBS_NIPA_model(row_num, col_num, Adj_dict, Max_Step, item_set,
                                   pos_set, init_occupy_state, desired_item_set,
                                   IO_point_set, empty_cell_pos):
    """
    定义建立NIPA模型，求解NIPA模型，然后输出运行结果的函数。
    ----------
    :param row_num:             仓库的行数
    :param col_num:             仓库的列数
    :param Adj_dict:            位置邻接字典
    :param Max_Step:            最大允许的步数
    :param item_set:            货物的编号集合
    :param pos_set:             位置的编号集合
    :param init_occupy_state:   初始占用信息字典
    :param desired_item_set:    目标货物位置编号集合
    :param IO_point_set:        IO口的位置编号集合
    :param empty_cell_pos:      空格的初始位置编号集合

    :return: Opt_Obj, CPU_time
        Opt_Obj:        double, 最优目标函数
        CPU_time:       double, 计算时间
    """
    start_time = time.time()        # 记录运行时间

    # 定义NIPA模型
    model = Model('NIPA Model')
    '''
    定义决策变量
    -------------------------
      x[k, i, p]: 0-1变量，在第k步移动后，货物i的是否处在位置p 
      y[k, i, p, q]: 0-1变量，第k步，是否把货物i从位置p移动到位置q 
    '''
    x = {}
    y = {}
    for k in range(Max_Step):
        for i in item_set:
            for p in pos_set:
                x[k, i, p] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY,
                                          name='x_' + str(k) + '_' + str(i) + '_' + str(p))
                for q in pos_set:
                    if (p != q):
                        y[k, i, p, q] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY
                                                     , name='y_' + str(k) + '_' + str(i) + '_' + str(p) + '_' + str(q))

    # 定义目标函数
    obj = LinExpr()
    for key in y.keys():
        obj.addTerms(1, y[key])
    model.setObjective(obj, GRB.MINIMIZE)

    '''
    添加约束条件 
    '''
    # 约束1: 初始化第0步的占用状态
    for i in item_set:
        for p in pos_set:
            temp_key = (i, p)
            if(temp_key in init_occupy_state.keys()):
                model.addConstr(x[0, i, p] == 1, name='init_' + str(0) + '_' + str(i) + '_' + str(p))
            else:
                model.addConstr(x[0, i, p] == 0, name='init_' + str(0) + '_' + str(i) + '_' + str(p))

    # 约束2: 第0步没有任何移动动作
    lhs = LinExpr()
    for i in item_set:
        for p in pos_set:
            for q in pos_set:
                if (p != q):
                    lhs.addTerms(1, y[0, i, p, q])
    model.addConstr(lhs == 0, name='cons_2_no_move_at_step_0')

    # 约束3: 每一步，每一个货物，必然占据且只占据一个位置
    for k in range(Max_Step):
        for i in item_set:
            lhs = LinExpr()
            for p in pos_set:
                lhs.addTerms(1, x[k, i, p])
            model.addConstr(lhs == 1, name='cons_3_' + str(k) + "_" + str(i))

    # 约束4: 每一步，每一个位置，至多被一个货物占据
    for k in range(Max_Step):
        for p in pos_set:
            lhs = LinExpr()
            for i in item_set:
                lhs.addTerms(1, x[k, i, p])
            model.addConstr(lhs <= 1, name='cons_4_occupy_limit_' + str(k) + '_' + str(p))

    # 约束5: 移动合法性，一个位置只能移动到其邻接位置
    for k in range(Max_Step):
        for i in item_set:
            for p in pos_set:
                for q in pos_set:
                    if (p != q):
                        model.addConstr(y[k, i, p, q] <= Adj_dict[p, q], name='cons_5_move_condition_' + str(k) + '_' + str(i) + '_' + str(p) + '_' + str(q))

    # 约束6: 只有目标位置为空，移动才被允许
    for k in range(1, Max_Step):
        for i in item_set:
            for q in pos_set:
                rhs = LinExpr()
                for item2 in item_set:
                    rhs.addTerms(1, x[k - 1, item2, q])
                for p in pos_set:
                    if (p != q):
                        model.addConstr(y[k, i, p, q] <= 1 - rhs,
                                        name='cons_6_move_condition_' + str(k) + '_' + str(i) + '_' + str(p) + '_' + str(q))

    # 约束7: 相邻两步的状态转化
    for k in range(1, Max_Step):
        for i in item_set:
            for p in pos_set:
                lhs = LinExpr()
                lhs.addTerms(1, x[k - 1, i, p])
                for q in pos_set:
                    if (p != q):
                        lhs.addTerms(-1, y[k, i, p, q])
                        lhs.addTerms(1, y[k, i, q, p])
                model.addConstr(lhs == x[k, i, p], name='cons_7_move_balance_' + str(k) + '_' + str(i) + '_' + str(p))

    # 约束8: 每一步只允许最多一次移动
    for k in range(1, Max_Step):
        lhs = LinExpr()
        for i in item_set:
            for p in pos_set:
                for q in pos_set:
                    if(p != q):
                        lhs.addTerms(1, y[k, i, p, q])
        model.addConstr(lhs <= 1, name='cons_8_move_upper_limit_' + str(k))

    # 约束9: 最终要将目标货物移动带各自的IO口
    model.addConstr(x[Max_Step - 1, desired_item_set[0], IO_point_set[0]] == 1, name='final_state_' + str(1))
    model.addConstr(x[Max_Step - 1, desired_item_set[1], IO_point_set[1]] == 1, name='final_state_' + str(2))

    # 设置求解日志输出的路径
    log_file_name = 'Log_4_4_grid' + '_Max_Step_'+ str(Max_Step) + '.log'
    model.setParam(GRB.Param.LogFile, log_file_name)        # 设置输出路径
    model.setParam(GRB.Param.MIPGap, 0)                     # 设置MIPGap容差为0
    # model.setParam(GRB.Param.TimeLimit, 7200)             # 设置求解时间限制
    model.write('n-n-slides.lp')                           # 导出IP模型
    model.optimize()                                      # 求解模型
    CPU_time = model.Runtime                                # 提取求解时间

    end_time = time.time()                                  # 记录整个程序的运行时间

    if (model.Status == 2):
        Opt_Obj = model.ObjVal
    else:
        Opt_Obj = 100000000

    print('Running time :', CPU_time)

    '''
    将求解结果输出    
    '''
    solution_file = 'Log_4_4_grid' + '_Max_Step_' + str(Max_Step) + '.txt'
    with open(solution_file, 'a') as f:  # 这个是append模型，也就是会继续在上一次的基础上添加到文件最后
    # with open(solution_file, 'x') as f:   # 模式'x'，每次都重新从头写入
        if (model.Status == 2):  # status code == 2, 表示求解到了最优解
            print('模型求解状态 :', model.Status)
            print('算例被求解到了最优！')
            print('目标函数: ', model.ObjVal)
            print('求解时间: ', CPU_time, ' s')
            f.write('\n 目标函数 : ' + str(model.ObjVal) + '\n')
            f.write('求解时间 : ' + str(CPU_time) + ' s' + '\n')
            f.write('\n----- 最优解 --- \n')
            for key in y.keys():
                if (y[key].x > 0):
                    sol_str = 'y ' + str(key) + ' = ' + str(y[key].x) + '\n'
                    print('y ', key, ' = ', y[key].x)
                    f.write(sol_str)
            f.write('\n----- 最优解 (逐步展示的版本)--- \n')
            Optimal_step_num = (int)(model.ObjVal)
            for k in range(Optimal_step_num + 1):   #Max_Step
                PBS_warehouse_k = np.zeros([row_num, col_num])
                for p in pos_set:
                    temp = 0
                    for i in item_set:
                        if(i in desired_item_set):
                            temp += 2 * x[k, i, p].x
                        else:
                            temp += x[k, i, p].x
                    col_ID = p % col_num
                    row_ID = (int)(p / col_num)
                    PBS_warehouse_k[row_ID][col_ID] = temp

                print('\n ------ 第%2d 步 --------\n' % k)
                f.write('\n ------ 第%2d 步 --------\n' % k)
                f.write(str(PBS_warehouse_k))
                print(PBS_warehouse_k)

            f.write('\n\n 输出解完毕！ \n\n')
            f.close()
        else:
            print('算例不可行！')
            Status_Code = model.Status
            f.write('\n\n  模型求解状态： ')
            f.write(str(Status_Code))
            f.write('\n')
            f.write('\n\n  模型不可行 !')
            f.close()

    return CPU_time, Opt_Obj


# 求解模型
Max_Step = 14
CPU_time, Opt_Obj = build_and_solve_PBS_NIPA_model(
    row_num, col_num, Adj_dict, Max_Step, item_set,
    pos_set, init_occupy_state, desired_item_set,
    IO_point_set, empty_cell_pos
)


