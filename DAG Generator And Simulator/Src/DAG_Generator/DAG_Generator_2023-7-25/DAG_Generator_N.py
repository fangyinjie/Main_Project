#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Randomized DAG Generator
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################
from z3 import *
import numpy as np
import pandas as pd
import networkx as nx
from itertools import combinations
from random import random, sample, uniform, randint


# #### DAG generator mine 算法  #### #
def Gen_mine_new(Param_Dict):
    Temp_DAG_list = []
    n = Param_Dict['Node_Num']
    # (1) 邻接矩阵
    ADJ_Matrix = np.full(shape=(n, n), fill_value=Int('None'))
    for x in range(n):
        for y in range(n):
            ADJ_Matrix[x][y] = Int(f"ADJ_{x}_{y}")

    # (2) 可达矩阵
    Arr_Matrix = ADJ_Matrix + np.eye(n, dtype=int)
    for _ in range(n):
        Arr_Matrix = np.dot(Arr_Matrix, ADJ_Matrix + np.eye(n, dtype=int))
    Arr_Matrix_Binary = np.full(shape=(n, n), fill_value=Int('None'))

    for x in range(n):
        for y in range(n):
            Arr_Matrix_Binary[x][y] = If(Arr_Matrix[x][y] > 0, 1, 0)

    s = Solver()
    # sink 和 source 分别默认为第一个和最后一个结点；
    # (1) 基础约束1，一个source & sink结点；
    for n_y in range(1, n):
        s.add(ADJ_Matrix[:, n_y].sum() > 0)  # 除了第一例，其他列的和都大于0；
    for n_x in range(n - 1):
        s.add(ADJ_Matrix[n_x, :].sum() > 0)  # 除了最后一行，其他行的和都大于0；
    # (1) 基础约束2，DAG是连通的；
    s.add(Arr_Matrix_Binary[0, :].sum() == n)  # source结点+全部可达
    s.add(Arr_Matrix_Binary[:, n - 1].sum() == n)  # 所有结点全部可达sink；
    # (1) 基础约束3，下三角 && 对角线全部为0
    # for n_x in range(n):
    #     for n_y in range(n):
    #         if n_y <= n_x:
    #             s.add(ADJ_Matrix[n_x][n_y] == 0)
    #         else:
    #             s.add(Or([ADJ_Matrix[n_x][n_y] == 1, ADJ_Matrix[n_x][n_y] == 0]))
    # (1) 基础约束4， 无环，可达矩阵的
    for n_xy in range(n):
        s.add(Arr_Matrix[n_xy][n_xy] == 1)  # 所有结点全部可达sink；
    # (1) 基础约束4，边只有单向的
    # for n_x in range(n):
    #     for n_y in range(n):
    #         if n_x == n_y:
    #             s.add(ADJ_Matrix[n_x][n_y] == 0)
    #         else:
    #             s.add(ADJ_Matrix[n_x][n_y] + ADJ_Matrix[n_y][n_x] <= 1)
    #             s.add(Or([ADJ_Matrix[n_x][n_y] == 1, ADJ_Matrix[n_x][n_y] == 0]))
    #             # s.add(Arr_Matrix_Binary[n_x][n_y] + Arr_Matrix_Binary[n_y][n_x] <= 1)
    sDAG_NUM = 0
    while True:
        sDAG_NUM += 1
        if str(s.check()) == 'sat':
            result = s.model()
            ret_ADJ_Matrix = np.full(shape=(n, n), fill_value=1, dtype=int)
            for i in range(n):
                for j in range(n):
                    ret_ADJ_Matrix[i][j] = int(result.eval(ADJ_Matrix[i][j]).as_long())
            ret_ARR_Matrix = np.full(shape=(n, n), fill_value=1, dtype=int)
            for i in range(n):
                for j in range(n):
                    ret_ARR_Matrix[i][j] = result.eval(Arr_Matrix[i][j]).as_long()
            ret_ARR_Matrix_Binary = np.full(shape=(n, n), fill_value=1, dtype=int)
            for i in range(n):
                for j in range(n):
                    ret_ARR_Matrix_Binary[i][j] = result.eval(Arr_Matrix_Binary[i][j]).as_long()
            #
            print(f"dag_id{sDAG_NUM}")
            # print(f"{ret_ADJ_Matrix}")
            # print(f"{ret_ARR_Matrix}")
            # print(f"{ret_ARR_Matrix_Binary}")
            # eigenvalue, featurevector = np.linalg.eig(ret_ARR_Matrix - np.eye(n))
            # for i in range(len(eigenvalue)):
            #     eigenvalue[i] = round(eigenvalue[i], 2)
            # print("特征值：", eigenvalue)

            Temp_G = nx.DiGraph(ret_ADJ_Matrix)
            Temp_G.graph['DAG_ID'] = str(sDAG_NUM)
            # 生成结果检查
            assert format(nx.is_directed_acyclic_graph(Temp_G))
            for node_x in Temp_G.nodes(data=True):
                node_x[1]['Node_Index'] = node_x[0]
                node_x[1]['Node_ID'] = node_x[0]
            # assert shape_list == [sorted(generation) for generation in nx.topological_generations(Temp_G)]
            Temp_DAG_list.append(Temp_G)
            s.add(Or([ADJ_Matrix[i][j] != result[ADJ_Matrix[i][j]] for i in range(n) for j in range(n)]))

        else:
            print(f"work finish dag_num:{len(Temp_DAG_list)}!\n")
            break
    return Temp_DAG_list


if __name__ == "__main__":
    # assert  n <= 2
    for Node_Num in range(1, 7):
        All_DAG_list = Gen_mine_new({'Node_Num': Node_Num})
