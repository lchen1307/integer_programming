from __future__ import division, print_function

from bokeh.layouts import column
from gurobipy import *

class MCTP:
    def __init__(self):
        # initialize data
        self.NumOrg = 0
        self.NumDes = 0
        self.NumProduct = 0
        self.Supply = []
        self.Demand = []
        self.Capacity = []
        self.Cost = []

        # initialize variables and constraints in RMP
        self.CapacityCons = [] # capacity constraints
        self.var_lambda = [] # decision variable of RMP, i.e., columns

        # initialize variables in subproblem
        self.var_x = []

        # initialize parameters
        self.Iter = 0
        self.dual_convexCons = 1
        # 凸组合约束的对偶变量，更新子问题目标函数使用
        # 这里赋予一个初值1，为了在第一次迭代的时候，子问题目标函数能小于0
        # ，能有新的检验数为负的列产生
        self.dual_CapacityCons = []
        # 容量约束的对偶变量，更新子问题目标函数使用
        self.SP_totalCost = []
        # 子问题的解产生的总运输成本，在添加新列的时候，是新变量的目标函数系数

    def readData(self, filename):
        with open(filename, 'r') as data:
            self.NumOrg = int(data.readline())
            self.NumDes = int(data.readline())
            self.NumProduct = int(data.readline())

            for i in range(self.NumOrg):
                col = data.readline().split()
                SupplyData = []
                for k in range(self.NumProduct):
                    SupplyData.append(float(col[k]))
                self.Supply.append(SupplyData)

            for j in range(self.NumDes):
                col = data.readline().split()
                DemandData = []
                for k in range(self.NumProduct):
                    DemandData.append(float(col[k]))
                self.Demand.append(DemandData)

            for i in range(self.NumOrg):
                CostData = []
                for j in range(self.NumDes):
                    col = data.readline().split()
                    CostData_temp = []
                    for k in range(self.NumProduct):
                        CostData_temp.append(float(col[k]))
                    CostData.append(CostData_temp)
                self.Cost.append(CostData)

    def initializeModel(self):
        # initialize master problem and subproblem
        self.RMP = Model('RMP')
        self.subProblem = Model('subProblem')

        # close log information
        self.RMP.setParam('OutputFlag', 0)
        self.subProblem.setParam('OutputFlag', 0)

        # add initial artificial variable in RMP, in order to start the algorithm
        self.var_Artificial = self.RMP.addVar(lb = 0.0
                                              , ub = GRB.INFINITY
                                              , obj = 0.0
                                              , vtype=GRB.CONTINUOUS
                                              , name='Artificial')

        # add temp capacity constraints in RMP, in order to start the algorithm
        for i in range(self.NumOrg):
            CapCons_temp = []
            for j in range(self.NumDes):
                CapCons_temp.append(self.RMP.addConstr(-self.var_Artificial <= self.Capacity[i][j], name = 'capacity cons'))
            self.CapacityCons.append(CapCons_temp)

        # initialize the convex combination constraints
        self.convexCons = self.RMP.addConstr(1 * self.var_Artificial == 1, name = 'convex cons')

        # add variables to subproblem, x is flow on arcs
        for i in range(self.NumOrg):
            var_x_array = []
            for j in range(self.NumDes):
                var_x_temp = []
                for k in range(self.NumProduct):
                    var_x_temp.append(self.subProblem.addVar(lb = 0.0
                                                             , ub = GRB.INFINITY
                                                             , obj = 0.0
                                                             , vtype = GRB.CONTINUOUS))
                var_x_array.append(var_x_temp)
            self.var_x.append(var_x_array)

        # add constraints supply to subproblem
        for i in range(self.NumOrg):
            for k in range(self.NumProduct):
                self.subProblem.addConstr(quicksum(self.var_x[i][j][k] for j in range(self.NumDes))\
                                          == self.Supply[i][k], name = 'Supply_' + str(i) + '_' + str(k))

        # add constraints demand to subproblem
        for j in range(self.NumDes):
            for k in range(self.NumProduct):
                self.subProblem.addConstr(quicksum(self.var_x[i][j][k] for i in range(self.NumOrg))\
                                          == self.Demand[j][k], name = 'Demand_' + str(j) + '_' + str(k))

        # export the initial RMP with aitificial variable
        self.RMP.write('initial_RMP.lp')

    def optimizePhase_1(self):
        # initialize parameters
        for i in range(self.NumOrg):
            dual_capacity_temp = [0.0] * self.NumDes
            self.dual_CapacityCons.append(dual_capacity_temp)

        obj_master_phase_1 = self.var_Artificial
        obj_sub_phase_1 = -quicksum(self.dual_CapacityCons[i][j] * self.var_x[i][j][k] \
                                    for i in range(self.NumOrg) \
                                    for j in range(self.NumDes) \
                                    for k in range(self.NumProduct)) - self.dual_convexCons

        # set objective for RMP of Phase 1
        self.RMP.setObjective(obj_master_phase_1, GRB.MINIMIZE)

        # set objective for subproblem of Phase 1
        self.subProblem.setObjective(obj_sub_phase_1, GRB.MINIMIZE)

        # in order to make initial model is feasible, we set initial convex constraints to Null,
        # and in later iteration, we set the RHS of convex constraint to 1
        self.RMP.chgCoeff(self.convexCons, self.var_Artificial, 0.0)

        # Phase 1 of Danzig-Wolfe decomposition: to ensure the initial model is feasible
        print('---------- start Phase 1 optimization ----------')

        while True:
            print('Iter: ', self.Iter)
            # export the model and check whether it is correct
            self.RMP.write('solve_master.lp')
            # solve subproblem of Phase 1
            self.subProblem.optimize()

            if self.subProblem.objval >= -1e-6:
                print('No new column will be generated, coz no negative reduced cost columns')
                break
            else:
                self.Iter = self.Iter + 1

                # complete the total cost of subproblem solutions
                # the total cost is the coefficient of RMP when new column is added
                totalCost_subProblem = sum(self.Cost[i][j][k] * self.var_x[i][j][k].x \
                                           for i in range(self.NumOrg) \
                                           for j in range(self.NumDes) \
                                           for k in range(self.NumProduct))

                self.SP_totalCost.append(totalCost_subProblem)

                # update constraints in RMP
                col = Column()
                for i in range(self.NumOrg):
                    for j in range(self.NumDes):
                        col.addTerms(sum(self.var_x[i][j][k].x for k in range(self.NumProduct)), self.CapacityCons[i][j])

                col.addTerms(1.0, self.convexCons)

                # add decision variable lambda to RMP, i.e., extreme point obtained from subproblems
                self.var_lambda.append(self.RMP.addVar(lb = 0.0
                                                       , ub = GRB.INFINITY
                                                       , obj =0.0
                                                       , vtype = GRB.CONTINUOUS
                                                       , name = 'lam_phase1_' + str(self.Iter)
                                                       , column = col))

                # solve RMP of Phase 1
                self.RMP.optimize()

                # update dual variables
                if self.RMP.objval <= -1e-6:
                    print('---obj of phase 1 reaches 0, phase 1 ends---')
                    break
                else:
                    for i in range(self.NumOrg):
                        for j in range(self.NumDes):
                            self.dual_CapacityCons[i][j] = self.CapacityCons[i][j].pi
                    self.dual_convexCons = self.convexCons.pi

                # reset objective for subproblem in Phase 1
                obj_sub_phase_1 = - quicksum(self.dual_CapacityCons[i][j] * self.var_x[i][j][k] \
                                            for i in range(self.NumOrg) \
                                            for j in range(self.NumDes) \
                                            for k in range(self.NumProduct)) - self.dual_convexCons

                self.subProblem.setObjective(obj_sub_phase_1, GRB.MINIMIZE)

    def updateModelPhase_2(self):
        # update model of Phase 2
        print('----------start update model of Phase 2----------')

        # set objective for RMP of Phase 2
        obj_master_phase_2 = quicksum(self.SP_totalCost[i] * self.var_lambda[i] \
                                        for i in range(len(self.SP_totalCost)))




if __name__ == '__main__':
    MCTP_instance = MCTP()
    MCTP_instance.readData('MCTP_data.txt')
    MCTP_instance.solveMCTP()
    MCTP_instance.reportSolution()