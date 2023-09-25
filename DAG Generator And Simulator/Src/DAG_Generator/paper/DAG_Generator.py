#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Randomized DAG Generator
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################
import os
import re
import math
import copy
# import datetime
import itertools

import numpy as np
import pandas as pd
import networkx as nx
import graphviz as gz
import z3.z3
# from itertools import combinations
from z3.z3 import Int, Sum, If, Solver, Or, IntNumRef, Bool, And, Implies
from random import random, sample, uniform, randint


def Algorithm_input(Algorithm, Algorithm_param_dict):
    dag_list = []
    if Algorithm == 'MINE_NEW2':
        dag_list = __gen_mine_new(Algorithm_param_dict)
    elif Algorithm == 'MINE_NEW':
        dag_list = __gen_mine_new_new(Algorithm_param_dict)
    else:
        pass
    return dag_list

# #### DAG generator mine 算法  #### #
def __gen_mine_new_new(Param_Dict):
    n = Param_Dict['Node_Num']
    ret_DAG_list = []
    dag = nx.DiGraph()
    # 添加节点
    # (1) 输入统一插入头结点
    dag.add_node(1)
    # (2) 输入中间结点
    ret_DAG_list = __dag_insert_node(dag, n, Param_Dict)
    # (3) 输入统一插入尾结点
    for dag_x in ret_DAG_list:
        # 获取所有后继为0的结点
        ns_node_list = [node_x for node_x in dag_x.nodes() if len(list(dag_x.successors(node_x))) == 0]
        dag_x.add_node(n)
        for ns_node_x in ns_node_list:
            dag_x.add_edge(ns_node_x, n)
    return ret_DAG_list

def __dag_insert_node(dag, node_num, Param_Dict):
    if dag.number_of_nodes() == node_num - 1:
        return [dag]
    elif dag.number_of_nodes() < node_num - 1:
        ret_dag_list = []
        # 穷举所有前驱（至少1个）
        pred_node_opt_list = []
        for n in range(dag.number_of_nodes()):
            pred_node_opt_list += list(itertools.combinations(list(dag.nodes()), n + 1))
        for pred_node_opt_x in pred_node_opt_list:
            temp_dag_x = copy.deepcopy(dag)
            temp_node_num = dag.number_of_nodes() + 1
            # 插入到处第二个结点，
            temp_dag_x.add_node(temp_node_num)
            # 连接边，
            for pnodex in pred_node_opt_x:
                temp_dag_x.add_edge(pnodex, temp_node_num)
            ret_dag_list += __dag_insert_node(temp_dag_x, node_num, Param_Dict)
        return ret_dag_list
    else:
        os.error(f'node_num_error ; node_num:{node_num}')
# #### DAG generator mine 算法  #### #
def __gen_mine_new(Param_Dict):
    n = Param_Dict['Node_Num']
    # (1) param*: 单位矩阵 IDE_Matrix
    IDE_Matrix = np.full(shape=(n, n), fill_value=Int('None'))
    for x in range(n):
        for y in range(n):
            IDE_Matrix[x][y] = Int(f"I_{x}_{y}")

    # (2) param*: 邻接矩阵 ADJ_Matrix
    ADJ_Matrix = np.full(shape=(n, n), fill_value=Int('None'))
    for x in range(n):
        for y in range(n):
            ADJ_Matrix[x][y] = Int(f"T_{x}_{y}")

    # (3) param*: 可达矩阵 ARR_Matrix
    ARR_Matrix = np.full(shape=(n, n), fill_value=Int('None'))
    for x in range(n):
        for y in range(n):
            ARR_Matrix[x][y] = Int(f"D_{x}_{y}")

    # (4) param*: 传递约简矩阵 TRA_Matrix
    TRA_Matrix = np.full(shape=(n, n), fill_value=Int('None'))
    for x in range(n):
        for y in range(n):
            TRA_Matrix[x][y] = Int(f"TR_{x}_{y}")

    s = Solver()

    # (1) 单位/逆单位矩阵约束
    for x in range(n):
        for y in range(n):
            if x == y:
                s.add(IDE_Matrix[x][y] == 1)
            else:
                s.add(IDE_Matrix[x][y] == 0)

    # (2) 邻接矩阵约束
    # 基础约束 1，一个source & sink结点；sink 和 source 分别默认为第一个和最后一个结点；
    for n_y in range(1, n):
        s.add(ADJ_Matrix[:, n_y].sum() > 0)  # 除了第一例，其他列的和都大于0；
    for n_x in range(n - 1):
        s.add(ADJ_Matrix[n_x, :].sum() > 0)  # 除了最后一行，其他行的和都大于0；
    # 基础约束 2，下三角 && 对角线全部为0
    for n_x in range(n):
        for n_y in range(n):
            if n_y <= n_x:
                s.add(ADJ_Matrix[n_x][n_y] == 0)
            else:
                s.add(Or([ADJ_Matrix[n_x][n_y] == 1, ADJ_Matrix[n_x][n_y] == 0]))

    # (3) 可达矩阵约束
    ARR_Matrix_temp = ADJ_Matrix + np.identity(n)
    for _ in range(n):
        ARR_Matrix_temp = np.dot(ARR_Matrix_temp, ADJ_Matrix + np.identity(n))

    for x in range(n):
        for y in range(n):
            if x == y:
                s.add(ARR_Matrix[x][y] == 0)
            else:
                s.add(ARR_Matrix[x][y] == If(ARR_Matrix_temp[x][y] > 0, 1, 0))

    # (4) 约简矩阵约束
    TRA_Matrix_temp = np.matmul(ADJ_Matrix, ARR_Matrix)
    for x in range(n):
        for y in range(n):
            s.add(TRA_Matrix[x][y] == If(And([ADJ_Matrix[x][y] == 1, TRA_Matrix_temp[x][y] == 0]), 1, 0))


    ret_DAG_list = []
    sDAG_NUM = 0
    # while True:
    while sDAG_NUM := sDAG_NUM + 1:
        if str(s.check()) == 'sat':
            result = s.model()
            ret_TRA_Matrix = np.full(shape=(n, n), fill_value=1, dtype=int)
            for i in range(n):
                for j in range(n):
                    ret_TRA_Matrix[i][j] = int(result.eval(TRA_Matrix[i][j]).as_long())

            ret_ARR_Matrix = np.full(shape=(n, n), fill_value=1, dtype=int)
            for i in range(n):
                for j in range(n):
                    ret_ARR_Matrix[i][j] = result.eval(ARR_Matrix[i][j]).as_long()

            ret_ADJ_Matrix = np.full(shape=(n, n), fill_value=1, dtype=int)
            for i in range(n):
                for j in range(n):
                    ret_ADJ_Matrix[i][j] = result.eval(ADJ_Matrix[i][j]).as_long()
            #
            # print(f"{sDAG_NUM}")
            # print(f"{ret_ADJ_Matrix}")
            # print(f"{ret_ARR_Matrix}")
            # print(f"{np.matmul(ret_ADJ_Matrix, ret_ARR_Matrix) }")
            # print(f"{ret_TRA_Matrix}")
            # eigenvalue, featurevector = np.linalg.eig(ret_ARR_Matrix - np.eye(n))
            # for i in range(len(eigenvalue)):
            #     eigenvalue[i] = round(eigenvalue[i], 2)
            # print("特征值：", eigenvalue)

            Temp_G = nx.DiGraph(ret_TRA_Matrix)
            Temp_G.graph['DAG_ID'] = str(sDAG_NUM)
            # 生成结果检查
            assert format(nx.is_directed_acyclic_graph(Temp_G))
            for node_x in Temp_G.nodes(data=True):
                node_x[1]['Node_Index'] = node_x[0]
                node_x[1]['Node_ID'] = node_x[0]
            # assert shape_list == [sorted(generation) for generation in nx.topological_generations(Temp_G)]
            ret_DAG_list.append(Temp_G)
            s.add(Or([TRA_Matrix[i][j] != result[TRA_Matrix[i][j]] for i in range(n) for j in range(n)]))

        else:
            print(f"work finish dag_num:{len(ret_DAG_list)}!\n")
            break
    return ret_DAG_list


def exam_pic_show(dag_x, title):
    dot = gz.Digraph()
    dot.attr(rankdir='LR')
    for node_x in dag_x.nodes(data=True):
        temp_label = 'Node_ID:{0}'.format(str(node_x[0]))
        dot.node('%s' % node_x[0], temp_label, color='black')
    for edge_x in dag_x.edges():
        dot.edge('%s' % edge_x[0], '%s' % edge_x[1])
    # dot.view('./test.png')
    dot.view(f'./generator_test/{title}')

if __name__ == "__main__":
    # DAG_Num       确定      否则穷举
    # Node_Num      确定      否则从小到大依次输出
    for node_num in range(3, 9):
        All_DAG_list = Algorithm_input('MINE_NEW',{'Node_Num': node_num})
    # for dag_x in All_DAG_list:
    #     exam_pic_show(dag_x, str(dag_x.graph['DAG_ID']))
        dag_num = len(All_DAG_list)
        print(f'node_num :{node_num} _ DAG_num:{dag_num}')

