def enumerate_solve_set_covering(universe_set, subset_set):
    """
    :param universe_set: 包含所有元素的集合
    :param subset_set: 所有子集的集合
    :return:
    """

    # 导包
    from itertools import combinations
    import numpy as np

    # 穷举出所有的选择方案，所有可能的方案为 2^n - 1个，其中n为全集的元素个数
    all_combinations = []
    index_list_of_S = [i for i in range(len(subset_set))]
    for n in range(1, len(subset_set)+1):
        for c in combinations(index_list_of_S, n):
            all_combinations.append(c)

    print('所有可能的组合数：', len(all_combinations))
    print('所有可能的组合：', all_combinations)

    # 判断每个组合是否是可行的，并计算对应的成本，筛选出最优解
    min_cost = np.inf
    optimal_sol = []
    for sol in all_combinations:
        temp_cost = 0
        sol_list = list(sol)
        temp_set = set(subset_set[sol_list[0]][0])
        for selected_subset_ID in sol_list:
            temp_set = set(subset_set[selected_subset_ID][0]) | temp_set  # 求并集
            temp_cost += subset_set[selected_subset_ID][1]

        if(temp_set == set(universe_set) and temp_cost < min_cost):
            min_cost = temp_cost
            optimal_sol = sol

    # 输出最优解
    print('最优解选择的子集为：{}'.format(optimal_sol))
    print('最小成本为：{}'.format(min_cost))

""" 数值实验 """

# 设置全集
universe_set = [1, 2, 3, 4, 5, 6]
# 设置子集的集合
# [[1, 3], 4]表示：子集为[1, 3]，对应的成本为4
subset_set = {0: [[1, 3], 4],
              1: [[1, 2, 3, 4], 6],
              2: [[4, 5, 6], 2],
              3: [[4, 6], 1]}

# 调用穷举求解函数求解集覆盖问题
enumerate_solve_set_covering(universe_set, subset_set)



