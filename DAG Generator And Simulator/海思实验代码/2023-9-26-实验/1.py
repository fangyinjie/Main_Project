#!/usr/bin/python3
# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # #
# Create Time: 2023/9/261:31
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
# # # # # # # # # # # # # # # #
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
import numpy as  np

Root_Addr = "D:\\github\\Exam_Data\\Output_data\\"                                        # 根地址
Data_Output_Addr = "D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\test\\Exam_8_7\\"  # 输出地址
Data_Input_flow_Addr = "D:\\github\\Exam_Data\\Input_data\\Exam_Input_data\\original_data\\DAG_Data_flow_new.xlsx"    # flow data
# Data_Input_huawei_Addr = "D:\\github\\Exam_Data\\Input_data\\Exam_Input_data\\original_data\\HUAWEI_Single.xlsx"      # huawei dag

Data_Input_huawei_Addr = 'D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\PT_data\\new.xlsx'

TTL         = 1130000
core_num    = 30
Period      = TTL  # / 5000
cycle       = 1
dag_num     = 10


if __name__ == "__main__":
    # DAG 1 X DAG 2
    HW_DAG = DG.Manual_Input('XLSX', [Data_Input_huawei_Addr])
    DAG_1_num       = HW_DAG[0].number_of_nodes()
    DAG_2_num       = HW_DAG[1].number_of_nodes()
    # a5 = np.array(ones((3,3)), ndmin=0, dtype=float)
    a5 = np.ones([DAG_1_num, DAG_2_num]).astype(bool)
    print(a5)
    print(a5[14][13])
    # print(a5)
    jitter_rate     = 0.5
    All_DAG_listx   = []
    exam_dl         = [0, 1]
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
    df.to_csv(f'./9-21_data_jitter_{jitter_rate * 100}_00.csv')
    # for dag_x in DAG_list:
        # DFA.dag_param_critical_update(HW_DAG[dag_id])
    # 初始化并加优先级
    #
    # (3) 信息采集

    pass