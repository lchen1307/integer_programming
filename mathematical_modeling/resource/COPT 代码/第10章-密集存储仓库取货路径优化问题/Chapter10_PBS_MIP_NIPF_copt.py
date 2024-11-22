"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 密集存储仓库取货路径优化问题（NIPF模型）- COPT Python接口代码实现
author: 杉数科技
date:2022-10-11
institute:杉数科技
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
建立NIPF模型并求解
"""
import time
from coptpy import *
# 定义建立NIPA模型，求解NIPF模型，然后输出运行结果的函数
def build_and_solve_PBS_NIPF_model(row_num, col_num, Adj_dict, Max_Step,
                                   pos_set, init_occupy_state, desired_item_set,
                                   IO_point_set, empty_cell_pos):
    """
    定义建立NIPF模型，求解NIPF模型，然后输出运行结果的函数。
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

    注意：
    -----------
    通过探索发现，约束 1,2,3,11,13,5,15,9,10 组成的模型依然是可行的，但是缺点是求解效果不太好。

    另外，在加入约束15的同时，也加入下面的约束
     model.addGenConstrIndicator(w[k, p, q, r], False, y[k - 1, p, d] + z[k, p, q] <= 1)
     这个约束的意思是上面约束15的else的部分。本来是不加也可以。但是如果将其加入，
     并且删除约束4,12,6,7,8,14，模型依然可行。但求解效率却会降低，例如R622的算例2需要278s，但是用之前的完整模型只需要25s。
    """
    start_time = time.time()        # 记录运行时间

    # 定义NIPF模型
    model = Envr().createModel('PBS-NIPF Model')
    '''
    定义决策变量
    -------------------------
      x[k, p]: 第k步时，位置p是否被某一个货物占据 
      y[k, p, r]: 第k步时，如果目标货物r占据了位置p，则y[k, p, r]=1，否则y[k, p, r]=0
      z[k, p, q]: 第k步时，若将位于p处的货物移动到位置q，则z[k, p, q]=1，否则z[k, p, q]=0
      w[k, p, q, r]: 第k步时，若将位于p处的目标货物r移动到位置q，则w[k, p, q, r]=1，否则w[k, p, q, r]=0
    '''
    x = {}
    y = {}
    z = {}
    w = {}
    for k in range(Max_Step):
        for p in pos_set:
            x[k, p] = model.addVar(lb=0, ub=1, vtype=COPT.BINARY, name='x_' + str(k) + '_' + str(p))
            for r in range(len(desired_item_set)):
                y[k, p, r] = model.addVar(lb=0, ub=1, vtype=COPT.BINARY,
                                          name='y_' + str(k) + '_' + str(p) + '_' + str(r))
            for q in pos_set:
                if (p != q):
                    z[k, p, q] = model.addVar(lb=0, ub=1, vtype=COPT.BINARY
                                              , name='z_' + str(k) + '_' + str(p) + '_' + str(q)
                                              )
                    for r in range(len(desired_item_set)):
                        w[k, p, q, r] = model.addVar(lb=0, ub=1, vtype=COPT.BINARY,
                                                     name='w_' + str(k) + '_' + str(p) + '_' + str(q) + '_' + str(r))

    # 创建目标函数
    obj = LinExpr(0)
    for key in z.keys():
        obj.addTerms(z[key], 1)
    model.setObjective(obj, COPT.MINIMIZE)

    '''
    添加约束条件
    '''
    ''' 约束1：初始化仓库的占用情况 '''
    for p in pos_set:
        is_occupied = False
        for key in init_occupy_state.keys():
            if (init_occupy_state[key] == 1 and key[1] == p):
                is_occupied = True
                break
        if (is_occupied == True):
            model.addConstr(x[0, p] == 1, name='init_x_' + str(0) + '_' + str(p))
        else:
            model.addConstr(x[0, p] == 0, name='init_x_' + str(0) + '_' + str(p))

    ''' 约束2: 设置 y[k, p, r]的初始值 '''
    for r in range(len(desired_item_set)):
        desired_item_pos_ID = desired_items_pos[r][0] * col_num + desired_items_pos[r][1]
        for p in pos_set:
            if (p == desired_item_pos_ID):
                model.addConstr(y[0, p, r] == 1,
                                name='init_y_' + str(0) + '_' + str(p) + '_' + str(r))
            else:
                model.addConstr(y[0, p, r] == 0,
                                name='init_y_' + str(0) + '_' + str(p) + '_' + str(r))

    ''' 约束3 : 设置z[0, p, q]的初始值 '''
    for key in z.keys():
        if (key[0] == 0):
            model.addConstr(z[0, key[1], key[2]] == 0, name='init_z_' + str(0) + '_' + str(key[1]) + '_' + str(key[2]))


    ''' 约束4: 每一步货物占据的总位置数量是恒定的 '''
    for k in range(Max_Step):
        lhs = LinExpr()
        for p in pos_set:
            lhs.addTerms(x[k, p], 1)
        model.addConstr(lhs == len(pos_set) - len(empty_cell_pos), 'occupied number')

    ''' 约束5: 每个位置的占用情况的转换 '''
    for k in range(1, Max_Step):  # 注意从1开始
        for p in pos_set:
            lhs = LinExpr()
            lhs.addTerms(x[k - 1, p], 1)
            for q in pos_set:
                if (p != q):
                    lhs.addTerms(z[k, p, q], -1)
                    lhs.addTerms(z[k, q, p], 1)
            model.addConstr(lhs == x[k, p], 'state transit')

    ''' 约束6:  y[k, p, r] <= x[k, p] '''
    for k in range(Max_Step):
        for p in pos_set:
            for d in range(len(desired_item_set)):
                model.addConstr(y[k, p, r] <= x[k, p], 'desired item location logic')

    ''' 约束7: 每个目标货物每一步都占据一个位置 '''
    for k in range(Max_Step):
        for d in range(len(desired_item_set)):
            lhs = LinExpr()
            for p in pos_set:
                lhs.addTerms(y[k, p, r], 1)
            model.addConstr(lhs == 1, 'desired item occupancy')

    ''' 约束8: 每个位置，至多只能被一个目标货物占据 '''
    for k in range(Max_Step):
        for p in pos_set:
            lhs = LinExpr()
            for r in range(len(desired_item_set)):
                lhs.addTerms(y[k, p, r], 1)
            model.addConstr(lhs <= 1, 'desired item locates at most one position')

    ''' 约束 9:  目标货物的占用位置变化 '''
    for k in range(1, Max_Step):
        for p in pos_set:
            for r in range(len(desired_items_pos)):
                lhs = LinExpr()
                lhs.addTerms(y[k - 1, p, r], 1)
                for q in pos_set:
                    if (p != q):
                        lhs.addTerms(w[k, p, q, r], -1)
                        lhs.addTerms(w[k, q, p, r], 1)
                model.addConstr(lhs == y[k, p, r], 'desired item location transit')

    ''' 约束10:  最终货物需要被成功移动到相应的IO口 '''
    for r in range(len(desired_item_set)):
        model.addConstr(y[Max_Step - 1, IO_point_set[r], r] == 1, 'desired item location end')

    ''' 约束11: 货物只能移动到期相邻位置'''
    for k in range(Max_Step):
        for p in pos_set:
            for q in pos_set:
                if (p != q):
                    model.addConstr(z[k, p, q] <= Adj_dict[p, q], 'move condition 1 : Adj_dict')

    ''' 约束12:  只有当目标位置是空位的时候，移动才被允许'''
    for k in range(1, Max_Step):
        for p in pos_set:
            for q in pos_set:
                if (p != q):
                    model.addConstr(z[k, p, q] <= 1 - x[k - 1, q], 'move condition 2 : escort available')

    ''' 约束13:  每一步至多只能移动一次 '''
    for k in range(0, Max_Step):
        lhs = LinExpr()
        for p in pos_set:
            for q in pos_set:
                if (p != q):
                    lhs.addTerms(z[k, p, q], 1)
        model.addConstr(lhs <= 1, 'single move cons')

    ''' 约束14: 目标货物的移动条件'''
    ''' sum w[k, p, q, r] <= z[p,q,r] '''
    for k in range(Max_Step):
        for p in pos_set:
            for q in pos_set:
                if(p != q):
                    lhs = LinExpr()
                    for r in range(len(desired_items_pos)):
                        lhs.addTerms(w[k, p, q, r], 1)
                    model.addConstr(lhs <= z[k, p, q], 'desired_item_move_logic')

    ''' 约束15: 目标物体移动的条件 '''
    ''' 如果 y[p, r, k-1] == 1 且 z[p,q,k] == 1, 则 w[p,q,r,k] == 1 '''
    ''' 约束15: 目标物体移动的条件 '''
    ''' 如果 y[p, r, k-1] == 1 且 z[p,q,k] == 1, 则 w[p,q,r,k] == 1 '''
    for k in range(1, Max_Step):
        for p in pos_set:
            for q in pos_set:
                if (p != q):
                    for r in range(len(desired_items_pos)):
                        # 第一种实现方法：直接使用函数addGenConstrAnd
                        # model.addGenConstrAnd(w[k, p, q, r], [y[k - 1, p, r], z[k, p, q]],
                        #                       'desired item location transit 2')

                        # 第二种实现方法：等价线性化
                        model.addConstr(w[k, p, q, r] >= y[k - 1, p, r] + z[k, p, q] - 1)
                        model.addConstr(w[k, p, q, r] <= y[k - 1, p, r])
                        model.addConstr(w[k, p, q, r] <= z[k, p, q])

                        # model.addGenConstrIndicator(w[k, p, q, r], False, y[k - 1, p, r] + z[k, p, q] <= 1)

                        """
                        通过探索发现，约束 1,2,3,11,13,5,15,9,10 组成的模型依然是可行的，但是缺点是求解效果不太好。
                        
                        另外，在加入约束15的同时，也加入下面的约束
                        
                        model.addGenConstrIndicator(w[k, p, q, r], False, y[k - 1, p, d] + z[k, p, q] <= 1)
                        这个约束的意思是上面约束15的else的部分。本来是不加也可以。但是如果将其加入，并且删除约束4,12,6,7,8,14，模型依然可行。但求解效率却会降低，例如R622的算例2需要278s，但是用之前的完整模型只需要25s。
                        """
    print(' ------------------ 求解 ------------------ ')

    log_file_name = 'Log_4_4_grid' + '_Max_Step_'+ str(Max_Step) + 'NIPF.log'
    model.setLogFile(log_file_name)
    model.setParam(COPT.Param.RelGap, 0)
    model.setParam(COPT.Param.TimeLimit, 7200 * 2)
    model.solve()

    end_time = time.time()
    # CPU_time = end_time - start_time
    CPU_time = model.SolvingTime
    print('求解时间 :', CPU_time)

    Opt_Obj = 100000000
    if(model.Status == 2):
        Opt_Obj = model.ObjVal

    # 打印一下desired item的位置
    print('打印一下desired item的位置')
    if (model.PoolSols > 0):
        for key in y.keys():
            if (y[key].x > 0):
                print('{} = {}'.format(y[key].name, y[key].x))

    '''
     ------------- 导出求解结果 -------------    
    '''
    solution_file = 'Sol_4_4_grid' + '_Max_Step_' + str(Max_Step) + 'NIPF.txt'
    Opt_sol = []
    with open(solution_file, 'a') as f:
    # with open(solution_file, 'w') as f:
        if (model.Status == COPT.OPTIMAL or model.Status == COPT.TIMEOUT):  # 状态码 == 2, 意味着模型求解到了OPTIMAL
            print('\n\n\n------------------------')
            print('模型求解状态 :', model.Status)
            if (model.Status == COPT.OPTIMAL):
                f.write('\n 模型求解状态 : OPTIMAL \n')
            if (model.Status == COPT.TIMEOUT):
                f.write('\n 模型求解状态 : TIME_LIMIT \n')

            if (model.PoolSols > 0):
                print('目标函数:', model.ObjVal)
                print('COPT获得的解的个数:', model.PoolSols)
                print('求解时间: {} 秒'.format(CPU_time))
                f.write('\n COPT获得的解的个数:' + str(model.PoolSols) + '\n\n')
                f.write('\n 目标函数 : ' + str(model.ObjVal) + '\n\n')
                f.write('模型求解时间 : ' + str(CPU_time) + ' s' + '\n\n')
                f.write('\n----- 移动决策变量的取值 --- \n')
                print('\n----- 移动决策变量的取值 --- \n')
                
                for key in z.keys():
                    if (z[key].x > 0.1):
                        sol_str = 'z ' + str(key) + ' = ' + str(round(z[key].x, 1)) + '\n'
                        pos_1 = key[1]
                        pos_2 = key[2]
                        for i in range(len(empty_cell_pos)):
                            if (pos_2 == empty_cell_pos[i] and i == 0):
                                # 表示移动空格1
                                if (pos_2 - pos_1 == col_num):  # 列的编号
                                    Opt_sol.append(0)  # 向上移
                                elif (pos_2 - pos_1 == -col_num):
                                    Opt_sol.append(1)  # 向下移
                                elif (pos_2 - pos_1 == 1):
                                    Opt_sol.append(2)  # 向左移
                                elif (pos_2 - pos_1 == -1):
                                    Opt_sol.append(3)  # 向右移

                                # 更新空格的位置
                                empty_cell_pos[i] = pos_1
                                
                            if (pos_2 == empty_cell_pos[i] and i == 1):
                                # 表示移动空格2
                                if (pos_2 - pos_1 == col_num):
                                    Opt_sol.append(4)  # 向上移
                                elif (pos_2 - pos_1 == -col_num):
                                    Opt_sol.append(5)  # 向下移
                                elif (pos_2 - pos_1 == 1):
                                    Opt_sol.append(6)  # 向左移
                                elif (pos_2 - pos_1 == -1):
                                    Opt_sol.append(7)  # 向右移

                                # 更新空格的位置
                                empty_cell_pos[i] = pos_1

                        print('z ', key, ' = ', round(z[key].x, 0))
                        f.write(sol_str)

                f.write('\n----- 最优解 (逐步展示的版本)--- \n')
                Optimal_step_num = (int)(round(model.ObjVal, 0))  
                for k in range(Optimal_step_num + 1): 
                    PBS_warehouse_k = np.zeros([row_num, col_num])
                    for p in pos_set:
                        temp = x[k, p].x
                        col_ID = p % col_num
                        row_ID = (int)(p / col_num)
                        PBS_warehouse_k[row_ID][col_ID] = round(temp, 0)
                    for r in range(len(desired_items_pos)):
                        for p in pos_set:
                            if (y[k, p, r].x > 0.1):
                                col_ID = p % col_num
                                row_ID = (int)(p / col_num)
                                PBS_warehouse_k[row_ID][col_ID] = round(2 * y[k, p, r].x, 0)  # round(2 * y[k, p, d].x, 0)
                                # print('y ', k, p, r, ' = ', y[k, p, r].x)
                                break
                    print('\n -------- 第 %2d 步 --------\n' % k)
                    f.write('\n -------- 第 %2d 步 --------\n' % k)
                    f.write(str(PBS_warehouse_k))
                    print(PBS_warehouse_k)

                f.write('\n\n Solution End \n\n')
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
CPU_time, Opt_Obj = build_and_solve_PBS_NIPF_model(row_num, col_num, Adj_dict, Max_Step,
                                   pos_set, init_occupy_state, desired_item_set,
                                   IO_point_set, empty_cell_pos)

