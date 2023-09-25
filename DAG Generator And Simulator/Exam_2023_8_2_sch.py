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
from Src.DAG_Scheduler import Light_Scheduling_Simulator as LSS
from Src.DAG_Scheduler import Core
from Src.DAG_Configurator import DAG_Features_Analysis as DFA
from Src.Data_Output import Simulation_Result_Show as SRS


Root_Addr = "D:\\github\\Exam_Data\\Output_data\\"                                        # 根地址
Data_Output_Addr = "D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\test\\Exam_8_7\\"  # 输出地址
Data_Input_flow_Addr = "D:\\github\\Exam_Data\\Input_data\\Exam_Input_data\\original_data\\DAG_Data_flow_new.xlsx"    # flow data
Data_Input_huawei_Addr = "D:\\github\\Exam_Data\\Input_data\\Exam_Input_data\\original_data\\HUAWEI_Single.xlsx"      # huawei dag

# DAG_list_Mine = DG.Algorithm_input('MINE', {'DAG_Num': 3, 'Node_Num': 37, 'Critic_Path': 7, 'Width': 15, 'Jump_level': 1, 'Conn_ratio': 0.08859, 'Max_Shape': 15, 'Min_Shape': 1, 'Max_in_degree': 15, 'Max_out_degree': 5})
DAG_list_GNP = DG.Algorithm_input('ERDOS_GNP', {'Node_Num': 10, 'Edge_Pro': 0.5, 'DAG_Num': 3})
# DAG_list_GNM = DG.Algorithm_input('ERDOS_GNM', {'Node_Num': 10, 'Edge_Num': 18, 'DAG_Num': 3 })
All_DAG_list = DAG_list_GNP


# 8-8 单DAG复现
# All_flow_list = DG.Manual_Input('XLSX', [Data_Input_huawei_Addr])
# tar_dags = [All_flow_list[1], All_flow_list[5]]

TTL = 1130000
core_num = 5
Period = TTL / 5000
cycle = 3
# Total_Time = TTL/500
# Period = Total_Time/3

for dag_id, dag_x in enumerate(All_DAG_list):
# for dag_id, dag_x in enumerate(tar_dags):
    DWC.WCET_Config(dag_x, 'Uniform', False, 20, 50)
    DFA.dag_data_initial(dag_x, DAGType=int(dag_id), DAG_id=int(dag_id), Period=Period, Cycle=cycle, Critic=int(dag_id) + 1)
    DFA.dag_param_critical_update(dag_x)
    DPC.Priority_Config('SELF', dag_x)

# DDP.Exam_Data_Output(All_DAG_list, 'ALL', Data_Output_Addr)
# for dag_id, dag_x in enumerate(All_DAG_list):
#     test_png = mpimg.imread(Data_Output_Addr + f"{dag_x.graph['DAG_ID']}.png")  # 读取png
#     print(f"DAG_ID:{dag_x.graph['DAG_ID']}")
#     plt.figure(figsize=(25, 10), dpi=80)
#     ax = plt.gca()       # 获取图形坐标轴
#     ax.set_axis_off()    # 去掉坐标
#     ax.imshow(test_png)  # 读取生成的图片
#     plt.draw()           # 将重新绘制图形。这允许您在交互模式下工作，如果您更改了数据或格式，则允许图形本身更改。
#     plt.show()           # plt.pause(0) # plt.close()


# ############### (1) SELF_NP ############### #
Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(All_DAG_list), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                            'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': False, 'Dynamic': False}])
Dispatcher.run()
SELF_NP_h = Dispatcher.Core_Data_List
SELF_NP_MDATA = Core.ret_makespan(SELF_NP_h)
# SELF_NP_MDATA_C1 = Core.ret_dag_cri_makespan(SELF_NP_h, 1)
# SELF_NP_MDATA_C2 = Core.ret_dag_cri_makespan(SELF_NP_h, 2)


print(f'SELF_NP_MAKESPAN:{SELF_NP_MDATA}', end='\t')
print()
# print(f'SELF_NP_MAKESPAN_cri_1:{SELF_NP_MDATA_C1}', end='\t')
# print(f'SELF_NP_MAKESPAN_cri_2:{SELF_NP_MDATA_C2}', end='\t')
# print(f'cri_1 surpass rade:{100 * (SELF_NP_MDATA_C1 - min_makespan) / SELF_NP_MDATA_C1}')


# ############## (2) SELF_P  typ4 纯保障############### #
Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(All_DAG_list), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                            'Enqueue_rank': False,'Priority_rank': True, 'Preempt_type': 'type1', 'Dynamic': False}])
Dispatcher.run()

SELF_P_h = Dispatcher.Core_Data_List
SELF_P_MDATA = Core.ret_makespan(SELF_P_h)
# SELF_P_MDATA_C1 = Core.ret_dag_cri_makespan(SELF_P_h, 1)
# SELF_P_MDATA_C2 = Core.ret_dag_cri_makespan(SELF_P_h, 2)

print(f'SELF_P_MAKESPAN:{SELF_P_MDATA}', end='\t')
print()
# print(f'SELF_P_MAKESPAN_cri_1:{SELF_P_MDATA_C1}', end='\t')
# print(f'SELF_P_MAKESPAN_cri_2:{SELF_P_MDATA_C2}', end='\t')
# print(f'cri_1 surpass rade:{100 * (SELF_P_MDATA_C1 - min_makespan) / SELF_P_MDATA_C1}')

# (3.3) type （1） 5%有限抢测试；
# Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(All_DAG_list), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
#                             'Enqueue_rank': False,'Priority_rank': True, 'Preempt_type': 'type1', 'Dynamic': False}])
Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(All_DAG_list), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                            'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type4', 'Dynamic': False}])
Dispatcher.run()

SELF_LP1_h = Dispatcher.Core_Data_List
SELF_LP1_MDATA = Core.ret_makespan(SELF_LP1_h)
# SELF_LP1_MDATA_C1 = Core.ret_dag_cri_makespan(SELF_LP1_h, 1)
# SELF_LP1_MDATA_C2 = Core.ret_dag_cri_makespan(SELF_LP1_h, 2)

print(f'SELF_lP1_MAKESPAN:{SELF_LP1_MDATA}', end='\t')
print()
# print(f'SELF_lP1_MAKESPAN_cri_1:{SELF_LP1_MDATA_C1}', end='\t')
# print(f'SELF_lP1_MAKESPAN_cri_2:{SELF_LP1_MDATA_C2}', end='\t')
# print(f'cri_1 surpass rade:{100 * (SELF_LP1_MDATA_C1 - min_makespan) / SELF_LP1_MDATA_C2}')
"""
# (3.3) type （1） 无5%有限抢测试；阈值抢占
Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(All_DAG_list), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                            'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type2', 'Dynamic': False}])
Dispatcher.run()

SELF_LP2_h = Dispatcher.Core_Data_List
SELF_LP2_MDATA = Core.ret_makespan(SELF_LP2_h)
# SELF_LP2_MDATA_C1 = Core.ret_dag_cri_makespan(SELF_LP2_h, 1)
# SELF_LP2_MDATA_C2 = Core.ret_dag_cri_makespan(SELF_LP2_h, 2)

print(f'SELF_lP2_MAKESPAN:{SELF_LP2_MDATA}', end='\t')
print()
# print(f'SELF_lP2_MAKESPAN_cri_1:{SELF_LP2_MDATA_C1}', end='\t')
# print(f'SELF_lP2_MAKESPAN_cri_2:{SELF_LP2_MDATA_C2}', end='\t')
# print(f'cri_1 surpass rade:{100 * (SELF_LP2_MDATA_C1 - min_makespan) / SELF_LP2_MDATA_C1}')


# (3.3) type （1） 无5%有限抢测试；阈值抢占
Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(All_DAG_list), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                            'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type5', 'Dynamic': False}])
Dispatcher.run()

SELF_LP5_h = Dispatcher.Core_Data_List
SELF_LP5_MDATA = Core.ret_makespan(SELF_LP5_h)
# SELF_LP5_MDATA_C1 = Core.ret_dag_cri_makespan(SELF_LP5_h, 1)
# SELF_LP5_MDATA_C2 = Core.ret_dag_cri_makespan(SELF_LP5_h, 2)

print(f'SELF_lP5_MAKESPAN:{SELF_LP5_MDATA}', end='\t')
print()
# print(f'SELF_lP5_MAKESPAN_cri_1:{SELF_LP5_MDATA_C1}', end='\t')
# print(f'SELF_lP5_MAKESPAN_cri_2:{SELF_LP5_MDATA_C2}', end='\t')
# print(f'cri_1 surpass rade:{100 * (SELF_LP5_MDATA_C1 - min_makespan) / SELF_LP5_MDATA_C1}')
# ############## SELF_LP-2 ############### #
"""
SRS.show_core_data_list({'SELF_NP': SELF_NP_h,
                         'SELF_P': SELF_P_h,
                         'SELF_LP1_h': SELF_LP1_h,
                         # 'SELF_LP2_h': SELF_LP2_h,
                         # 'SELF_LP5_h': SELF_LP5_h
                         },
                        'Show', '',
                        # Data_Output_Addr,'Save',
                        copy.deepcopy(All_DAG_list), Period, cycle)
# SRS.show_core_data_list({'NP': SELF_h, 'P': SELF_P_h}, 'Show', '', copy.deepcopy(All_DAG_list), Period, cycle)
# SRS.show_core_data_list({'NP': SELF_h, 'P': SELF_P_h}, 'Show', '', copy.deepcopy(All_DAG_list), Period)
