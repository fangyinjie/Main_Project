#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Core config
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################

import time
import copy
import networkx as nx
import matplotlib.pyplot as plt     # plt 用于显示图片
import matplotlib.image as mpimg    # mpimg 用于读取图片

from Src.DAG_Scheduler import *
from Src.DAG_Generator import DAG_Generator as DG
from Src.Data_Output import DAG_Data_Processing as DDP
from Src.DAG_Configurator import DAG_Priority_Config as DPC
from Src.DAG_Configurator import DAG_WCET_Config as DWC
from Src.DAG_Scheduler import Scheduling_Simulator as SS
from Src.DAG_Scheduler import Core
from Src.DAG_Configurator import DAG_Features_Analysis as DFA
from Src.Data_Output import Simulation_Result_Show as SRS


Root_Addr = "D:\\github\\Exam_Data\\Output_data\\"                              # 根地址
Data_Output_Addr = "D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\test\\"  # 输出地址
Data_Input_flow_Addr = "D:\\github\\Exam_Data\\Input_data\\Exam_Input_data\\original_data\\DAG_Data_flow_new.xlsx"        # flow data
Data_Input_huawei_Addr = "D:\\github\\Exam_Data\\Input_data\\Exam_Input_data\\original_data\\HUAWEI_Single.xlsx"        # huawei dag

# DAG_list_Mine = DG.Algorithm_input('MINE', {'DAG_Num': 3, 'Node_Num': 37, 'Critic_Path': 7, 'Width': 15, 'Jump_level': 1, 'Conn_ratio': 0.08859, 'Max_Shape': 15, 'Min_Shape': 1, 'Max_in_degree': 15, 'Max_out_degree': 5})
DAG_list_GNP = DG.Algorithm_input('ERDOS_GNP', {'Node_Num': 10, 'Edge_Pro': 0.5, 'DAG_Num': 3})
# DAG_list_GNM = DG.Algorithm_input('ERDOS_GNM', {'Node_Num': 10, 'Edge_Num': 18, 'DAG_Num': 3 })
All_DAG_list = DAG_list_GNP

TTL = 1130000
core_num = 3
Total_Time = TTL/500
Period = Total_Time/3

for dag_id, dag_x in enumerate(All_DAG_list):
    DWC.WCET_Config(dag_x, 'Uniform', False, 20, 50)
    DFA.dag_data_initial(dag_x, DAGType=int(dag_id), DAG_id=int(dag_id), Period=Period, Cycle=3, Critic=int(dag_id))

    DFA.dag_param_critical_update(dag_x)
    DPC.Priority_Config('SELF', dag_x)

Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(All_DAG_list), {'Core_Num': core_num, 'Total_Time': Total_Time * (4),
                            'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': False, 'Dynamic': False}])
Dispatcher.run()

SELF_h = Dispatcher.Core_Data_List
makespan = Core.ret_makespan(SELF_h)
workload_rade = 100 * sum([DFA.get_dag_volume(dag_x) for dag_x in All_DAG_list]) / sum([core_x.get_core_last_time() for core_id, core_x in SELF_h.items()])

print(f'makespan:{makespan}')
print(f'workload_rade:{workload_rade}')
SRS.show_core_data_list({'dag': SELF_h}, 'Show', '', copy.deepcopy(All_DAG_list), Period)
