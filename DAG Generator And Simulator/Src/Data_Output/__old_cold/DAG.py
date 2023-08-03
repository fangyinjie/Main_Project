#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Randomized DAG Generator
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################
import math
from random import randint, random, uniform
import random as rand
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import graphviz as gz
from z3 import *
from itertools import combinations
import xlwt
# import xlrd
import xlrd2 as xlrd
import pandas as pd

DAG_Generate_Arithmetic = ['GNM', 'GNP', 'MINE']


#####################################
# todo Section_0: DAG Basic function
#####################################
# #### Gets the nodes in the ready state of the DAG #### #
def get_ready_node_list(temp_DAG_list, run_list, ready_list):
    temp_ready_list = [(ready_node_x[0], ready_node_x[1][0])for ready_node_x in ready_list]
    ret_list = []
    for temp_DAG_x in temp_DAG_list:
        ret_list += [(temp_DAG_x.graph['DAG_ID'], x) for x in temp_DAG_x.nodes(data=True) if
                     (len(list(temp_DAG_x.predecessors(x[0]))) == 0) and
                     ((temp_DAG_x.graph['DAG_ID'], x[0]) not in run_list) and
                     ((temp_DAG_x.graph['DAG_ID'], x[0]) not in temp_ready_list)]
    return ret_list


# # #### get the amount of node in the DAG #### #
def get_node_num(temp_DAG_list):
    node_num = 0
    for temp_DAG_x in temp_DAG_list:
        node_num += temp_DAG_x.number_of_nodes()
    return node_num
#     return self.G.number_of_nodes()


#####################################
#   Section_5: DAG的关键参数分析
#####################################
def dag_param_critical_update(DAG_obj, DAG_id):
    # #### 1.DAG检测及基本参数 #### #
    assert format(nx.is_directed_acyclic_graph(DAG_obj))
    DAG_obj.graph['DAG_ID'] = str(DAG_id)                           # 1.1"DAG_ID",
    DAG_obj.graph['Number_Of_Nodes'] = DAG_obj.number_of_nodes()    # 1.2"Number_Of_Nodes"
    DAG_obj.graph['Number_Of_Edges'] = DAG_obj.number_of_edges()    # 1.3"Number_Of_Edges"
    # #### 2.shape #### #
    # 2.1 正向shape
    rank_list = [sorted(generation) for generation in nx.topological_generations(DAG_obj)]
    rank_num_list = [len(x) for x in rank_list]
    for rank_id, rank_l in enumerate(rank_list):
        for rank_x in rank_l:
            DAG_obj.nodes[rank_x]['rank'] = rank_id
    DAG_obj.graph['Number_Of_Level'] = len(rank_num_list)
    DAG_obj.graph['Shape_List'] = rank_num_list

    DAG_obj.graph['Ave_Shape'] = np.mean(rank_num_list)         # 2.1.1 "Ave_Shape",
    DAG_obj.graph['Std_Shape'] = np.std(rank_num_list)          # 2.1.2 "Std_Shape",
    rank_num_list.pop(len(rank_num_list)-1)
    rank_num_list.pop(0)
    DAG_obj.graph['Max_Shape'] = max(rank_num_list)             # 2.1.3 "Max_Shape",
    DAG_obj.graph['Min_Shape'] = min(rank_num_list)             # 2.1.4 "Min_Shape",
    # 2.2 re-shape
    re_rank_list = [sorted(generation) for generation in nx.topological_generations(nx.DiGraph.reverse(DAG_obj))]
    re_rank_list.reverse()
    re_rank_num_list = [len(x) for x in re_rank_list]

    DAG_obj.graph['Re_Shape_List'] = re_rank_num_list
    DAG_obj.graph['Ave_Re_Shape'] = np.mean(re_rank_num_list)   # 2.2.1 "Ave_re_shape",
    DAG_obj.graph['Std_Re_Shape'] = np.std(re_rank_num_list)    # 2.2.2 "Std_re_shape",
    DAG_obj.graph['Max_Re_Shape'] = max(re_rank_num_list)       # 2.2.3 "Max_re_shape",
    DAG_obj.graph['Min_Re_Shape'] = min(re_rank_num_list)       # 2.2.4 "Min_re_shape",
    # #### 3.antichains #### #
    anti_chains_list = list(nx.antichains(DAG_obj, topo_order=None))    # 3. "Width"
    anti_chains_num_list = [len(x) for x in anti_chains_list]
    DAG_obj.graph['Width'] = max(anti_chains_num_list)
    # DAG_obj.graph['Width'] = 20
    # #### 4.degree #### #
    # 4.1 Degree
    degree_list = [nx.degree(DAG_obj, self_node[0]) for self_node in DAG_obj.nodes(data=True)]
    DAG_obj.graph['Max_Degree'] = max(degree_list)              # 4.1.1 "Max_Degree",
    DAG_obj.graph['Min_Degree'] = min(degree_list)              # 4.1.2 "Min_Degree",
    DAG_obj.graph['Ave_Degree'] = np.mean(degree_list)          # 4.1.3 "Ave_Degree",
    DAG_obj.graph['Std_Degree'] = np.std(degree_list)           # 4.1.4 "Std_Degree",
    # 4.2 In-Degree
    degree_in_list = [DAG_obj.in_degree(self_node[0]) for self_node in DAG_obj.nodes(data=True)]
    DAG_obj.graph['Max_In_Degree'] = max(degree_in_list)        # 4.2.1 "Max_In_Degree",
    DAG_obj.graph['Min_In_Degree'] = min(degree_in_list)        # 4.2.2 "Min_In_Degree",
    DAG_obj.graph['Ave_In_Degree'] = np.mean(degree_in_list)    # 4.2.3 "Ave_In_Degree",
    DAG_obj.graph['Std_In_Degree'] = np.std(degree_in_list)     # 4.2.4 "Std_In_Degree",
    # 4.3 Out-Degree
    degree_out_list = [DAG_obj.out_degree(self_node[0]) for self_node in DAG_obj.nodes(data=True)]
    DAG_obj.graph['Max_Out_Degree'] = max(degree_out_list)      # 4.3.1 "Max_Out_Degree",
    DAG_obj.graph['Min_Out_Degree'] = min(degree_out_list)      # 4.3.2 "Max_Out_Degree",
    DAG_obj.graph['Ave_Out_Degree'] = np.mean(degree_out_list)  # 4.3.3 "Ave_Out_Degree",
    DAG_obj.graph['Std_Out_Degree'] = np.std(degree_out_list)   # 4.3.4 "Std_Out_Degree",
    # #### 5.DAG的稠密度 Density  #### #
    Dag_density = (2 * DAG_obj.number_of_edges()) / (DAG_obj.number_of_nodes() * (DAG_obj.number_of_nodes() - 1))
    DAG_obj.graph['Connection_Rate'] = Dag_density              # 5 "Connection_Rate"
    # #### 6.最大跳层  #### #
    Edges_Jump_List = [DAG_obj.nodes[x[1]]['rank'] - DAG_obj.nodes[x[0]]['rank'] for x in DAG_obj.edges.data()]
    DAG_obj.graph['Jump_Level'] = max(Edges_Jump_List)          # 6 "Connection_Rate"
    # #### 7.WCET  #### #
    WCET_list = [x[1]['WCET'] for x in DAG_obj.nodes.data(data=True) if x[1]['WCET'] > 10]
    DAG_obj.graph['DAG_volume'] = int(np.sum(WCET_list))        # 7.1 "DAG_volume"
    DAG_obj.graph['Max_WCET'] = float(max(WCET_list))           # 7.2 "Max_WCET"
    DAG_obj.graph['Min_WCET'] = float(min(WCET_list))           # 7.3 "Min_WCET"
    DAG_obj.graph['Ave_WCET'] = float(np.mean(WCET_list))       # 7.4 "Ave_WCET"
    DAG_obj.graph['Std_WCET'] = float(np.std(WCET_list))        # 7.5 "Std_WCET"


class DAG_Generator:
    #####################################
    #   DAG parameter
    #####################################
    def __init__(self):
        self.Width = 0  # 最大anti-chain数量；
        # self.Jump_Level = 0           # DAG 中两个节点之间的边的最大长度；
        self.Critical_Path_Length = 3  # 关键路径长度，DAG的长度；(结点个数来给你)
        self.parallelism = 1
        self.DAG_volume = 0

    def Main_Workbench(self, Arithmetic, Param_Dict, DAG_Num=1):
        DAG_list = []
        # todo DAG——生成方法（1）利用DAG_Generator算法来生成；
        if Arithmetic == 'GNM':
            node_num = Param_Dict['Node_Num']
            edge_num = Param_Dict['Edge_Num']
            assert node_num * (node_num - 1) >= edge_num >= node_num - 1
            for x in range(DAG_Num):
                while True:
                    temp_DAG = nx.gnm_random_graph(node_num, edge_num, directed=True)
                    if nx.is_directed_acyclic_graph(temp_DAG):
                        break
                temp_DAG.graph['DAG_ID'] = x
                DAG_list.append(temp_DAG)
            # 循环结束 保存DAG数据；
            sheet_title = Arithmetic
            self.Excel_DAG_Save(DAG_list, sheet_title)

        elif Arithmetic == 'GNP':
            node_num = Param_Dict['Node_Num']
            edge_probability = Param_Dict['Edge_Prob']
            for x in range(DAG_Num):
                while True:
                    temp_DAG = self.gen_gnp(node_num, edge_probability)
                    # temp_DAG = nx.gnp_random_graph(node_num, edge_probability, directed=True)
                    if nx.is_directed_acyclic_graph(temp_DAG):
                        break
                temp_DAG.graph['DAG_ID'] = x
                DAG_list.append(temp_DAG)
            # 循环结束 保存DAG数据；
            sheet_title = Arithmetic
            self.Excel_DAG_Save(DAG_list, sheet_title)

        elif Arithmetic == 'MINE':
            # 这里Node_Num和Critic_Path是算首尾结点的
            assert (Param_Dict['Node_Num'] > 3)
            assert (Param_Dict['Critic_Path'] > 3)
            assert (Param_Dict['Jump_level'] >= 1)
            assert (Param_Dict['Max_in_degree'] >= 1)
            assert (Param_Dict['Max_out_degree'] >= 1)
            assert (Param_Dict['Max_Shape'] >= Param_Dict['Min_Shape'])
            assert (Param_Dict['Min_Shape'] >= 1)
            assert (Param_Dict['Width'] >= Param_Dict['Max_Shape'])
            assert ((Param_Dict['Node_Num'] - 2) <= Param_Dict['Max_Shape'] * (Param_Dict['Critic_Path'] - 2))
            assert ((Param_Dict['Node_Num'] - 2) >= Param_Dict['Min_Shape'] * (Param_Dict['Critic_Path'] - 2))
            # assert (len(sample_list) > 0)
            # for sample_list_x in sample_list:
            #     assert (sum(sample_list_x) == n)
            #     assert (sum(sample_list_x) == n)
            #     assert (len(sample_list_x) == k)
            #     assert (max(sample_list_x) <= width)
            #     assert (max(sample_list_x[1:-1]) <= max_shape)
            #     assert (min(sample_list_x[1:-1]) >= min_shape)

            # todo step(1) 列出所有 shape 的可行解
            return self.gen_mine_new(Param_Dict, DAG_Num=DAG_Num)

            # sheet_title = Arithmetic
            # self.Excel_DAG_Save(DAG_list, sheet_title)
        # for x in range(DAG_Num):
        #     print(np.array(nx.adjacency_matrix(temp_DAG)))
        #     # print(np.array(nx.adjacency_matrix(temp_DAG).todense()))
        #     # print(np.array(nx.adjacency_matrix(temp_DAG)))
        #     # self.DAG_Param_Update(temp_DAG)
        #     ##################################
        #     self.Graphviz_show(temp_DAG)
        #
        #     matrix = np.mat(nx.adjacency_matrix(temp_DAG).todense())
        #     print('fff')
        #     print(matrix.astype(int))
        #     row, columns = matrix.shape
        #     assert (row == columns)
        #     i_test = np.eye(columns).astype(bool)
        #     i_matrix = matrix.astype(bool)
        #     D = (i_matrix | i_test) ** columns    # (M | I)^n
        #     print(D.astype(int))
        #     print(matrix.astype(int))
        #
        #     anti_chains_list = list(nx.antichains(temp_DAG, topo_order=None))
        #     # print("anti-chains:", anti_chains_list)  # 从DAG中生成antichains；
        #     anti_chains_num_list = [len(x) for x in anti_chains_list]

        #     max_antichain_obj = [obj_list for obj_list in anti_chains_list if len(obj_list)==max(anti_chains_num_list)]
        #     print(max_antichain_obj)
        #     # print("max anti-chains (Width):", max(anti_chains_num_list))  # 从DAG中生成antichains；
        #     # temp_dag.graph['Width'] = max(anti_chains_num_list)  # std-shape；
        #     ##################################
        #     DAG_list.append(temp_DAG)
        # todo DAG——生成方法（2）利用excel表格数据生成DAG 每个sheet一个DAG
        elif Arithmetic == 'USER':
            DAG_dict = self.User_DAG_Inject(Param_Dict["Address"])
            return DAG_dict
        else:
            pass
        # else:
        #     DAG_list = self.User_DAG_Inject(Param_List[0])
        # return DAG_list


    def gen_gnp(self, n, p):
        Temp_Matrix = np.zeros((n, n), dtype=bool)
        for x in range(1, n-1):
            for y in range(x+1, n-1):
                if random() < p:
                    Temp_Matrix[x][y] = True
        ret_DAG = nx.from_numpy_matrix(np.array(Temp_Matrix), create_using=nx.DiGraph)
        # self.G = nx.fast_gnp_random_graph(n=n, p=p, seed=None, directed=True)
        while True:
            for x in ret_DAG.nodes(data=True):
                # 无前驱节点的连接到0
                if len(list(ret_DAG.predecessors(x[0]))) == 0:
                    if x[0] != 0:
                        ret_DAG.add_edge(0, x[0])
                # 无前后继点的连接到n-1
                if len(list(ret_DAG.successors(x[0]))) == 0:
                    if x[0] != n-1:
                        ret_DAG.add_edge(x[0], n-1)
            if nx.is_directed_acyclic_graph(ret_DAG):
                # break
                return ret_DAG
            else:
                print("GNP Failed")

    # def gen_gnm(self, n, m):
    #     assert n * (n - 1) >= m >= n - 1
    #     All_edges_list = []
    #     for x in range(n):
    #         for y in range(x + 1, n):
    #             All_edges_list.append((x, y))
    #     Temp_edges_list = rand.sample(All_edges_list, m)
    #     self.G.add_edges_from(Temp_edges_list)
    #     for x in self.G.nodes(data=True):
    #         if (len(list(self.G.predecessors(x[0]))) == 0) and (x[0] != 0):
    #             self.G.add_edge(0, x[0])
    #         if (len(list(self.G.successors(x[0]))) == 0) and (x[0] != n-1):
    #             self.G.add_edge(x[0], n-1)
    #     assert nx.is_directed_acyclic_graph(self.G)

    # #### DAG generator Layer_By_Layer 算法  #### #
    def gen_layer_by_layer(self, n, m):
        pass

    # #### DAG generator Fan_in_Fan_out 算法  #### #
    def gen_fan_in_fan_out(self, n, m):
        pass

    # #### DAG generator Random_Order 算法  #### #
    def gen_random_order(self, n, m):
        pass

    # #### DAG generator mine 算法  #### #
    # n: DAG的节点数量
    # k: DAG的关键路径长度（level）
    # jl: DAG的最大jump
    # max_shape, min_shape:
    # max_in_degree, max_out_degree:
    def gen_mine_new(self, Param_Dict, DAG_Num):
        # 参数定义：
        n = Param_Dict['Node_Num']
        k = Param_Dict['Critic_Path']
        max_shape = Param_Dict['Max_Shape']
        min_shape = Param_Dict['Min_Shape']
        max_out_degree = Param_Dict['Max_out_degree']
        max_in_degree = Param_Dict['Max_in_degree']
        width = Param_Dict['Width']
        jl = Param_Dict['Jump_level']
        connection_ratio = Param_Dict['Connection_ratio']

        node_level_list = [Int(f'node_level_{x}') for x in range(n)]
        ADJ_Matrix = [[Int(f"ADJ_{i}_{j}") for j in range(n)] for i in range(n)]  # Adjacency_Matrix
        # ACC_Matrix      = [[Int(f"ACC_{i}_{j}") for j in range(n)] for i in range(n)]    # Accessibility
        # TEM_Matrix_1    = [[Int(f"TEM_{i}_{j}") for j in range(n)] for i in range(n)]    # Accessibility
        s = Solver()
        # (0) 上三角基本数据约束
        s.add([Or(ADJ_Matrix[i][j] == 1, ADJ_Matrix[i][j] == 0) for i in range(n) for j in range(n) if i < j])
        # (1) 下三角 && 对角线全部为0
        s.add([ADJ_Matrix[i][j] == 0 for i in range(n) for j in range(n) if i >= j])
        # (2) Shape内元素为0
        # (2.1) 确定shape
        for n_x in range(1, n - 1):
            s.add(node_level_list[n_x] < k, node_level_list[n_x] > 1)
            s.add(node_level_list[n_x] >= node_level_list[n_x - 1], node_level_list[n_x] <= node_level_list[n_x + 1])  # 层数顺序递增
        for kx in range(2, k):
            self_level_node_num = Sum([If(nl_x == kx, 1, 0) for nl_x in node_level_list])
            last_level_node_num = Sum([If(nl_x == kx - 1, 1, 0) for nl_x in node_level_list])
            next_level_node_num = Sum([If(nl_x == kx + 1, 1, 0) for nl_x in node_level_list])
            s.add(self_level_node_num <= max_shape)  # 层为kx的节点数量
            s.add(self_level_node_num >= min_shape)  # 层为kx的节点数量
            s.add(self_level_node_num <= width)  # 层中节点的数量一定小于width
            s.add(last_level_node_num * max_out_degree >= self_level_node_num)  # 前一层节点的数量乘以最大出度必须大于等于本层节点数
            s.add(next_level_node_num * max_in_degree >= self_level_node_num)  # 后一层节点的数量乘以最大入度必须大于等于本层节点数
        s.add(node_level_list[0] == 1)  # 首节点在第一层
        s.add(node_level_list[n - 1] == k)  # 尾节点在第k层
        # (2.2) shape内元素为0
        for n_x in range(n):
            s.add([ADJ_Matrix[n_x][n_y] == If(node_level_list[n_x] == node_level_list[n_y], 0, ADJ_Matrix[n_x][n_y]) for
                   n_y in range(n_x + 1, n)])
        # (3) jl, indegree, outdegree
        for n_x in range(1, n):
            s.add(Sum([If(node_level_list[n_x] - node_level_list[n_y] == 1, ADJ_Matrix[n_y][n_x], 0) for n_y in
                       range(n_x)]) >= 1)
            s.add(Sum([If(node_level_list[n_x] - node_level_list[n_y] > jl, ADJ_Matrix[n_y][n_x], 0) for n_y in
                       range(n_x)]) == 0)  # jl 约束向前
        for n_x in range(n - 1):
            s.add(Sum([If(node_level_list[n_y] - node_level_list[n_x] > 0, ADJ_Matrix[n_x][n_y], 0) for n_y in
                       range(n_x + 1, n)]) >= 1)  # jl 约束后前
            s.add(Sum([If(node_level_list[n_y] - node_level_list[n_x] > jl, ADJ_Matrix[n_x][n_y], 0) for n_y in
                       range(n_x + 1, n)]) == 0)  # jl 约束后前
        # (4) 稠密度约束  必须小于 connection_ratio 即 m 小于 connection_ratio * n * （n-1） / 2
        s.add(Sum([ADJ_Matrix[n_x][n_y] for n_x in range(n) for n_y in range(n_x + 1, n)]) <= (
                    connection_ratio * n * (n - 1) / 2))
        # (5) 度约束
        for n_x in range(n):
            sum_out_degree = [ADJ_Matrix[n_x][n_y] for n_y in range(n_x + 1, n)]
            sum_in_degree = [ADJ_Matrix[n_y][n_x] for n_y in range(n_x)]
            s.add(Sum(sum_in_degree) <= max_in_degree)  # (6) 出度约束
            s.add(Sum(sum_out_degree) <= max_in_degree)  # (7) 入度约束
            # s.add(Sum(sum_out_degree + sum_in_degree) <= max_degree)  # (8) 度约束

        # (6) DAG的width 约束：
        # TEM1_Matrix_Array = np.array(TEM_Matrix_1)
        # for i in range(n):
        #     for j in range(n):
        #         if i == j:
        #             s.add(TEM1_Matrix_Array[i][j] == 1)
        #         else:
        #             s.add(TEM1_Matrix_Array[i][j] == ADJ_Matrix[i][j])
        # TEM1_Matrix_Array = np.linalg.matrix_power(TEM1_Matrix_Array, n)
        #
        # for n_x in range(n):
        #     for n_y in range(n):
        #         if n_x >= n_y:
        #             s.add(ACC_Matrix[n_x][n_y] == 0)
        #         else:
        #             s.add(ACC_Matrix[n_x][n_y] == If(TEM1_Matrix_Array[n_x][n_y] > 0, 1, 0))

        Temp_DAG_list = []
        for sDAG_NUM in range(DAG_Num):
            if str(s.check()) == 'sat':
                result = s.model()
                ret_list = [result[node_level_list[x]].as_long() for x in range(n)]
                print(ret_list)
                r = [[result[ADJ_Matrix[i][j]].as_long() for j in range(n)] for i in range(n)]
                print("")
                for rx in r:
                    print(rx)
                # rr = [[result[ACC_Matrix[i][j]].as_long() for j in range(n)] for i in range(n)]
                # print("")
                # for rx in rr:
                #     print(rx)
                Temp_G = nx.DiGraph(np.array(r))
                Temp_G.graph['DAG_ID'] = sDAG_NUM
                # 生成结果检查
                assert format(nx.is_directed_acyclic_graph(Temp_G))
                # assert shape_list == [sorted(generation) for generation in nx.topological_generations(Temp_G)]
                Temp_DAG_list.append(Temp_G)
                s.add(Or([ADJ_Matrix[i][j] != result[ADJ_Matrix[i][j]] for i in range(n) for j in range(n)]))
            else:
                print("fully output!\n")
                return Temp_DAG_list
        return Temp_DAG_list

    # def gen_mine_new(self, n, k, max_shape, min_shape, width, max_in_degree, max_out_degree, jl, connection_ratio, DAG_Num):
    #     # 参数定义：
    #     node_level_list = [Int(f'node_level_{x}') for x in range(n)]
    #     ADJ_Matrix = [[Int(f"ADJ_{i}_{j}") for j in range(n)] for i in range(n)]  # Adjacency_Matrix
    #     # ACC_Matrix      = [[Int(f"ACC_{i}_{j}") for j in range(n)] for i in range(n)]    # Accessibility
    #     # TEM_Matrix_1    = [[Int(f"TEM_{i}_{j}") for j in range(n)] for i in range(n)]    # Accessibility
    #     s = Solver()
    #     # (0) 上三角基本数据约束
    #     s.add([Or(ADJ_Matrix[i][j] == 1, ADJ_Matrix[i][j] == 0) for i in range(n) for j in range(n) if i < j])
    #     # (1) 下三角 && 对角线全部为0
    #     s.add([ADJ_Matrix[i][j] == 0 for i in range(n) for j in range(n) if i >= j])
    #     # (2) Shape内元素为0
    #     # (2.1) 确定shape
    #     for n_x in range(1, n - 1):
    #         s.add(node_level_list[n_x] < k, node_level_list[n_x] > 1)
    #         s.add(node_level_list[n_x] >= node_level_list[n_x - 1], node_level_list[n_x] <= node_level_list[n_x + 1])  # 层数顺序递增
    #     for kx in range(2, k):
    #         self_level_node_num = Sum([If(nl_x == kx, 1, 0) for nl_x in node_level_list])
    #         last_level_node_num = Sum([If(nl_x == kx - 1, 1, 0) for nl_x in node_level_list])
    #         next_level_node_num = Sum([If(nl_x == kx + 1, 1, 0) for nl_x in node_level_list])
    #         s.add(self_level_node_num <= max_shape)  # 层为kx的节点数量
    #         s.add(self_level_node_num >= min_shape)  # 层为kx的节点数量
    #         s.add(self_level_node_num <= width)  # 层中节点的数量一定小于width
    #         s.add(last_level_node_num * max_out_degree >= self_level_node_num)  # 前一层节点的数量乘以最大出度必须大于等于本层节点数
    #         s.add(next_level_node_num * max_in_degree >= self_level_node_num)  # 后一层节点的数量乘以最大入度必须大于等于本层节点数
    #     s.add(node_level_list[0] == 1)  # 首节点在第一层
    #     s.add(node_level_list[n - 1] == k)  # 尾节点在第k层
    #     # (2.2) shape内元素为0
    #     for n_x in range(n):
    #         s.add([ADJ_Matrix[n_x][n_y] == If(node_level_list[n_x] == node_level_list[n_y], 0, ADJ_Matrix[n_x][n_y]) for
    #                n_y in range(n_x + 1, n)])
    #     # (3) jl, indegree, outdegree
    #     for n_x in range(1, n):
    #         s.add(Sum([If(node_level_list[n_x] - node_level_list[n_y] == 1, ADJ_Matrix[n_y][n_x], 0) for n_y in
    #                    range(n_x)]) >= 1)
    #         s.add(Sum([If(node_level_list[n_x] - node_level_list[n_y] > jl, ADJ_Matrix[n_y][n_x], 0) for n_y in
    #                    range(n_x)]) == 0)  # jl 约束向前
    #     for n_x in range(n - 1):
    #         s.add(Sum([If(node_level_list[n_y] - node_level_list[n_x] > 0, ADJ_Matrix[n_x][n_y], 0) for n_y in
    #                    range(n_x + 1, n)]) >= 1)  # jl 约束后前
    #         s.add(Sum([If(node_level_list[n_y] - node_level_list[n_x] > jl, ADJ_Matrix[n_x][n_y], 0) for n_y in
    #                    range(n_x + 1, n)]) == 0)  # jl 约束后前
    #     # (4) 稠密度约束  必须小于 connection_ratio 即 m 小于 connection_ratio * n * （n-1） / 2
    #     s.add(Sum([ADJ_Matrix[n_x][n_y] for n_x in range(n) for n_y in range(n_x + 1, n)]) <= (
    #                 connection_ratio * n * (n - 1) / 2))
    #     # (5) 度约束
    #     for n_x in range(n):
    #         sum_out_degree = [ADJ_Matrix[n_x][n_y] for n_y in range(n_x + 1, n)]
    #         sum_in_degree = [ADJ_Matrix[n_y][n_x] for n_y in range(n_x)]
    #         s.add(Sum(sum_in_degree) <= max_in_degree)  # (6) 出度约束
    #         s.add(Sum(sum_out_degree) <= max_in_degree)  # (7) 入度约束
    #         # s.add(Sum(sum_out_degree + sum_in_degree) <= max_degree)  # (8) 度约束
    #
    #     # (6) DAG的width 约束：
    #     # TEM1_Matrix_Array = np.array(TEM_Matrix_1)
    #     # for i in range(n):
    #     #     for j in range(n):
    #     #         if i == j:
    #     #             s.add(TEM1_Matrix_Array[i][j] == 1)
    #     #         else:
    #     #             s.add(TEM1_Matrix_Array[i][j] == ADJ_Matrix[i][j])
    #     # TEM1_Matrix_Array = np.linalg.matrix_power(TEM1_Matrix_Array, n)
    #     #
    #     # for n_x in range(n):
    #     #     for n_y in range(n):
    #     #         if n_x >= n_y:
    #     #             s.add(ACC_Matrix[n_x][n_y] == 0)
    #     #         else:
    #     #             s.add(ACC_Matrix[n_x][n_y] == If(TEM1_Matrix_Array[n_x][n_y] > 0, 1, 0))
    #
    #     Temp_DAG_list = []
    #     for sDAG_NUM in range(DAG_Num):
    #         if str(s.check()) == 'sat':
    #             result = s.model()
    #             ret_list = [result[node_level_list[x]].as_long() for x in range(n)]
    #             print(ret_list)
    #             r = [[result[ADJ_Matrix[i][j]].as_long() for j in range(n)] for i in range(n)]
    #             print("")
    #             for rx in r:
    #                 print(rx)
    #             # rr = [[result[ACC_Matrix[i][j]].as_long() for j in range(n)] for i in range(n)]
    #             # print("")
    #             # for rx in rr:
    #             #     print(rx)
    #             Temp_G = nx.DiGraph(np.array(r))
    #             Temp_G.graph['DAG_ID'] = sDAG_NUM
    #             # 生成结果检查
    #             assert format(nx.is_directed_acyclic_graph(Temp_G))
    #             # assert shape_list == [sorted(generation) for generation in nx.topological_generations(Temp_G)]
    #             Temp_DAG_list.append(Temp_G)
    #             s.add(Or([ADJ_Matrix[i][j] != result[ADJ_Matrix[i][j]] for i in range(n) for j in range(n)]))
    #         else:
    #             print("fully output!\n")
    #             return Temp_DAG_list
    #     return Temp_DAG_list

    def gen_mine(self, sample_list, n, k, jl, max_shape, min_shape, max_in_degree, max_out_degree, connection_ratio, width, DAG_Num):
        assert (len(sample_list) > 0)
        for sample_list_x in sample_list:
            assert (sum(sample_list_x) == n)
            assert (sum(sample_list_x) == n)
            assert (len(sample_list_x) == k)
            assert (max(sample_list_x) <= width)
            assert (max(sample_list_x[1:-1]) <= max_shape)
            assert (min(sample_list_x[1:-1]) >= min_shape)

        sDAG_Num = DAG_Num
        Temp_DAG_list = []
        for shape_l in sample_list:
            shape_list = [ ]
            node_index = 0
            for rank, node_num in enumerate(shape_l):
                shape_list.append([])
                for x in range(node_num):
                    shape_list[rank].append(node_index)
                    node_index += 1
            # print(shape_list)
            # n x n 整数变量矩阵
            temp_matrix   = [[Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
            temp_r_matrix = [[Int(f"xr_{i}_{j}") for j in range(n)] for i in range(n)]

            s = Solver()
            s.add( [Or(temp_matrix[i][j] == 1,  temp_matrix[i][j] == 0) for i in range(n) for j in range(n) if i <= j] )    # (0) 上三角基本数据约束
            s.add( [temp_matrix[i][j] == 0 for i in range(n) for j in range(n) if i >= j] )                                 # (1) 下三角与对角线全部为0
            s.add( [temp_matrix[i][j] == 0 for sl in shape_list for i in sl for j in sl] )                                  # (2) Shape内元素为0
            for rank, node_num_list in enumerate(shape_list):                                                               # (3) jl约束——其中与上一层间至少有一个直连
                for node_num in node_num_list:                                              # 遍历每个结点
                    p1 = [temp_matrix[p_n][node_num] for p_n_list in shape_list[max(0, rank - 1):rank] for p_n in p_n_list]
                    p2 = [temp_matrix[p_n][node_num] for p_n_list in shape_list[max(0, rank - jl):rank] for p_n in p_n_list]
                    if len(p1) > 0:
                        s.add(Sum(p1) >= 1)
                        s.add(Sum(p2) <= max_in_degree)
                    p3 = [temp_matrix[node_num][p_n] for p_n_list in shape_list[rank + 1: min(n - 1, rank + 1 + jl)] for p_n in p_n_list]
                    if len(p3) > 0:
                        s.add(Sum(p3) <= max_out_degree)
                        s.add(Sum(p3) >= 1)
            # (4) 稠密度约束  必须小于 connection_ratio  即 m 小于 connection_ratio * n * （n-1） / 2
            s.add( Sum( [temp_matrix[i][j] for j in range(n) for i in range(n)]) <= (connection_ratio * n * (n-1) / 2) )
            # (5) DAG的width 约束：
            for i in range(n):
                for j in range(n):
                    k_list = [If(And(temp_matrix[i][k] == 1, temp_matrix[k][j] == 1), 1, 0) for k in range(n)]
                    s.add(temp_r_matrix[i][j] == If( Or( Sum(k_list) > 0, temp_matrix[i][j] == 1), 1, 0 ))    # 可达矩阵：
            # (5.1) width下限约束
            node_list_temp = [x for x in range(1, n)]
            node_clist1 = [temp_ll for temp_ll in combinations(node_list_temp, width)]
            cpp1 = [[temp_r_matrix[t_l[i]][t_l[j]] for i in range(len(t_l)) for j in range(i + 1, len(t_l))] for t_l in node_clist1]
            s.add( Or( [If(Sum(x) == 0, True, False) for x in cpp1] ) == True)
            # (5.2) width上限约束 即 width + 1
            node_clist2 = [temp_ll for temp_ll in combinations(node_list_temp, width + 1)]
            cpp2 = [[temp_r_matrix[t_l[i]][t_l[j]] for i in range(len(t_l)) for j in range(i + 1, len(t_l))] for t_l in node_clist2]
            s.add( And( [If(Sum(x) == 0, False, True) for x in cpp2] ) == True)

            for i in range(n):
                # (6) 出度约束
                s.add( Sum([temp_matrix[i_c][i] for i_c in range(i)]) <= max_in_degree )
                # (7) 入度约束
                s.add( Sum([temp_matrix[i][i_r] for i_r in range(i + 1, n)]) <= max_in_degree )

            while str(s.check()) == 'sat':
                m = s.model()
                r = [[m[temp_matrix[i][j]].as_long() for j in range(n)] for i in range(n)]
                # for rx in r:
                    # print(rx)
                # print('')
                rr = [[m[temp_r_matrix[i][j]].as_long() for j in range(n)] for i in range(n)]
                # for rx in rr:
                #     print(rx)

                Temp_G = nx.DiGraph(np.array(r))
                Temp_G.graph['DAG_ID'] = DAG_Num - sDAG_Num
                assert format(nx.is_directed_acyclic_graph(Temp_G))
                assert shape_list == [sorted(generation) for generation in nx.topological_generations(Temp_G)]
                # 更新DAG数据
                sDAG_Num -= 1
                if sDAG_Num <= 0:
                    return Temp_DAG_list
                self.DAG_Param_Update(Temp_G)
                Temp_DAG_list.append(Temp_G)
                # 添加新的约束
                s.add( Or([temp_matrix[i][j] != m[temp_matrix[i][j]]for i in range(n) for j in range(n) ]) )
        return Temp_DAG_list

        # # ## transitive reduction 传递约简； ## #
        # # lp = list(nx.DiGraph(self.transitive_reduction_matrix()).edges())     # 1.networkx包
        # lp = list(nx.transitive_reduction(self.G).edges())                        # 2.networkx包
        # self.G.clear_edges()
        # self.G.add_edges_from(lp)

    def node_distribution(self, n, k, max_shape, min_shape, max_in_degree, max_out_degree, width):
        ret_list = []
        assert ((n - 2) <= max_shape * (k - 2))
        assert ((n - 2) >= min_shape * (k - 2))

        x_list = [Int(f'x_{k_x}') for k_x in range(1, k + 1)]

        s = Solver()
        s.add(Sum(x_list) == n)
        s.add(x_list[0] == 1)
        s.add(x_list[-1] == 1)

        for x in range(1, len(x_list) - 1):
            s.add(x_list[x] >= min_shape, x_list[x] <= max_shape)
            s.add(x_list[x] <= width)
            s.add(x_list[x - 1] * max_out_degree >= x_list[x])
            s.add(x_list[x + 1] * max_in_degree >= x_list[x])

        # if str(s.check()) == 'sat':
        while str(s.check()) == 'sat':
            result = s.model()
            ret_list.append([result[xl_x].as_long() for xl_x in x_list])
            s.add(Or([x_list[x] != result[x_list[x]] for x in range(1, len(x_list) - 1)]))
        return ret_list

    # ############################################################
    # Arithmetic = 'GNM'    ——》     Param_List = [N, M]
    # Arithmetic = 'GNP'    ——》     Param_List = [N, P]
    # ############################################################
    # todo DAG——生成方法（1）利用DAG_Generator算法来生成；
    def Generator(self, Arithmetic, Param_List):
        if Arithmetic == 'GNM':
            node_num = Param_List[0]
            edge_num = Param_List[1]
            assert node_num * (node_num - 1) >= edge_num >= node_num - 1
            while True:
                temp_DAG = nx.gnm_random_graph(node_num, edge_num, directed=True)
                if nx.is_directed_acyclic_graph(temp_DAG):
                    return temp_DAG
        elif Arithmetic == 'GNP':
            node_num = Param_List[0]
            edge_probability = Param_List[1]
            while True:
                temp_DAG = nx.gnp_random_graph(node_num, edge_probability, directed=True)
                if nx.is_directed_acyclic_graph(temp_DAG):
                    return temp_DAG
        else:
            print("Generator param error!!!\n")
            return False

    # todo DAG——生成方法（2）利用excel表格数据生成DAG 每个sheet一个DAG
    def User_DAG_Inject(self, address):
        """
        df = pd.ExcelFile('./data/result模块.xls')
        c = df.sheet_names  # 查看所有sheet 名字
        cc = df.parse(c[1])  # 为读取AAA工作薄中的内容
        df_concat = pd.concat([pd.read_excel(df, sheet) for sheet in df.sheet_names])  # 将所有sheet中数据合并到一个df中
        # import pandas as pd
        writer = pd.ExcelWriter('test_excel.xlsx')
        df.to_excel(writer, sheet_name='AAA')
        df.to_excel(writer, sheet_name='BBB')
        """
        with pd.ExcelFile(address) as data:
            all_sheet_names = data.sheet_names
            DAG_list = []
            for DAG_ID in all_sheet_names:
                temp_DAG = nx.DiGraph()
                temp_DAG.graph['DAG_ID'] = DAG_ID
                df = pd.read_excel(data, DAG_ID, index_col=None, na_values=["NA"])
                title_list = df.dtypes
                # xxxx = df.columns
                for row in df.index:
                    temp_DAG.add_node(df.loc[row]['Node_Index'], DAG_ID=DAG_ID)
                    for title_id, data_type in title_list.items():
                        row_data = df.loc[row][title_id]
                        if title_id == 'Edges_List':
                            if type(row_data) == float:
                                continue
                            row_data = row_data.split(';')
                            for edge_data in row_data:
                                edge_list = edge_data[1:-1].split(',')
                                temp_DAG.add_edge(int(edge_list[0]), int(edge_list[1]))
                        else:
                            temp_DAG.nodes[df.loc[row]['Node_Index']][title_id] = row_data

                DAG_list.append(temp_DAG)
        return DAG_list
        # num_row = temp_table.nrows                  # 获取行数量
        # num_col = temp_table.ncols                  # 获取列数量
        # param_title_list = temp_table.row(0)
        # for node_id in range(1, num_row):
        #     node_param_list = temp_table.row(node_id)
        #     temp_DAG.add_node(node_id)
        #     for param_id in range(len(param_title_list)):
        #         temp_DAG.node[node_id][param_title_list[param_id].value] = node_param_list[param_id].value
        #         print()
        # temp_DAG.get_node(node_id)

        # G.add_node(1, name='n1', weight=1)
        # G.add_node(2, name='n2', weight=3)
        # G.add_node(3, name='n3', weight=3)
        # G.add_node(4, name='n4', weight=6)
        # G.add_node(5, name='n5', weight=7)
        # G.add_node(6, name='n6', weight=8)
        #
        # G.add_edge(1, 2)
        # G.add_edges_from([
        #     (1, 2, {'weight': 8}),
        #     (1, 3, {'weight': 8}),
        #     (1, 4, {'weight': 8}),
        #     (1, 5, {'weight': 8}),
        #     (2, 6, {'weight': 8}),
        #     (3, 6, {'weight': 8}),
        #     (4, 6, {'weight': 8}),
        #     (5, 6, {'weight': 8}),
        # ])
        # print(x)

    #####################################
    #   Section_5: DAG的关键参数更新
    #   输入：无属性参数的DAG
    #   输出：赋予属性参数DAG
    #####################################


    def DAG_Param_Update(self, temp_dag):
        # #### 0.DAG检测及基本参数 #### #
        # assert format(nx.is_directed_acyclic_graph(temp_dag))     # 检测是否是有向无环图
        # print("DAG_ID:", self.DAG_ID)                             # 1.打印DAG的ID
        temp_dag.graph['Edges_List'] = temp_dag.edges(data=False)
        temp_dag.graph['Nodes_Number'] = temp_dag.number_of_nodes()
        temp_dag.graph['Edges_Number'] = temp_dag.number_of_edges()

        print("Number of Nodes:", temp_dag.number_of_nodes())
        print("Number of Edges:", temp_dag.number_of_edges())
        # #### 1.关键路径 #### #
        # node_list = nx.dag_longest_path(self.G, weight='weight')  # 关键路径
        # print('关键路径：{0}'.format(node_list))
        # #### 2.最短路径 #### #
        # shortest_path = list(nx.all_shortest_paths(self.G, 0, self.G.number_of_nodes() - 1, weight='weight'))
        # print('DAG的最短路径{0}条：'.format(len(shortest_path)))
        # [print(path) for path in shortest_path]

        # #### 3.获取拓扑分层 shape #### #
        # 3.1 正向shape
        rank_list = [sorted(generation) for generation in nx.topological_generations(temp_dag)]
        rank_num_list = [len(x) for x in rank_list]
        print('拓扑分层：{0}'.format(rank_list))
        print('拓扑分层节点数量分布：{0}'.format(rank_num_list))
        print("Max_Shape:{0}".format(max(rank_num_list)))
        print("Min_Shape:{0}".format(min(rank_num_list)))
        print("Ave_Shape:{0:0.2f}".format(np.mean(rank_num_list)))
        print("Std_Shape:{0:0.2f}".format(np.std(rank_num_list)))

        temp_dag.graph['Max_Shape'] = max(rank_num_list)  # max-shape；
        temp_dag.graph['Min_Shape'] = min(rank_num_list)  # min-shape；
        temp_dag.graph['Ave_Shape'] = np.mean(rank_num_list)  # ave-shape；
        temp_dag.graph['Std_Shape'] = np.std(rank_num_list)  # std-shape；

        # 3.2 反向shape
        re_rank_list = [sorted(generation) for generation in nx.topological_generations(nx.DiGraph.reverse(temp_dag))]
        re_rank_list.reverse()
        re_rank_num_list = [len(x) for x in re_rank_list]
        print('反向拓扑分层：{0}'.format(re_rank_list))
        print('反向拓扑分层节点数量分布：{0}'.format(re_rank_num_list))
        print("Max_re_shape:{0}".format(max(re_rank_num_list)))
        print("Min_re_shape:{0}".format(min(re_rank_num_list)))
        print("Ave_re_shape:{0:0.2f}".format(np.mean(re_rank_num_list)))
        print("Std_re_shape:{0:0.2f}".format(np.std(re_rank_num_list)))

        temp_dag.graph['Max_Re_Shape'] = max(rank_num_list)  # max-shape；
        temp_dag.graph['Min_Re_Shape'] = min(rank_num_list)  # min-shape；
        temp_dag.graph['Ave_Re_Shape'] = np.mean(rank_num_list)  # ave-shape；
        temp_dag.graph['Std_Re_Shape'] = np.std(rank_num_list)  # std-shape；

        # #### 5.antichains #### #
        # anti_chains_list = list(nx.antichains(temp_dag, topo_order=None))
        # print("anti-chains:", anti_chains_list)  # 从DAG中生成antichains；
        # anti_chains_num_list = [len(x) for x in anti_chains_list]
        # print("max anti-chains (Width):", max(anti_chains_num_list))  # 从DAG中生成antichains；
        print("max anti-chains (Width):", 40)  # 从DAG中生成antichains；
        # #### 6.degree #### #
        degree_list = [nx.degree(temp_dag, self_node[0]) for self_node in temp_dag.nodes(data=True)]
        print("Max_Degree:{0}".format(max(degree_list)))
        print("Min_Degree:{0}".format(min(degree_list)))
        print("Ave_Degree:{0:0.2f}".format(np.mean(degree_list)))
        print("Std_Degree:{0:0.2f}".format(np.std(degree_list)))

        temp_dag.graph['Max_Degree'] = max(degree_list)  # max-degree；
        temp_dag.graph['Min_Degree'] = min(degree_list)  # max-degree；
        temp_dag.graph['Ave_Degree'] = np.mean(degree_list)  # ave-degree；
        temp_dag.graph['Std_Degree'] = np.std(degree_list)  # std-degree；

        degree_in_list = [temp_dag.in_degree(self_node[0]) for self_node in temp_dag.nodes(data=True)]
        print("Max_In_Degree:{0}".format(max(degree_in_list)))
        print("Min_In_Degree:{0} —— 均为0".format(min(degree_in_list)))
        print("Ave_In_Degree:{0:0.2f}".format(np.mean(degree_in_list)))
        print("Std_In_Degree:{0:0.2f}".format(np.std(degree_in_list)))
        temp_dag.graph['Max_In_Degree'] = max(degree_in_list)  # max-degree；
        temp_dag.graph['Min_In_Degree'] = min(degree_in_list)  # max-degree；
        temp_dag.graph['Ave_In_Degree'] = np.mean(degree_in_list)  # ave-degree；
        temp_dag.graph['Std_In_Degree'] = np.std(degree_in_list)  # std-degree；

        degree_out_list = [temp_dag.out_degree(self_node[0]) for self_node in temp_dag.nodes(data=True)]
        print("Max_Out_Degree:{0}".format(max(degree_out_list)))
        print("Max_Out_Degree:{0} —— 均为0".format(min(degree_out_list)))
        print("Ave_Out_Degree:{0:0.2f}".format(np.mean(degree_out_list)))
        print("Std_Out_Degree:{0:0.2f}".format(np.std(degree_out_list)))
        temp_dag.graph['Max_Out_Degree'] = max(degree_out_list)  # max-degree；
        temp_dag.graph['Max_Out_Degree'] = min(degree_out_list)  # max-degree；
        temp_dag.graph['Ave_Out_Degree'] = np.mean(degree_out_list)  # ave-degree；
        temp_dag.graph['Std_Out_Degree'] = np.std(degree_out_list)  # std-degree；

        # #### 7.DAG的稠密度 Density  #### #
        Connectivity_Rate = (2 * temp_dag.number_of_edges()) / (temp_dag.number_of_nodes() * (temp_dag.number_of_nodes() - 1))
        temp_dag.graph['Connectivity_Rate'] = Connectivity_Rate  # max-degree；
        print("Dag_density：{0:2f}".format(Connectivity_Rate))

        # # Edges_Jump_List = [(self.G.nodes[x[0]], self.G.nodes[x[1]]) for x in self.G.edges.data(data=True)]
        # Edges_Jump_List = [temp_dag.nodes[x[1]]['rank'] - temp_dag.nodes[x[0]]['rank'] for x in temp_dag.edges.data(data=True)]
        # self.Jump_Level = max(Edges_Jump_List)
        # print("Jump_Level：{0}".format( self.Jump_Level ))

        # #### 0.Other_Test  #### #
        # degree_in_list = len[temp_dag.in_degree(self_node[0]) for self_node in temp_dag.nodes(data=True)]
        nout_degree_num = len([node_x for node_x in temp_dag.nodes() if len(list(temp_dag.successors(node_x))) < 1])
        nin_degree_num = len([node_x for node_x in temp_dag.nodes() if len(list(temp_dag.predecessors(node_x))) < 1])
        temp_dag.graph['Nin_degree_num'] = nin_degree_num       # 入度
        temp_dag.graph['Nout_degree_num'] = nout_degree_num     # 出度

        # #### get the volume of DAG (workload)#### #
        # def get_dag_volume():
        #     volume = 0
        #     for node_x in self.G.nodes(data=True):
        #         volume += node_x[1]['WCET']
        #     return volume

    """
    def Excel_DAG_Save(self, DAG_list, sheet_title):
        workbook = xlwt.Workbook(encoding='utf-8')

        # for DAG_x in DAG_list:
        #     worksheet = workbook.add_sheet(DAG_x)  # 新建一个sheet
        #     graph[excel_title[excel_title_id]]

        worksheet = workbook.add_sheet( sheet_title )  # 新建一个sheet
        # ### （1）excel 标题 ### #
        excel_title = ["DAG_ID",           "Edges_List",
                       "Nodes_Number",     "Edges_Number",     "Connectivity_Rate",
                       "Max_Shape",        "Min_Shape",        "Ave_Shape",        "Std_Shape",
                       "Max_Re_Shape",     "Min_Re_Shape",     "Ave_Re_Shape",     "Std_Re_Shape",
                       "Max_Degree",       "Min_Degree",       "Ave_Degree",       "Std_Degree",
                       "Max_In_Degree",    "Min_In_Degree",    "Ave_In_Degree",    "Std_In_Degree",
                       "Max_Out_Degree",   "Max_Out_Degree",   "Ave_Out_Degree",   "Std_Out_Degree"
                       # ,"Max_Anti-Chains (Width)", "DAG_volume"
                       ]
        for temp_title_id in range(len(excel_title)):
            worksheet.write(0, temp_title_id, excel_title[temp_title_id])
        # ### （2）excel 内容 ### #
        for temp_DAG_id in range(len(DAG_list)):
            for excel_title_id in range(len(excel_title)):
                temp_data = DAG_list[temp_DAG_id].graph[excel_title[excel_title_id]]
                # print( type(temp_data) )
                if isinstance(temp_data, float):
                    temp_data = round(temp_data, 2)
                worksheet.write(temp_DAG_id+1, excel_title_id, str( temp_data ))  # 内容添加
        # ### （3）excel 保存 ### #
        workbook.save(str("result模块.xls"))
        return True
    """

    def Graphviz_show(self, temp_dag):
        dot = gz.Digraph()
        [dot.node('%s' % t_node[0], '{0}\n{1}'.format(t_node[0], t_node[1]['Node_ID']))
         for t_node in temp_dag.nodes(data=True)]
        [dot.edge('%s' % t_edge[0], '%s' % t_edge[1]) for t_edge in temp_dag.edges()]
        dot.view('./graph/' + temp_dag.graph['DAG_ID'])

    """
    # #### get the median of DAG (中位数)#### #
    def get_dag_median(self):
        node_c = self.get_node_num()
        wcet_list = []
        for node_x in self.G.nodes(data=True):
            wcet_list.append(node_x[1]['WCET'])
        l = sorted(wcet_list)  # sorted(a)对列表进行排序，结果返回一个列表
        index = (int) (node_c / 2)  # 获取中间值索引（分两种情况）
        if len(l) % 2 == 0:     # 偶数
            return (l[index] + l[index - 1]) / 2
        else:                   # 基数
            return l[index]

    # #### 设置DAG的shape level或rank #### #
    def set_DAG_shape_level(self):
        # #### 3.获取拓扑分层 shape #### #
        rank_list = [sorted(generation) for generation in nx.topological_generations(self.G)]
        rank_num_list = [len(x) for x in rank_list]
        for x in range(len(rank_list)):
            for y in rank_list[x]:
                node_temp = self.G.nodes[y]
                node_temp['rank'] = x

    # #### Transitive reduction Function #### #
    #   param:  matrix: Adjacency Matrix
    #   return: A matrix that has been reduced in transitive
    def transitive_reduction_matrix(self):
        matrix = np.array(nx.adjacency_matrix(self.G).todense())
        row, columns = matrix.shape
        assert (row == self.task_num)
        assert (columns == self.task_num)
        print("matrix shape is ({0},{1})".format(row, columns))
        i_test = np.eye(self.task_num).astype(bool)
        i_matrix = matrix.astype(bool)
        D = np.power((i_matrix | i_test), self.task_num)  # (M | I)^n
        D = D.astype(bool) & (~i_test)
        TR = matrix & (~(np.dot(i_matrix, D)))  # Tr = T ∩ （-（T . D））
        return nx.DiGraph(TR)

    # #### critical path configuration #### #
    def critical_path_config(self):
        WCET = nx.get_node_attributes(self.G, 'WCET')
        for edge_x in self.G.edges(data=True):
            edge_x[2]['weight'] = WCET[edge_x[1]]
        node_list = nx.dag_longest_path(self.G, weight='weight')  # 关键路径
        for node_xx in self.G.nodes(data=True):
            if node_xx[0] in node_list:  # 判断是否在关键路径里
                node_xx[1]['critic'] = True
        # print('关键路径：{0}'.format(node_list))

    #####################################
    #   Section_1: DAG 随机生成函数
    #####################################
    def DAG_Generator(self, DAG_Generator_algorithm):
        if DAG_Generator_algorithm == "mine":
            self.gen_mine()
        elif DAG_Generator_algorithm == "GNM":
            self.gen_gnm(n=self.n, m=self.m)
        elif DAG_Generator_algorithm == "GNP":
            self.gen_gnp(n=self.n, p=self.p)       # 将所有前驱为0的和source连接，后继为0的和sink连接
        elif DAG_Generator_algorithm == "Layer_By_Layer":
            pass
        elif DAG_Generator_algorithm == "Fan_in_Fan_out":
            pass
        elif DAG_Generator_algorithm == "Random_Order":
            pass
        else:
            return False
        return 0

    # #### DAG generator mine 算法  #### #
    def gen_mine(self):
        assert (self.parallelism >= 1)
        assert (self.Critical_Path_Length >= 3)
        # 步骤一：initial a new graph G               # e.g. G = nx.DiGraph(Index=self.task_num)
        #   添加节点；确定rank的节点
        self_critical_path  = self.Critical_Path_Length    # 关键路径长度
        self_parallelism    = self.parallelism      # 图的并行度
        self_Node_num       = 0                     # DAG的节点数量
        self.G.add_node(0, Node_ID='souce', rank=0, critic=False, WCET=1, priority=1, state='blocked')  # 起始节点（1）；rank=0

        for x in range(1, self_critical_path - 1):
            m = randint(1, self_parallelism)        # 随机每层的节点数量（不能大于并行度）
            for y in range(1, m + 1):
                self_Node_num += 1
                self.G.add_node(self_Node_num, Node_ID='job{}'.format(self_Node_num), rank=x, critic=False, WCET=1, priority=1, state='blocked')
        self.G.add_node(self_Node_num + 1, Node_ID='sink', rank=self_critical_path - 1, critic=False, WCET=1, priority=1, state='blocked')
        self.task_num = self_Node_num + 2  # +2算上source和sink
        self.G.add_edge(0, 1)
        for x in range(1, self_critical_path - 1):  # 从第2层开始到倒数第二层
            ancestors_list      = [node_x for node_x in self.G.nodes(data=True) if (node_x[1].get('rank') < x)]
            descendants_list    = [node_x for node_x in self.G.nodes(data=True) if (node_x[1].get('rank') > x)]
            self_list           = [node_x for node_x in self.G.nodes(data=True) if (node_x[1].get('rank') == x)]
            successors_list     = [node_x for node_x in self.G.nodes(data=True) if (node_x[1].get('rank') == (x + 1))]
            for y in self_list:
                k1 = randint(1, len(ancestors_list))                    # 在祖先节点中随机几个节点作为前驱
                ancestors_group = rand.sample(ancestors_list, k1)
                k2 = randint(1, len(descendants_list))                  # 在后代节点中随机几个节点作为后继
                descendants_group = rand.sample(descendants_list, k2)
                for z in ancestors_group:
                    self.G.add_edge(z[0], y[0])
                for z in descendants_group:
                    self.G.add_edge(y[0], z[0])
            self.G.add_edge(self_list[0][0], successors_list[0][0])
        self.name = 'Tau_{:d}'.format(self.task_num)
        # self.G = nx.DiGraph(self.Matrix)                  # 邻接矩阵生成一个有向图netWorkX；属性全无；

        # # ## transitive reduction 传递约简； ## #
        # # lp = list(nx.DiGraph(self.transitive_reduction_matrix()).edges())     # 1.networkx包
        # lp = list(nx.transitive_reduction(self.G).edges())                  # 2.networkx包
        # self.G.clear_edges()
        # self.G.add_edges_from(lp)
        # # print(np.array(nx.adjacency_matrix(self.G).todense()))


    # #### DAG generator GNP 算法  #### #
    def gen_gnp(self, n, p):
        Temp_Matrix = np.zeros((n, n), dtype=bool)
        for x in range(1, n-1):
            for y in range(x+1, n-1):
                if random() < p:
                    Temp_Matrix[x][y] = True
        self.G = nx.from_numpy_matrix(np.array(Temp_Matrix), create_using=nx.DiGraph)
        while True:
            # self.G = nx.fast_gnp_random_graph(n=n, p=p, seed=None, directed=True)
            for x in self.G.nodes(data=True):
                x[1]['Node_ID']     = 'Job_{0}'.format(x[0])
                x[1]['rank']        = 0
                x[1]['critic']      = False
                x[1]['WCET']        = 1
                x[1]['priority']    = 1
                x[1]['state']       = 'blocked'
                # 无前驱节点的连接到0
                if len(list(self.G.predecessors(x[0]))) == 0:
                    if x[0] != 0:
                        self.G.add_edge(0, x[0])
                # 无前后继点的连接到n-1
                if len(list(self.G.successors(x[0]))) == 0:
                    if x[0] != n-1:
                        self.G.add_edge(x[0], n-1)
            if nx.is_directed_acyclic_graph(self.G):
                break
            else:
                print("GNP Failed")

    # #### DAG generator GNM 算法  #### #
    def gen_gnm(self, n, m):
        assert n * (n - 1) >= m >= n - 1
        All_edges_list = []
        for x in range(n):
            for y in range(x + 1, n):
                All_edges_list.append((x, y))
        Temp_edges_list = rand.sample(All_edges_list, m)
        self.G.add_edges_from(Temp_edges_list)
        for x in self.G.nodes(data=True):
            x[1]['Node_ID']     = 'Job_{0}'.format(x[0])
            x[1]['rank']        = 0
            x[1]['critic']      = False
            x[1]['WCET']        = 1
            x[1]['priority']    = 1
            x[1]['state']       = 'blocked'
            if (len(list(self.G.predecessors(x[0]))) == 0) and (x[0] != 0):
                self.G.add_edge(0, x[0])
            if (len(list(self.G.successors(x[0]))) == 0) and (x[0] != n-1):
                self.G.add_edge(x[0], n-1)
        assert nx.is_directed_acyclic_graph(self.G)

    # #### DAG generator Layer_By_Layer 算法  #### #
    def gen_layer_by_layer(self, n, m):
        pass

    # #### DAG generator Fan_in_Fan_out 算法  #### #
    def gen_fan_in_fan_out(self, n, m):
        pass

    # #### DAG generator Random_Order 算法  #### #
    def gen_random_order(self, n, m):
        pass

    #####################################
    #   Section_2: WCET 配置算法 #
    #   参数a： 均匀分布的最小值、高斯分布的均值
    #   参数b： 均匀分布的最大值、高斯分布的方差
    #####################################
    def WCET_Config(self, WCET_Config_type, a, b):
        # 方式1（均匀分布）：在区间[a, b]中均匀分布方式生成 WCET
        if WCET_Config_type == "random":
            for x in self.G.nodes(data=True):
                x[1]['WCET'] = math.ceil(np.random.uniform(a, b))
                x[1]['BCET'] = x[1]['WCET']
                x[1]['ACET'] = x[1]['WCET']
        # 方式2（正态分布）：以loc=a为均值，以scale=b为方差 # size:输出形式 / 维度
        elif WCET_Config_type == "normal":
            for x in self.G.nodes(data=True):
                while True:
                    x[1]['WCET'] = math.ceil(np.random.normal(loc=a, scale=b, size=None))
                    if x[1]['WCET'] > 0:
                        x[1]['BCET'] = x[1]['WCET']
                        x[1]['ACET'] = x[1]['WCET']
                        break
        # 方式3（高斯分布，gauss）以均值为mu=a，标准偏差为sigma=b的方式生成 WCET
        elif WCET_Config_type == "gauss":
            for x in self.G.nodes(data=True):
                while True:
                    x[1]['WCET'] = math.ceil(rand.gauss(a, b))
                    if x[1]['WCET'] > 0:
                        x[1]['BCET'] = x[1]['WCET']
                        x[1]['ACET'] = x[1]['WCET']
                        break
        else:
            pass

    #####################################
    #   Section_3: 优先级 配置算法 #
    #####################################
    def Priority_Config(self, Priority_Config_type):
        if Priority_Config_type == "random":
            self.priority_random_config()
        elif Priority_Config_type == "Zhao":
            self.priority_Zhao_config()
        elif Priority_Config_type == "He2019":
            self.priority_He2019_config()
        elif Priority_Config_type == "He2021":
            self.priority_He2021_config()
        elif Priority_Config_type == "Chen":
            self.priority_Chen_config()
        elif Priority_Config_type == "Mine":
            self.priority_Mine_config()
        elif Priority_Config_type == "WCET":
            self.priority_WCET_config()
        else:
            print("priority config error!\n")

    def priority_random_config(self):
        priority_random_list = list(range(0, self.G.number_of_nodes()))
        np.random.shuffle(priority_random_list)
        for x in self.G.nodes(data=True):
            x[1]['priority'] = priority_random_list.pop()

    def priority_Zhao_config(self):
        pass

    def priority_He2019_config(self):
        pass

    def priority_He2021_config(self):
        pass

    def priority_Chen_config(self):
        # 1. 关键路径分组；
        node_list = nx.dag_longest_path(self.G, weight='weight')  # 关键路径
        for x in node_list:
            temp_c_node = self.G.node[x]
        print('关键路径：{0}'.format(node_list))
        # 2. 到sink的路径最长者优先；
        # 3. wcet优先；
        # 4. 关键路径优先；
        pass

    def priority_Mine_config(self):

        pass

    def priority_WCET_config(self):
        temp_node_wcet = nx.get_node_attributes(self.G, 'WCET')
        temp_node_wcet = dict(sorted(temp_node_wcet.items(), key=lambda x: x[1], reverse=True))
        Temp_1 = 1
        for k, v in temp_node_wcet.items():
            self.G.node[k]['priority'] = Temp_1
            Temp_1 += 1
        return False

    #####################################
    #   Section_4: response time analysis arithmetic #
    #####################################
    def Response_Time_analysis(self, RTA_Type, core_num):
        if RTA_Type == "non-preemptive":
            return self.rta_basics_non_preemptive(core_num)
        elif RTA_Type == "preemptive":
            return self.rta_basics_preemptive(core_num)
        else:
            print("RTA_Type input error!")

    def rta_basics_non_preemptive(self, core_num):
        node_list = list(self.G.nodes())
        paths = list(nx.all_simple_paths(self.G, node_list[0], node_list[-1]))

        interference_node_list = []
        ret_path_and_rta = [0, 0, 0, [], []]
        for x in paths:
            temp_interference_node_list = []
            temp_path_weight = 0
            for y in x:
                temp_all_node = self.G.nodes(data=True)
                temp_ance = list(nx.ancestors(self.G, y))
                temp_desc = list(nx.descendants(self.G, y))
                temp_self = x
                sub_node = self.G.nodes[y]
                for z in temp_all_node:
                    if (z[0] not in temp_ance) and (z[0] not in temp_desc) and (z[0] not in temp_self):  # 判断z是否是干扰节点
                        if z[1]['priority'] < sub_node.get('priority'):             # 判断此z的优先级是否大于y
                            if z not in temp_interference_node_list:            # 判断此z是否已经加入
                                temp_interference_node_list.append(z)
                temp_path_weight += sub_node.get('WCET')
                # 每个节点的非前驱和非后继节点
            temp_inter_weight = 0
            for y in temp_interference_node_list:
                temp_inter_weight += y[1]['WCET']
            interference_node_list.append(temp_interference_node_list)
            temp_rta = temp_path_weight + temp_inter_weight/core_num
            # 计算此路径的RTA
            # ret_path_and_rta.append((temp_rta, temp_path_weight, temp_inter_weight, x, temp_interference_node_list))
            if temp_rta > ret_path_and_rta[0]:
                ret_path_and_rta[0] = temp_rta
                ret_path_and_rta[1] = temp_path_weight
                ret_path_and_rta[2] = temp_inter_weight
                ret_path_and_rta[3] = x
                ret_path_and_rta[4] = temp_interference_node_list
        return math.ceil(ret_path_and_rta[0])

    def rta_basics_preemptive(self, core_num):
        node_list = list(self.G.nodes())
        paths = list(nx.all_simple_paths(self.G, node_list[0], node_list[-1]))

        interference_node_list = []
        ret_path_and_rta = [0, 0, 0, [], []]
        for x in paths:
            temp_interference_node_list = []
            reserve_node_list = {}
            temp_path_weight = 0
            temp_WCET = []
            for y in x:
                temp_all_node = self.G.nodes(data=True)
                temp_ance = list(nx.ancestors(self.G, y))
                temp_desc = list(nx.descendants(self.G, y))
                temp_self = x
                sub_node = self.G.nodes[y]
                temp_path_weight += sub_node.get('WCET')
                temp_WCET.append(sub_node.get('WCET'))
                for z in temp_all_node:
                    if (z[0] not in temp_ance) and (z[0] not in temp_desc) and (z[0] not in temp_self):  # 判断z是否是干扰节点
                        if z[1]['priority'] < sub_node.get('priority'):   # 判断此z的优先级是否大于y
                            if z not in temp_interference_node_list:            # 判断此z是否已经加入
                                temp_interference_node_list.append(z)
                        else:
                            reserve_node_list[z[0]] = z[1]['WCET']
            t_reserve_list = sorted(reserve_node_list.items(), key=lambda x: x[1])
            add_reserve = 0
            for y in range(0, min(core_num, len(t_reserve_list))):
                add_reserve += t_reserve_list[y][1]
            temp_inter_weight = 0
            for y in temp_interference_node_list:
                temp_inter_weight += y[1]['WCET']
            interference_node_list.append(temp_interference_node_list)
            temp_rta = temp_path_weight + (temp_inter_weight+add_reserve)/core_num
            # 计算此路径的RTA
            if temp_rta > ret_path_and_rta[0]:
                ret_path_and_rta[0] = temp_rta
                ret_path_and_rta[1] = temp_path_weight
                ret_path_and_rta[2] = temp_inter_weight
                ret_path_and_rta[3] = x
                ret_path_and_rta[4] = temp_interference_node_list
        return math.ceil(ret_path_and_rta[0])


        #####################################
        #   section2. 获取DAG的时间相关参数
        #####################################
        # #### 1.DAG最差执行时间list  #### #
        WCET_list = [x[1]['WCET'] for x in self.G.nodes.data(data=True)]
        print("WCET_list：{0}".format(WCET_list))
        print("DAG_Volume：{0}".format( np.sum(WCET_list) ))
        print("Max_WCET：{0}".format( max(WCET_list) ))
        print("Min_WCET：{0}".format( min(WCET_list) ))
        print("Ave_WCET：{0:0.2f}".format( np.mean(WCET_list) ))
        print("Std_WCET：{0:0.2f}".format( np.std(WCET_list) ))

        self.DAG_volume = np.sum(WCET_list)
        self.Max_WCET = max(WCET_list)
        self.Min_WCET = min(WCET_list)
        self.Ave_WCET = np.mean(WCET_list)
        self.Std_WCET = np.std(WCET_list)

        worksheet.write(i, 0, i)
        worksheet.write(i, 1, self.G.number_of_nodes())
        worksheet.write(i, 2, self.G.number_of_edges())

        worksheet.write(i, 3, self.Max_Shape)
        worksheet.write(i, 4, self.Min_Shape)
        worksheet.write(i, 5, int(self.Ave_Shape))
        worksheet.write(i, 6, self.Std_Shape)

        worksheet.write(i, 7, self.Max_Reverse_Shape)
        worksheet.write(i, 8, self.Min_Reverse_Shape)
        worksheet.write(i, 9, self.Ave_Reverse_Shape)
        worksheet.write(i, 10, self.Std_Reverse_Shape)

        worksheet.write(i, 11, max(anti_chains_num_list) )

        worksheet.write(i, 12, self.Max_Degree)
        worksheet.write(i, 13, self.Min_Degree)
        worksheet.write(i, 14, self.Ave_Degree)
        worksheet.write(i, 15, self.Std_Degree)

        worksheet.write(i, 16, self.Max_In_Degree)
        worksheet.write(i, 17, self.Min_In_Degree)
        worksheet.write(i, 18, self.Ave_In_Degree)
        worksheet.write(i, 19, self.Std_In_Degree)

        worksheet.write(i, 20, self.Max_Out_Degree)
        worksheet.write(i, 21, self.Min_Out_Degree)
        worksheet.write(i, 22, self.Ave_Out_Degree)
        worksheet.write(i, 23, self.Std_Out_Degree)

        worksheet.write(i, 24, Dag_density)

    #########################################
    #   Show DAG
    #   DAG graph_node_position_determine
    #########################################
    def graphviz_DAG_show(self):
        dot = gz.Digraph()
        for node_x in self.G.nodes(data=True):
            temp_label = ''
            temp_label += 'Node_ID:' + str(node_x[1]['Node_ID']) + '\n'
            temp_label += 'rank:' + str(node_x[1]['rank']) + '\n'
            temp_label += 'WCET:' + str(node_x[1]['WCET']) + '\n'
            if node_x[1]['critic']:
                color_t = 'red'
            else:
                color_t = 'green'
            dot.node('%s' % node_x[0], temp_label, color=color_t)
        for edge_x in self.G.edges(data=True):
            dot.edge(str(edge_x[0]), str(edge_x[1]))
        # print(dot.source)
        # dot.view()
    """


if __name__ == "__main__":
    G = DAG_Generator()  # step0. 初始化DAG

    Dags_Num = 100
    """
    # ############ GNM ############## #
    arithmetic  = 'GNM'
    Node_Num    = 10
    Edge_Num    = 20
    G.Main_Workbench(arithmetic, [Node_Num, Edge_Num], Dags_Num)
    """
    # ############ GNP ############## #
    """
    arithmetic  = 'GNP'
    Node_Num    = 10
    Edge_Pro    = 0.3       # 0.4很难找到有向无环图
    G.Main_Workbench(arithmetic, [Node_Num, Edge_Pro], Dags_Num)
    """
    # ############ MINE ############## #
    # """
    arithmetic  = 'MINE'
    Node_Num            = 9
    Critic_Path         = 5

    Max_Shape           = 3
    Min_Shape           = 1

    Max_in_degree       = 3
    Max_out_degree      = 3

    Jump_level          = 2
    Connection_ratio    = 0.75
    Width               = 4
    G.Main_Workbench(arithmetic, [Node_Num, Critic_Path, Jump_level, Max_Shape, Min_Shape, Max_in_degree, Max_out_degree, Connection_ratio, Width], Dags_Num)

    # """
    # ############ User ############## #
    """
    arithmetic = 'USER'
    excel_address = './data/HUAWEI_10_12_1.xlsx'
    DAG_list = G.Main_Workbench(arithmetic, [excel_address], 0)
    for s_dag in DAG_list:
        G.Graphviz_show(s_dag)
    """
