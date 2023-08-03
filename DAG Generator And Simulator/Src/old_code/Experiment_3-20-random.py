#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Core config
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################

import copy
import random
import networkx as nx
import pandas as pd
import simpy
import matplotlib.pyplot as plt
import sys

import Scheduler.Core as Core
import Scheduler.DAG_Generator as DG
import Scheduler.DAG_Features_Analysis as DFA
import Scheduler.DAG_Priority_Config as DPC
import Scheduler.Scheduling_Simulator as SS
import Scheduler._scheduler_optimal_2 as SOPT
# import Simulation_Result_Show as SRS
# import limited_priority_assign as PP_lpa

TTL = 1130000

# DAG_ID_list = ["M1_S2_C1", "M1_S2_C2", "M2_S2_C1"]
# All_DAG_list = [dag_x for dag_x in All_DAG_list if dag_x.graph['DAG_ID'] in DAG_ID_list]


if __name__ == "__main__":
    # (1) Environment parameter configuration
    Total_Time = 3 * TTL
    # (2) DAG generation
    root_addr = 'D:/github/DAG_Scheduling_Summary/Exam_Input_data/xlsx_data/wireless/DAG_Data.xlsx'
    All_DAG_list = DG.Manual_Input('XLSX', [root_addr])  # 单source，单sink
    # (3) Critical Paramter：
    for dag_x in All_DAG_list:
        DFA.dag_param_critical_update(dag_x, dag_x.graph['DAG_ID'], Total_Time)
        for node_x in dag_x.nodes(data=True):
            node_x[1]['WCET'] = int(node_x[1]['WCET'])

    core_num_dict = {"M1_S1_C1": 2, "M1_S2_C1": 3, "M1_S1_C2": 2, "M1_S2_C2": 3,
                     "M2_S1_C1": 2, "M2_S2_C1": 3, "M2_S1_C2": 2, "M2_S2_C2": 3,
                     "M2_S3_C1": 5, "M2_S3_C2": 5}

    DAG_ID_list = ["M2_S3_C1"]
    Test_DAG = [dag_x for dag_x in All_DAG_list if dag_x.graph['DAG_ID'] in DAG_ID_list].pop(0)

    # 1) FIFO 调度
    Ret_Core_FIFO_Data_List = []
    for _ in range(10000):
        param_l = [copy.deepcopy([Test_DAG]), {'Core_Num': core_num_dict[Test_DAG.graph['DAG_ID']],
                                               "Total_Time": Total_Time, 'Enqueue_rank': False, 'Priority_rank': False, 'PE': False, 'Dynamic': False}]
        Dispatcher = SS.Dispatcher_Workspace(param_l)
        Dispatcher.run()
        Ret_Core_FIFO_Data_List.append(Dispatcher.Core_Data_List)
    Ret_Core_FIFO_Data = min(Ret_Core_FIFO_Data_List, key=lambda x: Core.ret_makespan(x))
    print(Core.ret_makespan(Ret_Core_FIFO_Data))
    Core.Core_Data_CSV_Output(Ret_Core_FIFO_Data, './opt/', 'FIFO', Test_DAG.graph['DAG_ID'])  # (1) 华为实验结果

    # (3.1) SELF_静态分析优先级;
    temp_dag_x = copy.deepcopy(Test_DAG)
    DFA.dag_param_critical_update(temp_dag_x, temp_dag_x.graph['DAG_ID'], Total_Time)
    DPC.Priority_Config("SELF", [temp_dag_x])
    param_l = [copy.deepcopy([temp_dag_x]), {'Core_Num': core_num_dict[Test_DAG.graph['DAG_ID']],
                                             "Total_Time": Total_Time, 'Enqueue_rank': False, 'Priority_rank': True, 'PE': False, 'Dynamic': False}]
    Dispatcher = SS.Dispatcher_Workspace(param_l)
    Dispatcher.run()
    Ret_Core_SELF_S_Data = Dispatcher.Core_Data_List
    SELF_S_Makespan = Core.ret_makespan(Ret_Core_SELF_S_Data)
    print( SELF_S_Makespan )

    # 1) 最优调度算法
    # param_l = [copy.deepcopy(dag_x), {'Core_Num': core_num_dict[dag_x.graph['DAG_ID']]}]
    # Ret_Core_OPT_Data = SOPT.Dispatcher_Workspace(param_l)
    # OPT_MakeSpan = Core.ret_makespan(Ret_Core_OPT_Data)
    # print(f'OPT_MakeSpan:{OPT_MakeSpan}')
    # Core.Core_Data_Output(Ret_Core_OPT_Data, './ret/', 'opt', dag_x.graph['DAG_ID'])
    # print('improve_rate:{0:.2f}'.format(opt_improve_rate))

