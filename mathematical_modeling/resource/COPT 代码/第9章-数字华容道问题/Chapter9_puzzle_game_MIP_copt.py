"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 数字华容道问题- COPT Python接口代码实现
author: 杉数科技
date:2022-10-11
"""

import numpy as np

# 定义数字华容道游戏盘面（用数组表示）
row_num = 3  # 定义行数
col_num = 3  # 定义列数

# 生成邻居字典和邻接字典
def init_Puzzle_grid(row_num=3, col_num=3):
    """
    该函数用来生成数字华容道游戏盘面以及后续需要用的参数。

    :param row_num: 行数，默认为3
    :param col_num: 列数，默认为3
    :return: Puzzle_grid, Neighbor_dict, Adj_dict
        Puzzle_grid:        array类型
        Neighbor_dict:      dict类型
        Adj_dict:           dict类型
        item_set:           list,数字滑块的集合
        pos_set:            list,位置的集合
    """
    Puzzle_grid = np.zeros([row_num, col_num])
    item_set = []
    pos_set = []

    Neighbor_dict = {}  # dict类型; key: 数字; value: 邻居集合
    # 遵循上下左右的顺序原则
    for i in range(row_num):
        for j in range(col_num):
            pos_ID = col_num * i + j  # 注意位置ID的计算： col_num * i + j

            pos_set.append(pos_ID)

            if(pos_ID + 1 < row_num * col_num):
                # 最后一个位置是空格
                Puzzle_grid[i][j] = pos_ID + 1
                item_set.append(pos_ID)

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

    return Puzzle_grid, Neighbor_dict, Adj_dict, item_set, pos_set

Puzzle_grid, Neighbor_dict, Adj_dict, item_set, pos_set = init_Puzzle_grid(row_num=3, col_num=3)

print("\n数字华容道初始游戏盘面\n", Puzzle_grid)
print("\n邻居位置字典\n", Neighbor_dict)
print("\n邻接字典\n", Adj_dict)
print("\n数字滑块集合\n", item_set)
print("\n位置集合\n", pos_set)



# 准备测试算例，注意，由于下标从0开始，所以对应的数字减去1
instance = {
    0: 0,
    1: 1,
    2: 2,
    3: 6,
    4: 5,
    5: 3,
    6: 7,
    7: 4
}


"""
建立模型并求解
"""
import time
from coptpy import *
# 定义建立模型并求解模型，输出运行结果的函数
def build_and_solve_Puzzle_grid(instance, Max_Step, item_set, pos_set, Adj_dict):
    """
    建立模型并求解的函数。
    ----------
    :param instance:    算例数据
    :param Max_Step:    移动步数上限
    :param item_set:    数字滑块集合
    :param pos_set:     位置集合
    :param Adj_dict:    位置邻接字典

    :return: Opt_Obj, CPU_time
        Opt_Obj:        double, 最优目标函数
        CPU_time:       double, 计算时间
    """
    start_time = time.time()        # 记录运行时间

    # 定义MIP模型
    env = Envr()
    model = env.createModel('Puzzle grid game')
    '''
    定义决策变量
    -------------------------
      x[k, i, p]: 0-1变量，在第k步移动后，数字i的是否处在位置p 
      y[k, i, p, q]: 0-1变量，第k步，是否把数字i从位置p移动到位置q 
    '''
    x = {}
    y = {}
    for k in range(Max_Step):
        for i in item_set:
            for p in pos_set:
                x[k, i, p] = model.addVar(lb=0, ub=1, vtype=COPT.BINARY,
                                          name='x_' + str(k) + '_' + str(i) + '_' + str(p))
                for q in pos_set:
                    if (p != q):
                        y[k, i, p, q] = model.addVar(lb=0, ub=1, vtype=COPT.BINARY
                                                     , name='y_' + str(k) + '_' + str(i) + '_' + str(p) + '_' + str(q))

    # 定义目标函数
    obj = LinExpr()
    for key in y.keys():
        obj.addTerms(y[key], 1)
    model.setObjective(obj, COPT.MINIMIZE)

    '''
    添加约束条件 
    '''
    # 约束1: 初始化第0步的占用状态
    for key in instance.keys():
        p = key
        i = instance[key]
        model.addConstr(x[0, i, p] == 1, name='cons_1_init_' + str(0) + '_' + str(i) + '_' + str(p))

    # 约束2: 第0步没有任何移动动作
    lhs = LinExpr()
    for i in item_set:
        for p in pos_set:
            for q in pos_set:
                if (p != q):
                    lhs.addTerms(y[0, i, p, q], 1)
    model.addConstr(lhs == 0, name='cons_2_no_move_at_step_0')

    # 约束3: 每一步，每一个数字，必然占据且只占据一个位置
    for k in range(Max_Step):
        for i in item_set:
            lhs = LinExpr()
            for p in pos_set:
                lhs.addTerms(x[k, i, p], 1)
            model.addConstr(lhs == 1, name='cons_3_' + str(k) + "_" + str(i))

    # 约束4: 每一步，每一个位置，至多被一个数字占据
    for k in range(Max_Step):
        for p in pos_set:
            lhs = LinExpr()
            for i in item_set:
                lhs.addTerms(x[k, i, p], 1)
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
                    rhs.addTerms(x[k - 1, item2, q], 1)
                for p in pos_set:
                    if (p != q):
                        model.addConstr(y[k, i, p, q] <= 1 - rhs,
                                        name='cons_6_move_condition_' + str(k) + '_' + str(i) + '_' + str(p) + '_' + str(q))

    # 约束7: 相邻两步的状态转化
    for k in range(1, Max_Step):
        for i in item_set:
            for p in pos_set:
                lhs = LinExpr()
                lhs.addTerms(x[k - 1, i, p], 1)
                for q in pos_set:
                    if (p != q):
                        lhs.addTerms(y[k, i, p, q], -1)
                        lhs.addTerms(y[k, i, q, p], 1)
                model.addConstr(lhs == x[k, i, p], name='cons_7_move_balance_' + str(k) + '_' + str(i) + '_' + str(p))

    # 约束8: 每一步只允许最多一次移动
    for k in range(1, Max_Step):
        lhs = LinExpr()
        for i in item_set:
            for p in pos_set:
                for q in pos_set:
                    if(p != q):
                        lhs.addTerms(y[k, i, p, q], 1)
        model.addConstr(lhs <= 1, name='cons_8_move_upper_limit_' + str(k))

    # 约束9: 最终要完成还原
    item_num = col_num * row_num - 1
    for i in item_set:
        if (i != item_num):
            model.addConstr(x[Max_Step - 1, i, i] == 1, name='cons_9_final_state_' + str(i))

    # 设置求解日志输出的路径
    log_file_name = './Results_tested/Log_3_3_slides' + '_Max_Step_'+ str(Max_Step) + '.log'
    model.setLogFile(log_file_name)        # 设置输出路径
    # model.setParam(COPT.Param.TimeLimit, 7200)             # 设置求解时间限制
    model.write('n-n-slides.lp')                           # 导出LP模型
    model.solve()                                      # 求解模型

    end_time = time.time()                                  # 记录整个程序的运行时间
    CPU_time = end_time-start_time                                # 提取求解时间

    if (model.Status == 2):
        Opt_Obj = model.ObjVal
    else:
        Opt_Obj = 100000000

    print('Running time :', CPU_time)

    '''
    将求解结果输出    
    '''
    # solution_file = './Results_tested/Log_n_n_slides' + '_Max_Step_' + str(Max_Step) + '.txt'
    solution_file = 'Log_n_n_slides' + '_Max_Step_' + str(Max_Step) + '.txt'
    # with open(solution_file,'a') as f:  # 这个是append模型，也就是会继续在上一次的基础上添加到文件最后
    with open(solution_file, 'x') as f:   # 模式'x'，每次都重新从头写入
        if (model.Status == 1):  # status code == 1, 表示求解到了最优解
            print('Model Status :', model.Status)
            print('instance: ', ' is Solved to OPTIMAL')
            f.write('\n Objective : ' + str(model.ObjVal) + '\n')
            f.write('Running Time : ' + str(CPU_time) + ' s' + '\n')
            f.write('\n----- Optimal Solution --- \n')
            for key in y.keys():
                if (y[key].x > 0):
                    sol_str = 'y ' + str(key) + ' = ' + str(y[key].x) + '\n'
                    print('y ', key, ' = ', y[key].x)
                    f.write(sol_str)
            f.write('\n----- Optimal Solution (Step Version)--- \n')
            Optimal_step_num = (int)(model.ObjVal)
            for k in range(Optimal_step_num + 1):  # Max_Step
                Puzzle_grid_k = np.zeros([row_num, col_num])
                for p in pos_set:
                    temp = 0
                    for i in item_set:
                        if (x[k, i, p].x > 0):
                            temp += (int)(i + 1)

                    col_ID = p % col_num
                    row_ID = (int)(p / col_num)
                    Puzzle_grid_k[row_ID][col_ID] = temp

                print('\n ------ 第%2d 步 --------\n' % k)
                f.write('\n ------ 第%2d 步 --------\n' % k)
                f.write(str(Puzzle_grid_k))
                print(Puzzle_grid_k)

            f.write('\n\n Solution End \n\n')
            f.close()
        else:
            print('instance: ', ' is infeasible')
            Status_Code = model.Status
            f.write(str(Status_Code))
            f.write('\n\n  Solution Status \n')
            f.write('\n\n  Model is infeasible !')
            f.close()

    return CPU_time, Opt_Obj

# 求解模型
Max_Step = 11
CPU_time, Opt_Obj = build_and_solve_Puzzle_grid(instance=instance,
                Max_Step=Max_Step,
                item_set=item_set,
                pos_set=pos_set,
                Adj_dict=Adj_dict)

