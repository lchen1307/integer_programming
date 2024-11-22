"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 无人机与卡车联合配送问题 - Gurobi Python接口代码实现
author: 刘兴禄
date: 2017-10-30
"""

from gurobipy import *
import re
import math
import matplotlib.pyplot as plt
import numpy as np

"""
定义数据类
"""
class Data(object):
    """
    存储算例数据的类
    """
    def __init__(self):
        self.customer_num = 0            # 客户数量
        self.node_num = 0                # 点的数量
        self.range = 0                  # 无人机的飞行范围
        self.lunching_time = 0           # 发射无人机消耗的时间
        self.recover_time = 0            # 回收无人机消耗的时间
        self.cor_X = []                 # 点的横坐标
        self.cor_Y = []                 # 点的纵坐标
        self.demand = []                # 客户点的需求
        self.service_time = []           # 服务时间
        self.ready_time = []             # 最早开始时间
        self.due_time = []               # 最晚结束时间
        self.dis_matrix = [[]]           # 点的距离矩阵

    # 读取数据的函数
    def read_data(self, path, customer_num):
        """
        读取算例数据中前customer_num个顾客的数据。

        :param path: 文件路径
        :param customer_num: 顾客数量
        :return:
        """
        self.customer_num = customer_num
        self.node_num = customer_num + 2
        f = open(path, 'r')
        lines = f.readlines()
        count = 0
        # 读取数据信息
        for line in lines:
            count = count + 1
            if (count == 2):
                line = line[:-1]
                str = re.split(r" +", line)
                self.range = float(str[0])
            elif (count == 5):
                line = line[:-1]
                str = re.split(r" +", line)
                self.lunching_time = float(str[0])
                self.recover_time = float(str[1])
            elif (count >= 9 and count <= 9 + customer_num):
                line = line[:-1]
                str = re.split(r" +", line)
                self.cor_X.append(float(str[2]))
                self.cor_Y.append(float(str[3]))
                self.demand.append(float(str[4]))
                self.ready_time.append(float(str[5]))
                self.due_time.append(float(str[6]))
                self.service_time.append(float(str[7]))

        # 复制一份depot
        self.cor_X.append(data.cor_X[0])
        self.cor_Y.append(data.cor_Y[0])
        self.demand.append(data.demand[0])
        self.ready_time.append(data.ready_time[0])
        self.due_time.append(data.due_time[0])
        self.service_time.append(data.service_time[0])

        # 计算距离矩阵
        self.dis_matrix = np.zeros((self.node_num, self.node_num))
        for i in range(0, self.node_num):
            for j in range(0, self.node_num):
                temp = (self.cor_X[i] - self.cor_X[j]) ** 2 + (self.cor_Y[i] - self.cor_Y[j]) ** 2
                self.dis_matrix[i][j] = math.sqrt(temp)
                temp = 0

    # 打印算例数据
    def print_data(self, customer_num):
        print("\n------- 无人机参数 --------")
        print("%-20s %4d" % ('UAV range: ', self.range))
        print("%-20s %4d" % ('UAV lunching time: ', self.lunching_time))
        print("%-20s %4d" % ('UAV recover time: ', self.recover_time))
        print("\n------- 点的信息 --------")
        print('%-10s %-8s %-6s %-6s' % ('需求', '起始时间', '截止时间', '服务时间'))
        for i in range(len(self.demand)):
            print('%-12.1f %-12.1f %-12.1f %-12.1f' % (self.demand[i], self.ready_time[i], self.due_time[i], self.service_time[i]))

        print("-------距离矩阵-------\n")
        for i in range(self.node_num):
            for j in range(self.node_num):
                print("%6.2f" % (self.dis_matrix[i][j]), end=" ")
            print()
			
			


class Model_builder(object):
    """
    构建模型的类。
    """

    def __init__(self):
        self.model = None           # 模型
        self.big_M = 10000
        # X[i, j]
        self.X = [([0] * data.node_num) for j in range(data.node_num)]
        # Y[i, j, k]
        self.Y = [[([0] * data.node_num) for j in range(data.node_num)] for i in range(data.node_num)]
        # U[i]
        self.U = [[0] for i in range(data.node_num)]
        # P[i, j]
        self.P = [[[0] for j in range(data.node_num)] for i in range(data.node_num)]
        # T[i], T[i]'
        self.T = [[0] for i in range(data.node_num)]
        self.Tt = [[0] for i in range(data.node_num)]

    def build_model(self, data=None, solve_model=False):
        """
        构建模型的类。

        :param data: 算例数据
        :param solve_model: 是否求解模型
        :return:
        """

        # 创建模型对象
        self.model = Model("FSTSP")

        # 创建决策变量
        for i in range(data.node_num):
            name1 = 'U_' + str(i)
            name2 = 'T_' + str(i)
            name3 = 'Tt_' + str(i)
            self.U[i] = self.model.addVar(lb=0, ub=data.node_num, vtype=GRB.CONTINUOUS, name=name1)
            self.T[i] = self.model.addVar(lb=0, ub=self.big_M, vtype=GRB.CONTINUOUS, name=name2)
            self.Tt[i] = self.model.addVar(lb=0, ub=self.big_M, vtype=GRB.CONTINUOUS, name=name3)
            for j in range(data.node_num):
                name4 = 'X_' + str(i) + "_" + str(j)
                name5 = 'P_' + str(i) + "_" + str(j)
                self.X[i][j] = self.model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=name4)
                self.P[i][j] = self.model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=name5)
                for k in range(data.node_num):
                    name6 = 'Y_' + str(i) + "_" + str(j) + "_" + str(k)
                    self.Y[i][j][k] = self.model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=name6)

        # 创建目标函数
        self.model.setObjective(self.T[data.node_num - 1], GRB.MINIMIZE)

        # 约束 1: 每个点均被访问
        for j in range(1, data.node_num - 1):  # 这里需要注意，i的取值范围，否则可能会加入空约束
            expr = LinExpr(0)
            for i in range(0, data.node_num - 1):           # i in N0
                if (i != j):
                    expr.addTerms(1, self.X[i][j])
                    for k in range(1, data.node_num):       # k in N+
                        if (i != k and j != k):
                            expr.addTerms(1, self.Y[i][j][k])

            self.model.addConstr(expr == 1, "c1")

        # 约束 2: 卡车从起点出发一次
        expr = LinExpr(0)
        for j in range(1, data.node_num):
            expr.addTerms(1, self.X[0][j])
        self.model.addConstr(expr == 1, "c2")

        # 约束 3: 卡车到达终点一次
        expr = LinExpr(0)
        for i in range(data.node_num - 1):
            expr.addTerms(1, self.X[i][data.node_num - 1])
        self.model.addConstr(expr == 1.0, "c3")

        # 约束 4: 卡车到达终点一次
        for i in range(1, data.node_num - 1):
            for j in range(1, data.node_num):
                if (i != j):
                    self.model.addConstr(self.U[i] - self.U[j] + 1 <= self.big_M * (1 - self.X[i][j]), 'c4')

        # 约束 5: 流平衡约束
        for j in range(1, data.node_num - 1):
            expr1 = LinExpr(0)
            expr2 = LinExpr(0)
            for i in range(0, data.node_num - 1):
                if (j != i):
                    expr1.addTerms(1, self.X[i][j])

            for k in range(1, data.node_num):
                if (j != k):
                    expr2.addTerms(1, self.X[j][k])

            self.model.addConstr(expr1 == expr2, "c5")

        # 约束 6
        for i in range(data.node_num - 1):
            expr = LinExpr(0)
            for j in range(1, data.node_num - 1):
                if (i != j):
                    for k in range(1, data.node_num):
                        if (i != k and j != k):
                            expr.addTerms(1, self.Y[i][j][k])
            self.model.addConstr(expr <= 1, 'c6')

        # 约束 7
        for k in range(1, data.node_num):
            expr = LinExpr(0)
            for i in range(0, data.node_num - 1):
                if (i != k):
                    for j in range(1, data.node_num - 1):
                        if (j != i and j != k):
                            expr.addTerms(1, self.Y[i][j][k])
            self.model.addConstr(expr <= 1, 'c7')

        # 约束 8
        for i in range(1, data.node_num - 1):
            for j in range(1, data.node_num):
                for k in range(1, data.node_num):
                    if (i != j and i != k and j != k):
                        expr1 = LinExpr(0)
                        expr2 = LinExpr(0)
                        for h in range(data.node_num - 1):
                            if (h != i):
                                expr1.addTerms(1, self.X[h][i])
                        for l in range(1, data.node_num - 1):
                            if (l != k):
                                expr2.addTerms(1, self.X[l][k])
                        self.model.addConstr(2 * self.Y[i][j][k] <= expr1 + expr2, "c8")

        # 约束 9
        for j in range(1, data.node_num - 1):
            for k in range(1, data.node_num):
                if (j != k):
                    expr = LinExpr(0)
                    for h in range(1, data.node_num - 1):
                        expr.addTerms(1, self.X[h][k])
                    self.model.addConstr(self.Y[0][j][k] <= expr, "c9")

        # 约束 10
        for i in range(1, data.node_num - 1):
            for k in range(1, data.node_num):
                if (k != i):
                    expr = LinExpr(0)
                    for j in range(1, data.node_num - 1):
                        if (i != j and j != k):
                            expr.addTerms(self.big_M, self.Y[i][j][k])
                    self.model.addConstr(self.U[k] - self.U[i] >= 1 - self.big_M + expr, "c10")

        # 约束 11
        for i in range(1, data.node_num - 1):
            expr = LinExpr(0)
            for j in range(1, data.node_num - 1):
                for k in range(1, data.node_num):
                    if (j != i and i != k and j != k):
                        expr.addTerms(self.big_M, self.Y[i][j][k])
            self.model.addConstr(self.Tt[i] >= self.T[i] - self.big_M + expr, "c12")

        # 约束 12
        for i in range(1, data.node_num - 1):
            expr = LinExpr(0)
            for j in range(1, data.node_num - 1):
                for k in range(1, data.node_num):
                    if (j != i and i != k and j != k):
                        expr.addTerms(self.big_M, self.Y[i][j][k])
            self.model.addConstr(self.Tt[i] <= self.T[i] + self.big_M - expr, "c12")

        # 约束 13
        for k in range(1, data.node_num):
            expr = LinExpr(0)
            for i in range(0, data.node_num - 1):
                for j in range(1, data.node_num - 1):
                    if (j != i and i != k and j != k):
                        expr.addTerms(self.big_M, self.Y[i][j][k])
            self.model.addConstr(self.Tt[k] >= self.T[k] - self.big_M + expr, "c13")

        # 约束 14
        for k in range(1, data.node_num):
            expr = LinExpr(0)
            for i in range(0, data.node_num - 1):
                for j in range(1, data.node_num - 1):
                    if (j != i and i != k and j != k):
                        expr.addTerms(self.big_M, self.Y[i][j][k])
            self.model.addConstr(self.Tt[k] <= self.T[k] + self.big_M - expr, "c14")


        # 约束 15
        for h in range(data.node_num - 1):
            for k in range(1, data.node_num):
                if (h != k):
                    expr1 = LinExpr(0)
                    expr2 = LinExpr(0)
                    for l in range(1, data.node_num - 1):
                        for m in range(1, data.node_num):
                            if (k != l and k != m and l != m):
                                expr1.addTerms(data.lunching_time, self.Y[k][l][m])

                    for i in range(data.node_num - 1):
                        for j in range(1, data.node_num - 1):
                            if (i != j and i != k and j != k):
                                expr2.addTerms(data.recover_time, self.Y[i][j][k])
                    self.model.addConstr(self.T[k] >= self.T[h] + data.dis_matrix[h][k] + expr1 + expr2 - self.big_M + self.big_M * self.X[h][k],
                                    "c15")

        # 约束 16
        for j in range(1, data.node_num - 1):
            for i in range(data.node_num - 1):
                if (i != j):
                    expr = LinExpr(0)
                    for k in range(1, data.node_num):
                        if (i != k and j != k):
                            expr.addTerms(self.big_M, self.Y[i][j][k])
                    self.model.addConstr(self.Tt[j] >= self.Tt[i] + data.dis_matrix[i][j] - self.big_M + expr, "c16")

        # 约束 17
        for j in range(1, data.node_num - 1):
            for k in range(1, data.node_num):
                if (k != j):
                    expr = LinExpr(0)
                    for i in range(data.node_num - 1):
                        if (i != k and i != j):
                            expr.addTerms(self.big_M, self.Y[i][j][k])
                    self.model.addConstr(self.Tt[k] >= self.Tt[j] + data.dis_matrix[j][k] + data.recover_time - self.big_M + expr, "c17")

        # 约束 18
        for k in range(1, data.node_num):
            for j in range(1, data.node_num - 1):
                for i in range(data.node_num - 1):
                    if (i != j and i != k and j != k):
                        self.model.addConstr(
                            self.Tt[k] - self.Tt[j] + data.dis_matrix[i][j] <= data.range + self.big_M - self.big_M * self.Y[i][j][k], "c18")

        # 约束 19
        for i in range(1, data.node_num - 1):
            for j in range(1, data.node_num - 1):
                if (i != j):
                    self.model.addConstr(self.U[i] - self.U[j] >= 1 - self.big_M * self.P[i][j], "c19")

        # 约束 20
        for i in range(1, data.node_num - 1):
            for j in range(1, data.node_num - 1):
                if (i != j):
                    self.model.addConstr(self.U[i] - self.U[j] <= -1 + self.big_M - self.big_M * self.P[i][j], "c20")

        # 约束 21
        for i in range(1, data.node_num - 1):
            for j in range(1, data.node_num - 1):
                if (i != j):
                    self.model.addConstr(self.P[i][j] + self.P[j][i] == 1, "c21")

        # 约束 22
        for i in range(data.node_num - 1):
            for k in range(1, data.node_num):
                for l in range(1, data.node_num - 1):
                    if (k != i and l != i and l != k):
                        expr1 = LinExpr(0)
                        expr2 = LinExpr(0)
                        for j in range(1, data.node_num - 1):
                            if (k != j and i != j):
                                expr1.addTerms(self.big_M, self.Y[i][j][k])
                        for m in range(1, data.node_num - 1):
                            for n in range(1, data.node_num):
                                if (l != m and l != n and m != n):
                                    expr2.addTerms(self.big_M, self.Y[l][m][n])
                        self.model.addConstr(self.Tt[l] >= self.Tt[k] - 3 * self.big_M + expr1 + expr2 + self.big_M * self.P[i][l], "c22")

        # 约束 23
        self.model.addConstr(self.T[0] == 0, "c23")

        # 约束 24
        self.model.addConstr(self.Tt[0] == 0, "c24")

        # 约束 25
        for j in range(1, data.node_num - 1):
            self.model.addConstr(self.P[0][j] == 1, "c25")

        # 约束 26
        for i in range(data.node_num):
            for j in range(data.node_num):
                if (i == j):
                    self.model.addConstr(self.X[i][j] == 0, "c26")
                for k in range(data.node_num):
                    if (i == j or i == k or k == j):
                        self.model.addConstr(self.Y[i][j][k] == 0, "c27")

        # 求解模型
        self.model.write('FSTSP.lp')
        self.model.Params.timelimit = 1200
        if(solve_model == True):
            self.model.optimize()



class Solution(object):
    """
    Solution类，用于记录关于解的信息。
    """
    def __init__(self):
        self.ObjVal = 0             # 目标函数值
        self.X = [[]]               # 决策变量 X[i, j] 的取值
        self.Y = [[[]]]             # 决策变量 Y[i, j, k] 的取值
        self.U = []                 # 决策变量 U[i] 的取值
        self.P = []                 # 决策变量 P[i, j] 的取值
        self.T = []                 # 决策变量 T[i] 的取值
        self.Tt = []                # 决策变量 T[i]' 的取值
        self.route_truck = []        # 卡车的路径
        self.route_UAV = []          # 无人机的路径

    def get_solution(self, data, model):
        """
        从模型获得解的信息。

        :param data: 算例数据对象
        :param model: 模型
        :return:
        """
        self.ObjVal = model.ObjVal
        # X[i, j]
        self.X = [([0] * data.node_num) for j in range(data.node_num)]
        # Y[i, j, k]
        self.Y = [[([0] * data.node_num) for j in range(data.node_num)] for i in range(data.node_num)]
        # U[i]
        self.U = [[0] for i in range(data.node_num)]
        # P[i, j]
        self.P = [[[0] for j in range(data.node_num)] for i in range(data.node_num)]
        # T[i], T[i]'
        self.T = [[0] for i in range(data.node_num)]
        self.Tt = [[0] for i in range(data.node_num)]

        for m in model.getVars():
            str = re.split(r"_", m.VarName)
            if (str[0] == "X" and m.x > 0.5):
                self.X[int(str[1])][int(str[2])] = round(m.x, 0)
                print(str, end="")
                print(" = %d" % m.x)
            elif (str[0] == "Y" and m.x > 0.5):
                self.Y[int(str[1])][int(str[2])][int(str[3])] = round(m.x, 0)
            elif (str[0] == "U" and m.x > 0):
                self.U[int(str[1])] = m.x
            elif (str[0] == "T" and m.x > 0):
                self.T[int(str[1])] = m.x
            elif (str[0] == "Tt" and m.x > 0):
                self.Tt[int(str[1])] = m.x
            elif (str[0] == "P" and m.x > 0):
                self.P[int(str[1])][int(str[2])] = m.x

        # 提取truck和无人机的路径
        print('提取truck和无人机的路径')
        current_node = 0
        self.route_truck.append(current_node)
        while(current_node != data.node_num-1):
            for j in range(data.node_num):
                if (self.X[current_node][j] == 1):
                    if(j != data.node_num - 1):
                        self.route_truck.append(j)
                    current_node = j
                    break
        self.route_truck.append(0)
        print('提取truck和无人机的路径：结束')

        # 提取出无人机的路径
        count = 0
        for i in range(data.node_num):
            for j in range(data.node_num):
                for k in range(data.node_num):
                    if (self.Y[i][j][k] == 1):
                        count = count + 1
                        temp = [i, j, k]
                        self.route_UAV.append(temp)

        print("\n\n 最优目标值：%.2f " % self.ObjVal)
        print("\n\n ------ 卡车的路径 ------- ")
        print('[', end='')
        for i in range(len(self.route_truck)):
            print(" %d " % self.route_truck[i], end=" ")
        print(']')

        print("\n\n ------ 无人机的路径 ------- ")
        for i in range(len(self.route_UAV)):
            print("UAV %d :[%d - %d - %d]" % (i, self.route_UAV[i][0], self.route_UAV[i][1], self.route_UAV[i][2]))

    def plot_solution(self, file_name=None, customer_num=0):
        """
        将解进行可视化。

        :param file_name: 存储的文件名
        :param customer_num: 顾客的数量
        :return:
        """

        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

        font_dict_1 = {'family': 'Arial',   # serif
                     'style': 'normal',     # 'italic',
                     'weight': 'normal',
                     'color': 'darkred',
                     'size': 30,
                     }

        font_dict_2 = {'family': 'Arial',    # serif
                      'style': 'normal',    # 'italQic',
                      'weight': 'normal',
                      'size': 24,
                      }

        # ax.set_aspect('equal')
        # ax.grid(which='minor', axis='both')
        # ax.set_xlim(0, 100)
        # ax.set_ylim(0, 100)

        ax.set_xlabel(r'$x$', fontdict=font_dict_1)
        ax.set_ylabel(r'$y$', fontdict=font_dict_1)
        # ax.set_xticklabels(labels=[38, 39, 40, 41, 42, 43, 44, 45, 46, 47], fontdict=font_dict_2, minor=False)
        # ax.set_yticklabels(labels=[50, 52.5, 55, 57.5, 60, 65, 70, 75], fontdict=font_dict_2, minor=False)

        title_text_str = 'Optimal Solution for FSTSP (' + str(customer_num) + ' customers)'
        ax.set_title(title_text_str, fontdict=font_dict_1)

        # 画出depot和顾客
        # ax.scatter(data.cor_X[0], data.cor_Y[0], c='black', alpha=1, marker='s', s=20, linewidths=5, label='depot')
        # ax.scatter(data.cor_X[1:-1], data.cor_Y[1:-1], c='gray', alpha=1, marker='p', s=15, linewidths=5, label='customer')  # c='red'定义为红色，alpha是透明度，marker是画的样式
        line_depot_x = [data.cor_X[0]]
        line_depot_y = [data.cor_Y[0]]

        line_customer_x = []
        line_customer_y = []
        for i in range(1, len(data.cor_X)-1):
            line_customer_x.append(data.cor_X[i])
            line_customer_y.append(data.cor_Y[i])

        line_1, = ax.plot(line_depot_x, line_depot_y, c='black', marker='s',markersize=20, linewidth=0, zorder=10)
        line_2, = ax.plot(line_customer_x, line_customer_y, c='brown', marker='p', markersize=15, linewidth=0, zorder=10)


        # 画出卡车的路线
        line_data_truck_x = []
        line_data_truck_y = []
        line_text_x_coor = []
        line_text_y_coor = []
        for i in range(len(self.route_truck)-1):
            current_node = self.route_truck[i]
            line_data_truck_x.append(data.cor_X[current_node])
            line_data_truck_y.append(data.cor_Y[current_node])

            line_text_x_coor.append(data.cor_X[current_node] - 0.2)
            line_text_y_coor.append(data.cor_Y[current_node])
            plt.text(data.cor_X[current_node] - 0.2, data.cor_Y[current_node], str(current_node), fontdict=font_dict_2)
        line_data_truck_x.append(data.cor_X[self.route_truck[-1]])
        line_data_truck_y.append(data.cor_Y[self.route_truck[-1]])

        # 画出无人机的路线
        line_data_UAV_x = []
        line_data_UAV_y = []
        line_UAV_text_x_coor = []
        line_UAV_text_y_coor = []
        temp_x = []
        temp_y = []
        for i in range(data.node_num):
            for j in range(data.node_num):
                for k in range(data.node_num):
                    if (self.Y[i][j][k] == 1):
                        temp_x.append(data.cor_X[i])
                        temp_x.append(data.cor_X[j])
                        temp_x.append(data.cor_X[k])

                        temp_y.append(data.cor_Y[i])
                        temp_y.append(data.cor_Y[j])
                        temp_y.append(data.cor_Y[k])

                        line_UAV_text_x_coor.append(data.cor_X[j] - 0.2)
                        line_UAV_text_y_coor.append(data.cor_Y[j])
                        plt.text(data.cor_X[j] - 0.2, data.cor_Y[j], str(j), fontdict=font_dict_2)

                        if(len(temp_x) > 0):
                            line_data_UAV_x.append(temp_x)
                            line_data_UAV_y.append(temp_y)
                            temp_x = []
                            temp_y = []


        line_3, = ax.plot(line_data_truck_x, line_data_truck_y, c='blue', linewidth=3)
        line_4, = ax.plot(line_data_UAV_x[0], line_data_UAV_y[0], c='red', linewidth=3, linestyle = ':')
        for i in range(1, len(line_data_UAV_x)):
            ax.plot(line_data_UAV_x[i], line_data_UAV_y[i], c='red', linewidth=3, linestyle=':')

        # 画出箭头
        for i in range(len(self.route_truck)-1):
            start = self.route_truck[i]
            end = self.route_truck[i + 1]
            plt.arrow(data.cor_X[start], data.cor_Y[start], data.cor_X[end] - data.cor_X[start], data.cor_Y[end] - data.cor_Y[start],
                      length_includes_head=True, head_width=0.1, head_length=0.5, lw=3,
                      color='blue')

        ax.legend([line_1, line_2, line_3, line_4],
                  ['depot', 'customer', 'truck route', 'UAV route'],
                  loc='best', prop=font_dict_2
                  # , bbox_to_anchor=(1, 1, 0, 0)  # 分别控制比例，x, y, width, height
                    )

        # 导出图片
        plt.savefig(file_name)
        plt.show()

if __name__ == "__main__":
    # 调用函数读取数据
    data = Data()
    path = 'instances/c101.txt'
    customer_num = 9
    data.read_data(path, customer_num)
    data.print_data(customer_num)

    # 建立模型并求解
    model_handler = Model_builder()
    model_handler.build_model(data=data, solve_model=True)

    # 获取解并可视化
    solution = Solution()
    solution.get_solution(data, model_handler.model)
    file_name = str(customer_num)+ '_customer.pdf'
    solution.plot_solution(file_name=file_name, customer_num=customer_num)		
			
			