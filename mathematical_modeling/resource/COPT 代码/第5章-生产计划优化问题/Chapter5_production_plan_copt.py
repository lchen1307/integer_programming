"""
booktitle: 《数学建模与数学规划：方法、案例及实战 Python+COPT+Gurobi实现》
name: 生产计划优化问题--COPT Python接口代码实现
author: 杉数科技
date: 2022-10-11
"""

class Instance():
    ''' 定义算例数据 '''

    def __init__(self):
        self.period_num = 7                      # 周期数
        self.raw_material_cost = 90              # 原材料成本
        self.unit_product_time = 5               # 单位产品需要的工时
        self.price = 300                         # 产品售价
        self.init_employee_num = 1000            # 1月初剩余的员工个数
        self.init_inventory = 15000              # 1月初的员工数量
        self.normal_unit_salary = 30             # 正常单位工时工资
        self.overtime_unit_salary = 40           # 加班单位工时工资
        self.work_day_num = 20                   # 每月工作的天数
        self.work_time_each_day = 8              # 员工每天的正常工作时间
        self.overtime_upper_limit = 20           # 每个工人每月的加班工时上限
        self.outsource_unit_cost = 200           # 外包单位成本
        self.unit_inventory_cost = 15            # 单位库存成本
        self.unit_shortage_cost = 35             # 单位缺货成本
        self.hire_cost = 5000                    # 单个工人的雇佣成本
        self.fire_cost = 8000                    # 单个工人的解雇成本
        self.inventory_LB_of_last_month = 10000  # 6月底的最低库存要求

        # 预测需求量（12月的用0补充）
        self.demand = [0, 20000, 40000, 42000, 35000, 19000, 18500]




from coptpy import *

def build_production_plan_model_and_solve(instance=None):
    """ 完整函数代码见附配电子资源。 """


    '''
    创建模型实例
    '''
    env = Envr()
    model = env.createModel('production model')

    '''
    创建决策变量
    '''
    x, y, I, e, H, F, L, P, S, O, z = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
    for i in range(instance.period_num):
        x[i] = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.INTEGER, name='x_'+str(i))
        y[i] = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.INTEGER, name='y_'+str(i))
        I[i] = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.INTEGER, name='I_'+str(i))
        e[i] = model.addVar(lb=-COPT.INFINITY, ub=COPT.INFINITY, vtype=COPT.INTEGER, name='e_'+str(i))
        H[i] = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.INTEGER, name='H_'+str(i))
        F[i] = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.INTEGER, name='F_'+str(i))
        L[i] = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.INTEGER, name='L_'+str(i))
        P[i] = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.INTEGER, name='P_'+str(i))
        S[i] = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.INTEGER, name='S_'+str(i))
        O[i] = model.addVar(lb=0, ub=COPT.INFINITY, vtype=COPT.CONTINUOUS, name='O_'+str(i))
        z[i] = model.addVar(lb=0, ub=1, vtype=COPT.BINARY, name='z_'+str(i))

    '''
    创建目标函数
    '''
    obj = LinExpr()
    for i in range(1, instance.period_num):
        obj.addTerms(S[i],instance.price)
        obj.addTerms(x[i],-instance.raw_material_cost)
        obj.addTerms(y[i],-instance.outsource_unit_cost)
        obj.addTerms(O[i],-instance.overtime_unit_salary)
        obj.addTerms(P[i],-instance.normal_unit_salary * instance.work_day_num * instance.work_time_each_day)
        obj.addConstant(-instance.init_inventory * instance.unit_inventory_cost)
        obj.addTerms(I[i],-instance.unit_inventory_cost)
        obj.addTerms(L[i],-instance.unit_shortage_cost)
        obj.addTerms(H[i],-instance.hire_cost)
        obj.addTerms(F[i],-instance.fire_cost)


    model.setObjective(obj, COPT.MAXIMIZE)

    '''
    添加约束
    '''
    # 约束1-5
    big_M = 1000000
    model.addConstr(I[0] == instance.init_inventory)
    model.addConstr(P[0] == instance.init_employee_num)
    model.addConstr(L[0] == 0)
    model.addConstr(S[0] == 0)
    model.addConstr(I[instance.period_num-1] >= instance.inventory_LB_of_last_month)
    model.addConstr(H[0] == 0)
    model.addConstr(F[0] == 0)
    model.addConstr(e[0] == 0)
    model.addConstr(x[0] == 0)
    model.addConstr(y[0] == 0)
    model.addConstr(z[0] == 0)
    model.addConstr(O[0] == 0)

    # 约束6-14
    for i in range(1, instance.period_num):
        # 约束6
        model.addConstr(I[i-1] + x[i] + y[i] + e[i] == instance.demand[i], name='instance.demand_'+str(i))

        # 约束7
        model.addConstr(I[i-1] + x[i] + y[i] - S[i] == I[i], name='inventory_' + str(i))

        # 约束8
        model.addConstr(e[i] - big_M * z[i] <= 0, name='shortage1_' + str(i))

        # 约束9
        model.addConstr(1 - e[i] - big_M * (1 - z[i]) <= 0, name='shortage2_' + str(i))

        # 约束10
        model.addConstr(L[i] - e[i] - big_M * (1 - z[i]) <= 0, name='shortage3_' + str(i))

        # 约束11
        model.addConstr(e[i] - L[i] - big_M * (1 - z[i]) <= 0, name='shortage3_' + str(i))

        # 约束12
        model.addConstr(S[i] == instance.demand[i] - L[i], name='sale_' + str(i))

        # 约束13
        model.addConstr(P[i-1] + H[i] - F[i] == P[i], name='employee_' + str(i))

        # 约束14
        model.addConstr(instance.unit_product_time * x[i] <= P[i] * instance.work_time_each_day * instance.work_day_num + O[i], name='time_' + str(i))

        # 约束15
        model.addConstr(O[i] <= instance.overtime_upper_limit * P[i], name='instance.overtime_upper_limit_' + str(i))

    '''
    求解模型并输出结果
    '''
    model.write('production.lp')
    model.solve()

    print('---------------  最优解 ----------------')
    print('最优总净利润：%10d \n' % model.ObjVal)

    print('详细计划为\n====================')
    print('|%2s|%4s|  %2s | %2s |  %2s  |%2s| %4s | %4s | %4s |%2s|%3s|%4s|%4s|'
        % ('月份', '期初库存', '生产', '外包', '差值', '缺货', '需求', '销售', '库存'
            , '雇佣', '解雇', '可用员工', '加班时长'))

    for i in range(0, instance.period_num):
        print('%2d' % (i), end='')
        if(i == 0):
            print(' %9d ' % (I[0].x), end='')
        else:
            print(' %9d ' % (I[i - 1].x), end='')
        print('%8d' % (x[i].x), end='')
        print('%7d' % (y[i].x), end='')
        print('%9d' % (e[i].x), end='')
        print('%5d' % (L[i].x), end='')
        print('%9d' % (instance.demand[i]), end='')
        print('%9d' % (S[i].x), end='')
        print('%9d' % (I[i].x), end='')
        print('%5d' % (H[i].x), end='')
        print('%6d' % (F[i].x), end='')
        print('%8d' % (P[i].x), end='')
        print('%8d' % (O[i].x), end='')
        print()


if __name__ == '__main__':
    realized_Instance = Instance()
    build_production_plan_model_and_solve(realized_Instance)