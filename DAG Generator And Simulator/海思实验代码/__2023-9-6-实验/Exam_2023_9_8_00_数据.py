#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Core config
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################

import os
import time
import copy
import math
import random
import pandas as pd
import networkx as nx
import graphviz as gz
import matplotlib.pyplot as plt     # plt 用于显示图片
import matplotlib.image as mpimg    # mpimg 用于读取图片


import sys
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
Data_Input_huawei_Addr = "D:\\github\\Exam_Data\\Input_data\\Exam_Input_data\\original_data\\HUAWEI_Single.xlsx"      # huawei dag
ct = 'D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\PT_data\\T.xlsx'
TTL = 1130000
core_num = 30
Period = TTL  # / 5000
cycle = 1
dag_num = 10


if __name__ == "__main__":
    # (1) 读数据
    base_dir = 'D:\github\Exam_Data\Output_data\DAG_Generator\PT_data'
    # ct = 'D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\PT_data\\new.xlsx'
    ct = 'D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\PT_data\\new00-1.xlsx'
    # c1 = 'D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\PT_data\\1.xlsx'
    # c2 = 'D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\PT_data\\2.xlsx'
    # files = [os.path.join(base_dir, file) for file in os.listdir(base_dir)]
    Source_dag_list = DG.Manual_Input('XLSX', [ct])
    All_DAG_list = []
    for s_dag_x in Source_dag_list:
        cri_dag_list = []
        for dag_id in range(dag_num):
            dag_id = int(s_dag_x.graph['DAG_ID'])
            ss_dag_x = copy.deepcopy(s_dag_x)
            DFA.dag_data_initial(ss_dag_x, DAGType=dag_id, DAG_id=dag_id, Period=Period, Critic=int(s_dag_x.graph['DAG_ID']), Cycle=1)
            DFA.dag_param_critical_update(ss_dag_x)
            cri_dag_list.append(ss_dag_x)
        DPC.MDAG_Priority_Config('SELF', cri_dag_list)
        All_DAG_list += cri_dag_list

    # (2) 运行
    exam_num = 0
    ret_dict = {}
    Preempt_type_dict = {'NP': False, 'P': 'type1', 'PT': 'type4_2'}
    for jitter_rate in [0.1, 0.3, 0.5]:
        for _ in range(1000):
            exam_num += 1
            exam_data_dict = {}

            exam_dag_list = copy.deepcopy(All_DAG_list)
            # 动态！！！
            for dag_x in exam_dag_list:
                for node_x in dag_x.nodes(data=True):
                    node_x[1]['WCET'] = int((1 + random.uniform(-jitter_rate, jitter_rate)) * node_x[1]['WCET'])
            print(f'exam_num:{exam_num}:', end='\t')
            # PT_list = {f"{dag_x.graph['Criticality']}_{dag_x.graph['DAG_ID']}": {node_x[0]:node_x[1]['PT'] for node_x in dag_x.nodes(data=True)} for dag_x in exam_dag_list}
            # for dag_x in exam_dag_list:
            #     print(f"{dag_x.graph['Criticality']}_{dag_x.graph['DAG_ID']}")
            #     for node_x in dag_x.nodes(data=True):
            #         print(f"node{node_x[0]}:{node_x[1]['PT']}")
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
                print(f'M_import:\t{Core.ret_dag_cri_makespan(SELF_NP_h, 2)}', end=',\t')

                exam_data_dict[f'{type_name}_MAKESPAN'] = Core.ret_makespan(SELF_NP_h)
                exam_data_dict[f'{type_name}_C1'] = Core.ret_dag_cri_makespan(SELF_NP_h, 1)
                exam_data_dict[f'{type_name}_C2'] = Core.ret_dag_cri_makespan(SELF_NP_h, 2)
                # show_data_dict[f'{type_name}'] = SELF_NP_h
                # show_data_dict[exam_num] = SELF_NP_h
            exam_data_dict['jitter'] = str(jitter_rate)
            print('')
            ret_dict[exam_num] = exam_data_dict
            # # 如果高关键任务性能不降反增，则展示结果；
            # if exam_data_dict['P_C1'] > exam_data_dict['PT_C1']:
            #     print('\nttttt\n')
            #     SRS.show_core_data_list(show_data_dict,
            #                             'Show', '',
            #                             # Data_Output_Addr,'Save',
            #                             copy.deepcopy([exam_dag_list[0], exam_dag_list[1]]), Period, cycle)
    df = pd.DataFrame(ret_dict).T
    df.to_csv(f'./9-8_data_00.csv')
