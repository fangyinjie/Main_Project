#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Core config
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################
import sys
import time
import copy
import math
import random
import pandas as pd
import networkx as nx
import graphviz as gz
import matplotlib.pyplot as plt     # plt 用于显示图片
import matplotlib.image as mpimg    # mpimg 用于读取图片


sys.path.append('D:\\github\\Main_Project\\DAG Generator And Simulator\\')
for pathx in sys.path:
    print(pathx)

from Src.DAG_Scheduler import *
from Src.DAG_Generator import DAG_Generator as DG
from Src.Data_Output import DAG_Data_Processing as DDP
from Src.Data_Output import Simulation_Result_Show as SRS
from Src.DAG_Configurator import DAG_Priority_Config as DPC
from Src.DAG_Configurator import DAG_WCET_Config as DWC
from Src.DAG_Configurator import DAG_Features_Analysis as DFA
from Src.DAG_Scheduler import Core
from Src.DAG_Scheduler import Scheduling_Simulator as SS
from Src.DAG_Scheduler import Light_Scheduling_Simulator as LSS

Root_Addr = "D:\\github\\Exam_Data\\Output_data\\"                                        # 根地址
Data_Output_Addr = "D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\test\\Exam_8_7\\"  # 输出地址
Data_Input_flow_Addr = "D:\\github\\Exam_Data\\Input_data\\Exam_Input_data\\original_data\\DAG_Data_flow_new.xlsx"    # flow data
# Data_Input_huawei_Addr = "D:\\github\\Exam_Data\\Input_data\\Exam_Input_data\\original_data\\HUAWEI_Single.xlsx"      # huawei dag

Data_Input_huawei_Addr = 'D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\PT_data\\new.xlsx'

TTL = 1130000
core_num = 30
Period = TTL  # / 5000
cycle = 1
dag_num = 10

def exam_pic_show(dag_x, title):
    dot = gz.Digraph()
    dot.attr(rankdir='LR')
    for node_x in dag_x.nodes(data=True):
        temp_label = 'Node_ID:{0}\nPrio:{1}\nWCET:{2}\nPT:{3}'.format(str(node_x[0]), str(node_x[1]['Prio']), str(node_x[1]['WCET']), str(node_x[1]['PT']))
        dot.node('%s' % node_x[0], temp_label, color='black')
    for edge_x in dag_x.edges():
        dot.edge('%s' % edge_x[0], '%s' % edge_x[1])
    dot.view('./pic_test/' + title)


def random_PT_dag_list(dag_list, sample_num):
    dag_node_num = len([node_x for dag_x in dag_list  for node_x in dag_x.nodes()])   # 初始化100组
    ret_dag_list = [[1, 1, 1, copy.deepcopy(dag_list)] for _ in range(sample_num)]    # (1) cri 1 (2) makespan (3) dag_list
    for ret_dag_x in ret_dag_list:
        random_sample_x = list(range(dag_node_num))
        random.shuffle(random_sample_x)
        # print(random_sample_x)
        for tdag_x in ret_dag_x[3]:
            for node_x in tdag_x.nodes(data=True):
                node_x[1]['PT'] = random_sample_x.pop(0)  # 为true则可以抢占
    return ret_dag_list


# (1) 生成新的种群成员
def random_PT_dag_list_new(dag_list, source_dag_list, sample_num):
    ret_dag_list = [[1, 1, 1, copy.deepcopy(dag_list)] for _ in range(sample_num)]
    for ret_dag_data in ret_dag_list:
        for source_dag_x in source_dag_list:
            node_pt_list = list(range(source_dag_x.number_of_nodes()))
            random.shuffle(node_pt_list)
            for dag_x in ret_dag_data[3]:
                node_pt_listx = copy.deepcopy(node_pt_list)
                if dag_x.graph['Criticality'] == source_dag_x.graph['Criticality']:
                    for node_x in dag_x.nodes(data=True):
                        # node_x[1]['PT'] = dag_x.graph['Criticality']
                        # node_x[1]['PT'] = 3 - dag_x.graph['Criticality']
                        node_x[1]['PT'] = node_pt_listx.pop(0)
    return ret_dag_list


# (2) 成员随机变异
def random_PT_dag_list_mutation(dag_list_list):
    ret_dag_list = copy.deepcopy(dag_list_list)
    for dag_list in ret_dag_list:
        for dag_x in dag_list[3]:
            for node_x in dag_x.nodes(data=True):
                if random.random() > 0.8:
                    node_x[1]['PT'] = random.randint(0, dag_x.number_of_nodes())  # 为true则可以抢占
    return ret_dag_list


# (3) 成员随机交叉
def random_PT_dag_list_cross(dag_list_list, dag_list, target_dag_list, sample_num):
    test_ret_dag_list = random_PT_dag_list_new(dag_list, target_dag_list, sample_num)
    for test_ret_dag_x in test_ret_dag_list:
        tpt_list1 = [node_x[1]['PT'] for dag_x in random.choice(dag_list_list)[3] for node_x in dag_x.nodes(data=True)]
        tpt_list2 = [node_x[1]['PT'] for dag_x in random.choice(dag_list_list)[3] for node_x in dag_x.nodes(data=True)]
        random_sample_x = [random.choice([tpt_list1[nx], tpt_list2[nx]]) for nx in range(len(tpt_list1))]
        for tdag_x in test_ret_dag_x[3]:
            for node_x in tdag_x.nodes(data=True):
                node_x[1]['PT'] = random_sample_x.pop(0)  # 为true则可以抢占
        return test_ret_dag_list


def PT_abstract(dag_data_list):
    ret_PT_list = []
    for dag_data_id, dag_data_x in enumerate(dag_data_list):
        cri_list = list(set(dag_x.graph['Criticality'] for dag_x in dag_data_x[3]))
        temp_pt_dict = {}
        for cri_x in cri_list:
            cx_dag = [dag_x for dag_x in dag_data_x[3] if dag_x.graph['Criticality'] == cri_x][0]
            cx_pt_dict = {node_x[0]: node_x[1]['PT'] for node_x in cx_dag.nodes(data=True)}
            temp_pt_dict[cri_x] = cx_pt_dict
        ret_PT_list.append(temp_pt_dict)
    return ret_PT_list

def PT_transmit(PT_list, exam_dag_list):
    ret_dag_list = []
    for PT_x in PT_list:
        exam_dag_list_x = [1, 1, 1, copy.deepcopy(exam_dag_list)]
        for edag_x in exam_dag_list_x[3]:
            edag_x_cri = edag_x.graph['Criticality']
            for node_x in edag_x.nodes(data=True):
                node_x[1]['PT'] = PT_x[edag_x_cri][node_x[0]]
        ret_dag_list.append(exam_dag_list_x)
    return ret_dag_list


if __name__ == "__main__":
    HW_DAG = DG.Manual_Input('XLSX', [Data_Input_huawei_Addr])
    jitter_rate = 0.5
    All_DAG_listx = []
    exam_dl = [0, 1]
    for dag_cri, dag_id in enumerate(exam_dl):
        DFA.dag_data_initial(HW_DAG[dag_id], DAGType=int(dag_cri)+ 1, DAG_id=int(dag_cri)+ 1, Period=Period, Critic=dag_cri + 1, Cycle=cycle)  # (2.1) 配置DAG的初始参数
        DFA.dag_param_critical_update(HW_DAG[dag_id])
        All_DAG_listx.append( copy.deepcopy(HW_DAG[dag_id]) )
    # (1) P AND NP
    All_DAG_list = []
    for dag_x in All_DAG_listx:
        Cx_DAG_list = [copy.deepcopy(dag_x) for _ in range(dag_num)]
        DPC.MDAG_Priority_Config('SELF', Cx_DAG_list)
        All_DAG_list += Cx_DAG_list

    # (2) 运行
    ret_dict = {}
    for exam_num in range(100):
        exam_data_dict = {}

        Preempt_type_dict = {'NP': False, 'P': 'type1', 'PT1':'type5_1', 'PT2':'type5_2', 'PT3':'type5_3'
                                                      , 'PT6':'type6'}
        exam_dag_list = copy.deepcopy(All_DAG_list)
        # 动态！！！
        for dag_x in exam_dag_list:
            for node_x in dag_x.nodes(data=True):
                node_x[1]['WCET'] = int((1 + random.uniform(-jitter_rate, jitter_rate)) * node_x[1]['WCET'])
            DFA.dag_param_critical_update(dag_x)

        print(f'exam_num:{exam_num}:', end='\t')
        show_data_dict = {}
        for type_name, Preempt_type in Preempt_type_dict.items():
            Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(exam_dag_list), {'Core_Num': core_num,
                                                                                 'Total_Time': Period * cycle * 2,
                                                                                 'Enqueue_rank': False,
                                                                                 'Priority_rank': True,
                                                                                 'Preempt_type': Preempt_type,
                                                                                 'Dynamic': False}])
            Dispatcher.run()
            SELF_NP_h = Dispatcher.Core_Data_List
            print(f'{type_name}:', end='  ')
            print(f'MAKESPAN:\t{Core.ret_makespan(SELF_NP_h)}', end=',\t')
            print(f'C1:\t{Core.ret_dag_cri_makespan(SELF_NP_h, 1)}', end=',\t')
            print(f'C2:\t{Core.ret_dag_cri_makespan(SELF_NP_h, 2)}', end=',\t')
            # print(f'M_import:\t{Core.ret_dag_cri_makespan(SELF_NP_h, 2)}', end=',\t')

            exam_data_dict[f'{type_name}_MAKESPAN'] = Core.ret_makespan(SELF_NP_h)
            exam_data_dict[f'{type_name}_C1'] = Core.ret_dag_cri_makespan(SELF_NP_h, 1)
            exam_data_dict[f'{type_name}_C2'] = Core.ret_dag_cri_makespan(SELF_NP_h, 2)
            show_data_dict[f'{type_name}'] = SELF_NP_h
            # show_data_dict[exam_num] = SELF_NP_h
        print('')
        ret_dict[exam_num] = exam_data_dict

        # # 如果高关键任务性能不降反增，则展示结果；
        # if exam_data_dict['P_C2'] < exam_data_dict['PT_C2']:
        #     print('\nttttt\n')
        #     SRS.show_core_data_list(show_data_dict,
        #                             'Show', '',
        #                             # Data_Output_Addr,'Save',
        #                             copy.deepcopy([exam_dag_list[0], exam_dag_list[1]]), Period, cycle)
    # print(ret_dict)
    df = pd.DataFrame(ret_dict).T
    df.to_csv(f'./9-21_data_jitter_{jitter_rate * 100}_01.csv')
    # for dag_x in DAG_list:
        # DFA.dag_param_critical_update(HW_DAG[dag_id])
    # 初始化并加优先级
    #
    # (3) 信息采集
