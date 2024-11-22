import numpy as np
import random
import itertools
import math

random.seed(42)                 # 设置随机生成器的种子
city_num = 8                    # 城市的数量

# 生成随机的城市坐标
def generate_loc(node_num):
    node_loc = [(random.randint(1, 100), random.randint(1, 100)) for i in range(0, city_num)]
    return node_loc

# 计算城市间的距离矩阵
def calc_dis_matric(city_num, loc):
    # dis_matrix = np.zeros((city_num, city_num), dtype=np.complex_)
    dis_matrix = np.zeros((city_num, city_num))

    for i in range(city_num):
        for j in range(city_num):
            node1_x = loc[i][0]
            node1_y = loc[i][1]
            node2_x = loc[j][0]
            node2_y = loc[j][1]
            dis_matrix[int(i)][int(j)] = math.sqrt((node1_x - node2_x)**2 + (node1_y - node2_y)**2)
    return dis_matrix

# 计算路径的距离
def cal_route_dis(city_num, dis_matrix):
    route_length = city_num - 1
    route_dis_dict = {}
    min_paths = []
    min_dis = float('Inf')
    all_min_dis = [float('Inf') for i in range(len(dis_matrix))]

    paths = itertools.permutations(range(city_num))
    for path in paths:
        key = path
        route_dis = sum([dis_matrix[path[i]][path[i + 1]] for i in range(route_length)] + [dis_matrix[path[-1]][path[0]]])
        route_dis_dict[key] = route_dis

        if route_dis < min_dis:
            min_dis = route_dis
            min_paths = []
            min_paths.append(path)
        elif min_dis == route_dis:
            min_paths.append(path)

    return min_paths, route_dis_dict


city_loc = generate_loc(city_num)                   # 生成随机城市坐标
dis_matrix = calc_dis_matric(city_num, city_loc)    # 计算距离矩阵

min_paths, route_dis = cal_route_dis(city_num, dis_matrix)      # 使用穷举法求解TSP，遍历所有的可行路径

# 输出结果
for path in min_paths:
    print(f'最短路径为: {path}, 距离 = {route_dis[path]}')