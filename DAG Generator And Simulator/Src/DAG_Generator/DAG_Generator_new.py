#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Randomized DAG Generator
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################
import re
import math
import copy
import datetime
import numpy as np
import pandas as pd
import networkx as nx

from z3 import *
from itertools import combinations
from random import random, sample, uniform, randint


def DAG_Feature_Input(address):
    with pd.ExcelFile(address) as data:
        all_sheet_names = data.sheet_names
        DAG_Feature_list = []
        for DAG_ID in all_sheet_names:
            df = pd.read_excel(data, DAG_ID, index_col=None, na_values=["NA"])
            DAG_Feature_list.append(np.array(df))
    return DAG_Feature_list


def Algorithm_input(Algorithm, Algorithm_param_dict):
    dag_list = []
    if Algorithm == 'FLOW':
        dag_list = __gen_flow_new(Algorithm_param_dict)
    elif Algorithm == 'FLOW_S':
        dag_list = __gen_flow_single(Algorithm_param_dict)
    else:
        pass
    return dag_list


# #### DAG generator FLOW 算法  #### #
def __gen_flow_single(Algorithm_param_dict):
    Flow_set = Algorithm_param_dict['Flow_set']
    flow_num = Algorithm_param_dict['flow_num']
    arrival_interval = Algorithm_param_dict['arrival_interval']
    WCET_interval_max = Algorithm_param_dict['WCET_interval']
    DAG_num = Algorithm_param_dict['DAG_Num']
    ret_DAGs_list = []
    for DAG_num_id in range(DAG_num):
        temp_flow_set = [copy.deepcopy(sample(Flow_set, 1)[0]) for _ in range(flow_num)]
        temp_dag, source_node_num, sink_node_num = DPC.DAG_list_merge(temp_flow_set)
        DFA.dag_critical_path_new(temp_dag)
        DPC.Priority_Config('SELF', [temp_dag])
        for node_x in temp_dag.nodes(data=True):
            node_x[1]['DAG'].nodes[node_x[1]['Node_Index']]['Prio'] = node_x[1]['Prio']
        for temp_flow_x in temp_flow_set:
            max_level = max([nx[1]['rank'] for nx in temp_flow_x.nodes(data=True)])
            random_level = math.ceil( uniform(1, max_level) ) - 1
            temp_flow_x.graph['Arrive_time'] = float(uniform(arrival_interval[0], arrival_interval[1]))
            for nx in temp_flow_x.nodes(data=True):
                if nx[1]['Node_ID'] == 'start' or nx[1]['Node_ID'] == 'end':
                    nx[1]['AET'] = 0
                else:
                    nx[1]['AET'] = int((1 + uniform(-WCET_interval_max, WCET_interval_max)) * nx[1]['WCET'])
            s_rank_nodes_list = [nx[0] for nx in temp_flow_x.nodes(data=True) if nx[1]['rank'] > random_level and nx[1]['Node_ID'] != 'end']
            for srn in s_rank_nodes_list:
                temp_flow_x.remove_node(srn)
            end_node_s = [nx[0] for nx in temp_flow_x.nodes(data=True) if nx[1]['Node_ID'] == 'end'][0]
            n_succnode_s = [nxx for nxx in temp_flow_x.nodes() if (nxx != end_node_s) and (len(list(temp_flow_x.successors(nxx))) == 0)]
            for nss in n_succnode_s:
                temp_flow_x.add_edge(nss, end_node_s)
            branch_node_id_list = list(set([tfnx[1]['Node_ID'] for tfnx in temp_flow_x.nodes(data=True) if tfnx[1]['C_Node'] == True]))
            for bnode_id_x in branch_node_id_list:
                temp_bnode_list = [tbnx for tbnx in temp_flow_x.nodes(data=True) if tbnx[1]['Node_ID'] == bnode_id_x]
                for n_nodex in sample(temp_bnode_list, randint(0, len(temp_bnode_list)-1)):
                    temp_flow_x.remove_node(n_nodex[0])
        ret_DAGs_list.append(temp_flow_set)
    return ret_DAGs_list




    # todo DAG——生成方法（2）利用excel表格数据生成DAG 每个sheet一个DAG
    # def User_DAG_Inject(self, address):
    #     with pd.ExcelFile(address) as data:
    #         all_sheet_names = data.sheet_names
    #         DAG_dict = {}
    #         for DAG_ID in all_sheet_names:
    #             temp_DAG = nx.DiGraph()
    #             temp_DAG.graph['DAG_ID'] = DAG_ID
    #             df = pd.read_excel(data, DAG_ID, index_col=None, na_values=["NA"])
    #             title_list = df.dtypes
    #             for row in df.index:
    #                 temp_DAG.add_node(df.loc[row]['Node_Index'], DAG_ID=DAG_ID, Status="Block")
    #                 for title_id, data_type in title_list.items():
    #                     row_data = df.loc[row][title_id]
    #                     if title_id == 'Edges_List':
    #                         if type(row_data) == float:
    #                             continue
    #                         row_data = row_data.split(';')
    #                         for edge_data in row_data:
    #                             edge_list = edge_data[1:-1].split(',')
    #                             temp_DAG.add_edge(int(edge_list[0]), int(edge_list[1]))
    #                     else:
    #                         temp_DAG.nodes[df.loc[row]['Node_Index']][title_id] = row_data
    #             DAG_dict[DAG_ID] = temp_DAG
    #     return DAG_dict
    #

# #### DAG generator FLOW 算法  #### #
def __gen_flow_new(Algorithm_param_dict):
    Flow_set = Algorithm_param_dict['Flow_set']                         # []
    flow_num = Algorithm_param_dict['flow_num']                         # 1~10
    arrival_interval = Algorithm_param_dict['arrival_interval']         # [0, 20 * 2260]
    WCET_interval_max = Algorithm_param_dict['WCET_interval']           # [0, 0.1]
    DAG_num = Algorithm_param_dict['DAG_Num']
    ret_DAG_list = []
    for dag_id in range(DAG_num):
        temp_flow_set = [copy.deepcopy(sample(Flow_set, 1)[0]) for _ in range(flow_num)]  # 随机抽取（可重复）flow_num个流
        for temp_flow_x in temp_flow_set:
            max_level = max([nx[1]['rank'] for nx in temp_flow_x.nodes(data=True)])
            random_level = math.ceil( uniform(1, max_level) ) - 1
            # print(f"flow:{temp_flow_x.graph['DAG_ID']},max_level:{max_level},rand_level{random_level}")
            for nx in temp_flow_x.nodes(data=True):
                # (1) 初始化起始时间_ok
                if nx[1]['Node_ID'] == 'start':
                    nx[1]['AET'] = int(uniform(arrival_interval[0], arrival_interval[1]))
                # (1) 初始化截止时间_ok
                elif nx[1]['Node_ID'] == 'end':
                    nx[1]['AET'] = 0
                # (2) 随机执行时间波动;
                else:
                    nx[1]['AET'] = int((1 + uniform(-WCET_interval_max, WCET_interval_max)) * nx[1]['WCET'])
            # (3) 层数变化_大于random的为0
            s_rank_nodes_list = [nx[0] for nx in temp_flow_x.nodes(data=True) if nx[1]['rank'] > random_level and nx[1]['Node_ID'] != 'end']
            for srn in s_rank_nodes_list:
                temp_flow_x.remove_node(srn)
            # (3) 无后继结点与end连接
            end_node_s = [nx[0] for nx in temp_flow_x.nodes(data=True) if nx[1]['Node_ID'] == 'end'][0]
            n_succnode_s = [nxx for nxx in temp_flow_x.nodes() if (nxx != end_node_s) and (len(list(temp_flow_x.successors(nxx))) == 0)]
            for nss in n_succnode_s:
                temp_flow_x.add_edge(nss, end_node_s)
            # (4) 分支数量波动
            branch_node_id_list = list(set([tfnx[1]['Node_ID'] for tfnx in temp_flow_x.nodes(data=True) if tfnx[1]['C_Node'] == True]))
            for bnode_id_x in branch_node_id_list:
                temp_bnode_list = [tbnx for tbnx in temp_flow_x.nodes(data=True) if tbnx[1]['Node_ID'] == bnode_id_x]
                for n_nodex in sample(temp_bnode_list, randint(0, len(temp_bnode_list)-1)):
                    temp_flow_x.remove_node(n_nodex[0])   # 随机抽0, len(temp_bnode_list)
        temp_dag, source_node_num, sink_node_num = DPC.DAG_list_merge(temp_flow_set)
        for node_x in temp_dag.nodes(data=True):
            node_x[1]['WCET_old'] = node_x[1]['WCET']
        ret_DAG_list.append(temp_dag)
    return ret_DAG_list

import graphviz
import DAG_Generator as DG
import matplotlib.pyplot as plt     # plt 用于显示图片
import matplotlib.image as mpimg    # mpimg 用于读取图片
import sys
sys.path.append("..")
from Data_Output import DAG_Data_Processing as DDP
from DAG_Configurator import DAG_Priority_Config as DPC
from DAG_Configurator import DAG_WCET_Config as DWC
from DAG_Configurator import DAG_Features_Analysis as DFA
# from ..Data_Output import DAG_Data_Processing as DDP
# from ..DAG_Configurator import DAG_WCET_Config as DWC
# from ..DAG_Configurator import DAG_Priority_Config as DPC
# from ..DAG_Configurator import DAG_Features_Analysis as DFA

if __name__ == "__main__":
    Data_Output_Addr = "D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\test\\"
    Algorithm_Type = 'ERDOS_GNP'

    All_DAG_list = DG.Algorithm_input(Algorithm_Type, {'Node_Num': 10, 'Edge_Pro': 0.8, 'DAG_Num': 10 })
    print(len(All_DAG_list))
    for dag_id, dag_x in enumerate(All_DAG_list):
        print(type(All_DAG_list))
        print(dag_x)
        DWC.WCET_Config(dag_x, 'Uniform', True, 1, 100)     # (1) 配置 DAG的 WCET
        DFA.dag_data_initial(dag_x, dag_id, dag_id, 0)
        DFA.dag_param_critical_update(dag_x)                # (2) 配置DAG的关键参数
        DPC.Priority_Config('SELF', dag_x)                  # (3) 配置DAG的优先级

    addr_x  =  Data_Output_Addr + Algorithm_Type + "\\"
    DDP.Exam_Data_Output(All_DAG_list, 'ALL', addr_x)

    for dag_id, dag_x in enumerate(All_DAG_list):
        test_png = mpimg.imread(addr_x + f"{dag_x.graph['DAG_ID']}.png")  # 读取png
        plt.figure(figsize=(25, 10), dpi=80)
        ax = plt.gca()                           # 获取图形坐标轴
        ax.set_axis_off()                        # 去掉坐标
        ax.imshow(test_png)                  # 读取生成的图片
        plt.show()
        # plt.plot()
        # plt.close()
        # plt.draw()    将重新绘制图形。这允许您在交互模式下工作，如果您更改了数据或格式，则允许图形本身更改。
        # plt.savefig('./img/pic-{}.png'.format(epoch + 1))
        # plt.pause(1)