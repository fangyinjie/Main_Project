#!/usr/bin/python3
# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # 
# Randomized DAG Generator
# Create Time: 2023/9/1311:38
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
# # # # # # # # # # # # # # # #
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
    if Algorithm == 'MINE_NEW':
        dag_list = __gen_mine(Algorithm_param_dict)
    else:
        pass
    return dag_list


# #### DAG generator mine 算法  #### #
def __gen_mine(Param_Dict):
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
