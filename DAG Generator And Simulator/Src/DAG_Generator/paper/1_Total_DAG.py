#!/usr/bin/python3
# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # 
# Randomized DAG Generator
# Create Time: 2023/9/1311:50
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
# # # # # # # # # # # # # # # #
import os
import re
import math
import copy
import time
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
        dag_list = __gen_mine_new(Algorithm_param_dict)
    # if Algorithm == 'MINE':
    #     dag_list = __gen_mine(Algorithm_param_dict)
    else:
        pass
    return dag_list








            # (1.1) 全穷举
            # (1.2) 反链
        # all_shape_list = __dag_insert_node(dag, node_num, Param_Dict)
def __dag_insert_level(dag, node_num, Param_Dict):
    dag_num = dag.number_of_nodes()
    level_node_list = list(range(dag_num + 1, dag_num + node_num + 1))
    # 获取向前连接的所有组合，元素中至少要有1个sink结点和
    if dag.number_of_nodes() == node_num:
        return [dag]
    elif dag.number_of_nodes() < node_num:
        ret_dag_list = []
        pred_node_opt_list = []
        # for n in range(1, dag.number_of_nodes() + 1):
        #     pred_node_opt_list += list(itertools.combinations(list(dag.nodes()), n))    # 穷举
        pred_node_opt_list = list(nx.antichains(dag, topo_order=None))
        for pred_node_opt_x in pred_node_opt_list:
            if len(pred_node_opt_x) == 0:
                continue
            temp_dag_x = copy.deepcopy(dag)
            temp_node_num = dag.number_of_nodes() + 1
            temp_dag_x.add_node(temp_node_num)
            for pnodex in pred_node_opt_x:
                temp_dag_x.add_edge(pnodex, temp_node_num)
            ret_dag_list += __dag_insert_node(temp_dag_x, node_num, Param_Dict)
        return ret_dag_list
    else:
        os.error(f'node_num_error ; node_num:{node_num}')


# #### DAG generator mine 算法  #### #
# def __gen_mine(Param_Dict):
#     n = Param_Dict['Node_Num']
#     dag = nx.DiGraph()
#     dag.add_node(1)
#     ret_dag_list = __dag_insert_node(dag, n - 1, Param_Dict)
#     for dag_x in ret_dag_list:
#         ns_node_list = [ns_node for ns_node in dag_x.nodes() if len(list(dag_x.successors(ns_node))) == 0]
#         for ns_node_x in ns_node_list:
#             dag_x.add_edge(ns_node_x, n)
#     return ret_dag_list
#
# def __dag_insert_node(dag, node_num, Param_Dict):
#     if dag.number_of_nodes() == node_num:
#         return [dag]
#     elif dag.number_of_nodes() < node_num:
#         ret_dag_list = []
#         pred_node_opt_list = []
#         for n in range(1, dag.number_of_nodes() + 1):
#             pred_node_opt_list += list(itertools.combinations(list(dag.nodes()), n))    # 穷举
#         # pred_node_opt_list = list(nx.antichains(dag, topo_order=None))
#         for pred_node_opt_x in pred_node_opt_list:
#             if len(pred_node_opt_x) == 0:
#                 continue
#             temp_dag_x = copy.deepcopy(dag)
#             temp_node_num = dag.number_of_nodes() + 1
#             temp_dag_x.add_node(temp_node_num)
#             for pnodex in pred_node_opt_x:
#                 temp_dag_x.add_edge(pnodex, temp_node_num)
#             ret_dag_list += __dag_insert_node(temp_dag_x, node_num, Param_Dict)
#         return ret_dag_list
#     else:
#         os.error(f'node_num_error ; node_num:{node_num}')

def exam_pic_show(dag_x, node_num, title):
    dot = gz.Digraph()
    dot.attr(rankdir='LR')
    for node_x in dag_x.nodes(data=True):
        temp_label = 'Node_ID:{0}'.format(str(node_x[0]))
        dot.node('%s' % node_x[0], temp_label, color='black')
    for edge_x in dag_x.edges():
        dot.edge('%s' % edge_x[0], '%s' % edge_x[1])
    # dot.view('./test.png')
    address = f'./generator_test/{node_num}/'
    os.makedirs(address, mode=0o777, exist_ok=True)
    dot.view(address + f'{title}')


# #### DAG generator new mine 算法  #### #
def __gen_mine_new(Param_Dict):
    node_num = Param_Dict['Node_Num']
    all_shape_list = shape_enumator(node_num, [1])
    ret_dag_list = []
    for shape_num_list in all_shape_list:
        shape_list = shape_list_trance(shape_num_list)
        dag_list = [nx.DiGraph()]
        for level_id, self_node_list in enumerate(shape_list):
            if (level_id + 1) == len(shape_list):
                for dag_x in dag_list:
                    p_nodes = [nodex for nodex in dag_x.nodes() if len(list(dag_x.successors(nodex))) == 0]
                    for p_node_x in p_nodes:
                        dag_x.add_edge(p_node_x, self_node_list[0])
            else:
                temp_dag_list = []
                for dag_x in dag_list:
                    temp_dag_list += shape_dag_generator(dag_x, self_node_list)
                dag_list = temp_dag_list
        ret_dag_list += dag_list
    return ret_dag_list

def shape_enumator(node_num, last_shape_num_list):
    reset_node_num = node_num - sum(last_shape_num_list)
    assert reset_node_num > 0
    if reset_node_num == 1:
        temp_new_last_shape_num_list = copy.deepcopy(last_shape_num_list)
        temp_new_last_shape_num_list.append(1)
        return [temp_new_last_shape_num_list]
    else:
        ret_list = []
        for slevel_node_num in range(1, reset_node_num):
            temp_new_last_shape_num_list = copy.deepcopy(last_shape_num_list)
            temp_new_last_shape_num_list.append(slevel_node_num)
            ret_list += shape_enumator(node_num, temp_new_last_shape_num_list)
        return ret_list

def shape_list_trance(shape_num_list):
    node_num = sum(shape_num_list)
    node_id_list = list(range(node_num))
    ret_shape_list = []
    for shape_num_x in shape_num_list:
        ret_shape_list.append(node_id_list[:shape_num_x])
        del node_id_list[:shape_num_x]
    return  ret_shape_list

def shape_dag_generator(dag_x, self_node_list):
    ret_dag_list = []
    # (1) 加新结点
    temp_dag_x = copy.deepcopy(dag_x)
    temp_dag_x.add_nodes_from(self_node_list)
    # (2) 加新边 pnode_list_enumerate
    # (2.1) 前驱sink点集合  sink_node_list
    # (2.2) 前驱内点集合  inter_node_list
    sink_node_list = []
    inter_node_list = []
    for node_x in dag_x.nodes():
        if len(list(dag_x.successors(node_x))) == 0:
            sink_node_list.append(node_x)
        else:
            inter_node_list.append(node_x)
    # (2.3) 穷举所有可行连接前驱 pnode_list_enumerate [(p1,p2,p3...),()], 至少1个sink——node,
    sink_node_enumerate_list = []
    for sn_num in range(len(sink_node_list)):
        sink_node_enumerate_list += list(itertools.combinations(sink_node_list, sn_num + 1))
    """
    # (2.4) 纯穷举
    inter_node_enumerate_list = []
    for in_num in range(len(inter_node_list) + 1):
    """
    pnode_list_enumerate = []

    """
    inter_node_enumerate_list += list(itertools.combinations(inter_node_list, in_num))

    for inter_node_enumerate_x in inter_node_enumerate_list:
        for sink_node_enumerate_x in sink_node_enumerate_list:
            pnode_list_enumerate.append(inter_node_enumerate_x + sink_node_enumerate_x)
    """
    # (2.5) sink的对抗链
    for sink_node_enumerate_x in sink_node_enumerate_list:
        # 1) 样例DAG 删除sink node的所有祖先；
        sample_dag = copy.deepcopy(dag_x)
        rem_set = set(sink_node_enumerate_x)
        for sink_node_x in sink_node_enumerate_x:
            rem_set.update(nx.ancestors(sample_dag, sink_node_x))
        sample_dag.remove_nodes_from(rem_set)
        # (2) 获取剩下DAG的对抗链子；
        pred_node_opt_list = list(nx.antichains(sample_dag, topo_order=None))
        for pred_node_opt_x in pred_node_opt_list:
            pred_node_opt_x += sink_node_enumerate_x
        pnode_list_enumerate += pred_node_opt_list

    # (2.4) 根据本层结点搭配组合 edge_pnode_ret_list      [ [1:[p11,p12,p13],2:[p21,p22,p23],3:[p31,p32,p33]], [1:[p11,p12,p13],2:[p21,p22,p23],3:[p31,p32,p33]] ]
    if len(pnode_list_enumerate) == 0:
        ret_dag_list.append(temp_dag_x)
    else:

        edge_p_list = list(itertools.combinations_with_replacement(pnode_list_enumerate, len(self_node_list))) # 从可行解法中抽取 len(sn)个
        for edge_p_list_x in edge_p_list:
            temp_dag_list_x = copy.deepcopy(temp_dag_x)
            for self_node_id, edges_p_x in enumerate(edge_p_list_x):
                for edge_p_x in edges_p_x:
                    temp_dag_list_x.add_edge(edge_p_x, self_node_list[self_node_id])
            ret_dag_list.append(temp_dag_list_x)
    return ret_dag_list



if __name__ == "__main__":
    # DAG_Num       确定      否则穷举
    # Node_Num      确定      否则从小到大依次输出
    # dag_list = [nx.DiGraph()]
    # shape_list = [[0],[1,2,3],[4,5,6,7,8],[9,10,11,12],[13,14,15,16],[17]]
    # for self_node_list in shape_list:
    #     temp_dag_list = []
    #     for dag_x in dag_list:
    #         temp_dag_list += shape_dag_generator(dag_x, self_node_list)
    #     dag_list = temp_dag_list

    for node_num in range(4, 6):
        stime = time.time()
        # All_DAG_list = Algorithm_input('MINE',{'Node_Num': node_num})
        All_DAG_list = Algorithm_input('MINE_NEW',{'Node_Num': node_num})
        etime = time.time()
        # 同构去除
        for dag_id, dag_x in enumerate(All_DAG_list):
            exam_pic_show(dag_x, str(node_num), str(dag_id))
        dag_num = len(All_DAG_list)
        print(f'node_num :{node_num} _ DAG_num:{dag_num} _ time:{etime - stime}')

