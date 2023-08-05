#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Randomized DAG Generator
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################
# import re
import math
# import copy
# import datetime
import numpy as np
import pandas as pd
import networkx as nx
import os
# from z3 import *
from z3 import *
# from itertools import combinations
# from random import random, sample, uniform, randint


######################
# Generation type 2 ~
# Algorithm_Generation
# adjacent_matrix
######################
from z3.z3 import Int, Solver, If, Sum, Or, Bool, IntNumRef


def Algorithm_input(Algorithm, Algorithm_param_dict):
    dag_list = []
    if Algorithm == 'MINE':
        dag_list = __gen_mine_new(Algorithm_param_dict)
    return dag_list


# #### DAG generator mine 算法  #### #
def __gen_mine_new(Param_Dict):
    # 这里Node_Num和Critic_Path是算首尾结点的
    assert (Param_Dict['Node_Num'] > 3)
    assert (Param_Dict['Critic_Path'] >= 3)
    assert (Param_Dict['Jump_level'] >= 1)
    assert (Param_Dict['Max_in_degree'] >= 1)
    assert (Param_Dict['Max_out_degree'] >= 1)
    assert (Param_Dict['Max_Shape'] >= Param_Dict['Min_Shape'])
    assert (Param_Dict['Min_Shape'] >= 1)
    assert (Param_Dict['Width'] >= Param_Dict['Max_Shape'])
    assert ((Param_Dict['Node_Num'] - 2) <= Param_Dict['Max_Shape'] * (Param_Dict['Critic_Path'] - 2))
    assert ((Param_Dict['Node_Num'] - 2) >= Param_Dict['Min_Shape'] * (Param_Dict['Critic_Path'] - 2))

    # 参数定义：
    n = Param_Dict['Node_Num']
    k = Param_Dict['Critic_Path']
    max_shape = Param_Dict['Max_Shape']
    min_shape = Param_Dict['Min_Shape']
    max_out_degree = Param_Dict['Max_out_degree']
    max_in_degree = Param_Dict['Max_in_degree']
    width = Param_Dict['Width']
    jl = Param_Dict['Jump_level']
    connection_ratio = Param_Dict['Conn_ratio']
    DAG_Num = Param_Dict['DAG_Num']

    # width_list = np.full(shape=n, fill_value=Int('None'))
    # for x in range(n):
    #     width_list[x] = Int(f'node_level_{x}')
    node_level_list = np.full(shape=n, fill_value=Int('None'))
    for x in range(n):
        node_level_list[x] = Int(f'node_level_{x}')
    ADJ_Matrix = np.full(shape=(n, n), fill_value=Int('None'))
    for x in range(n):
        for y in range(n):
            ADJ_Matrix[x][y] = Bool(f"ADJ_{x}_{y}")
    TEM_Matrix = np.full(shape=(n, n), fill_value=Int('None'))
    for x in range(n):
        for y in range(n):
            TEM_Matrix[x][y] = Int(f"TEM_{x}_{y}")
    Arr_Matrix_2 = np.full(shape=(n, n), fill_value=Int('None'))
    for x in range(n):
        for y in range(n):
            Arr_Matrix_2[x][y] = Int(f"ARR2_{x}_{y}")

    s = Solver()
    for x in range(n):
        for y in range(n):
            if x == y:
                s.add(TEM_Matrix[x][y] == 1)
            else:
                s.add(TEM_Matrix[x][y] == If(ADJ_Matrix[x][y], 1, 0))

    Arr_Matrix = np.power(TEM_Matrix, n)

    # (2) Shape内元素为0
    # (2.1) 确定shape
    for n_x in range(1, n-1):
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

    # (1) 下三角 && 对角线全部为0
    s.add([ADJ_Matrix[n_x][n_y] == False for n_x in range(n) for n_y in range(n_x + 1)])

    for n_x in range(n):
        # (2) shape内元素为0
        s.add([ADJ_Matrix[n_x][n_y] == If(node_level_list[n_x] == node_level_list[n_y], False, ADJ_Matrix[n_x][n_y]) for n_y in range(n_x + 1, n)])
        # (5) 度约束
        sum_out_degree = [If(ADJ_Matrix[n_x][n_y], 1, 0) for n_y in range(n_x + 1, n)]
        sum_in_degree = [If(ADJ_Matrix[n_y][n_x], 1, 0) for n_y in range(n_x)]
        s.add(Sum(sum_in_degree) <= max_in_degree)  # (6) 出度约束
        s.add(Sum(sum_out_degree) <= max_in_degree)  # (7) 入度约束

    # (3) jl, indegree, outdegree
    for n_x in range(1, n):
        s.add(Sum([If(node_level_list[n_x] - node_level_list[n_y] == 1, ADJ_Matrix[n_y][n_x], False) for n_y in range(n_x)]) >= 1)
        s.add(Sum([If(node_level_list[n_x] - node_level_list[n_y] > jl, ADJ_Matrix[n_y][n_x], False) for n_y in range(n_x)]) == 0)  # jl 约束向前
    for n_x in range(n - 1):
        s.add(Or([If(node_level_list[n_y] - node_level_list[n_x] > 0, ADJ_Matrix[n_x][n_y], False) for n_y in range(n_x + 1, n)]) == True)  # jl 约束后前
        s.add(Or([If(node_level_list[n_y] - node_level_list[n_x] > jl, ADJ_Matrix[n_x][n_y], False) for n_y in range(n_x + 1, n)]) == False)  # jl 约束后前

    # (4) 稠密度约束  必须小于 connection_ratio 即 m 小于 connection_ratio * n * （n-1） / 2
    s.add(Sum([If(ADJ_Matrix[n_x][n_y], 1, 0) for n_x in range(n) for n_y in range(n_x + 1, n)]) <= (connection_ratio * n * (n - 1) / 2))
    # s.add(Sum(sum_out_degree + sum_in_degree) <= max_degree)  # (8) 度约束
    # (6) DAG的width 约束：
    # """
    width_dict = {}
    for x in range(n):
        for y in range(n):
            Arr_Matrix_2[x][y] = If(Arr_Matrix[x][y] == 0, 0, 1)
    for n_x in range(1, n - 1):
        width_dict[n_x] = [Arr_Matrix_2[n_y][n_x] for n_y in range(n_x)] + [Arr_Matrix_2[n_x][n_y] for n_y in range(n_x + 1, n)]
        s.add(Sum(width_dict[n_x]) <= width)
    s.add(Or([Sum(width_dict[n_x]) == width for n_x in range(1, n - 1)]) == True)
    # """
    Temp_DAG_list = []
    for sDAG_NUM in range(DAG_Num):
        if str(s.check()) == 'sat':
            result = s.model()
            ret_level = np.full(shape=n, fill_value=1)
            for i in range(n):
                ret_level[i] = result[node_level_list[i]].as_long()
            ret_ADJ_Matrix = np.full(shape=(n, n), fill_value=False)
            for i in range(n):
                for j in range(n):
                    ret_ADJ_Matrix[i][j] = result.eval(ADJ_Matrix[i][j])
            ret_ARR_Matrix = np.full(shape=(n, n), fill_value=1, dtype=IntNumRef)
            for i in range(n):
                for j in range(n):
                    ret_ARR_Matrix[i][j] = result.eval(Arr_Matrix[i][j])
            ret_ARR_Matrix2 = np.full(shape=(n, n), fill_value=1, dtype=IntNumRef)
            for i in range(n):
                for j in range(n):
                    ret_ARR_Matrix2[i][j] = result.eval(Arr_Matrix_2[i][j])
            """
            print("")
            print(f"{ret_level}")
            print(f"{ret_ADJ_Matrix}")
            print(f"{ret_ARR_Matrix}")
            print(f"{ret_ARR_Matrix2}")
            """
            Temp_G = nx.DiGraph(ret_ADJ_Matrix)
            Temp_G.graph['DAG_ID'] = str(sDAG_NUM)
            # 生成结果检查
            assert format(nx.is_directed_acyclic_graph(Temp_G))
            for node_x in Temp_G.nodes(data=True):
                t_edges_list = ''
                for s_node_x in list(Temp_G.successors( node_x[0] )):
                    t_edges_list += '({0},{1});'.format(node_x[0], s_node_x)
                node_x[1]['Edges_List'] = t_edges_list
                node_x[1]['Node_Index'] = node_x[0]
                node_x[1]['Node_ID'] = node_x[0]
            # assert shape_list == [sorted(generation) for generation in nx.topological_generations(Temp_G)]
            Temp_DAG_list.append(Temp_G)
            s.add(Or([ADJ_Matrix[i][j] != result[ADJ_Matrix[i][j]] for i in range(n) for j in range(n)]))

        else:
            print("fully output!\n")
            return Temp_DAG_list
    return Temp_DAG_list


def WCET_Config(temp_dag, Virtual_node, a, b):
    for x in temp_dag.nodes(data=True):
        x[1]['WCET'] = math.ceil(np.random.uniform(a, b))
        x[1]['BCET'] = x[1]['WCET']
        x[1]['ACET'] = x[1]['WCET']
    if Virtual_node:
        temp_dag.nodes[0]['WCET'] = 0
        temp_dag.nodes[temp_dag.number_of_nodes() - 1]['WCET'] = 0


def __exam_xlsx_Self_Output(DAG_list, address):
    temp_address = address + 'CSV/'
    os.makedirs(temp_address, mode=0o777, exist_ok=True)
    # title_list = ['Node_Index', 'Node_ID', 'Succ_Nodes', 'BCET', 'ACET', 'WCET', 'Group']
    title_list = ['Node_Index', 'Node_ID', 'Edges_List', 'BCET', 'ACET', 'WCET', 'Group', 'critic']
    writer = pd.ExcelWriter(temp_address + '2022-12-28(1)-experiment.xlsx')
    for dag_x in DAG_list:
        temp_data = {}
        node_id_list = []
        for node_x in dag_x.nodes(data=True):
            temp_data[node_x[0]] = node_x[1]
            node_id_list.append(node_x[0])
        df = pd.DataFrame(temp_data, index=title_list, columns=node_id_list)
        df = df.T
        df.to_csv(temp_address + str(dag_x.graph['DAG_ID']) + '.csv')

        df.to_excel(writer, sheet_name=str(dag_x.graph['DAG_ID']), index=False, header=True)
    writer._save()


if __name__ == "__main__":
    All_DAG_list = Algorithm_input('MINE', {'DAG_Num': 5, 'Node_Num': 16, 'Critic_Path': 8, 'Width': 5,
                                            'Jump_level': 1, 'Conn_ratio': 0.6, 'Max_Shape': 5,
                                            'Min_Shape': 1, 'Max_in_degree': 5, 'Max_out_degree': 5})
    MAX_WCET = 264088
    MIN_WCET = 3032

    for dag_id, dag_x in enumerate(All_DAG_list):
        WCET_Config(dag_x, False, MIN_WCET, MAX_WCET)

    __exam_xlsx_Self_Output(All_DAG_list, './test/')
