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
import math
import random
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt     # plt 用于显示图片
import matplotlib.image as mpimg    # mpimg 用于读取图片

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

TTL = 1130000
core_num = 6
Period = TTL # / 5000
cycle = 1


if __name__ == "__main__":
    DAG_list_huawei = DG.Manual_Input('XLSX', [Data_Input_huawei_Addr])
    All_DAG_list = [copy.deepcopy(DAG_list_huawei[1]) for _ in range(1)] + [copy.deepcopy(DAG_list_huawei[5]) for _ in range(1)]

    for dag_id, dag_x in enumerate(All_DAG_list):
        DFA.dag_data_initial(dag_x, DAGType=int(dag_id), DAG_id=int(dag_id), Period=Period, Critic=dag_id + 1)  # (2.1) 配置DAG的初始参数
        DFA.dag_param_critical_update(dag_x)  # (2.2) 配置DAG的关键参数

    DPC.MDAG_Priority_Config('SELF', All_DAG_list)  # 合并赋予全优先级做阈值
    # 抢占阈值赋予
    for dag_x in All_DAG_list:
        for node_x in dag_x.nodes(data=True):
            node_x[1]['PT'] = node_x[1]['Prio']

    DPC.MDAG_Priority_Config('SELF', [dag_x for dag_x in All_DAG_list if dag_x.graph['Criticality'] == 1])
    DPC.MDAG_Priority_Config('SELF', [dag_x for dag_x in All_DAG_list if dag_x.graph['Criticality'] == 2])

    HI_DAG_list = [dag_x for dag_x in All_DAG_list if dag_x.graph['Criticality'] == 1]
    HI_DAG_list_M = DPC.DAG_list_merge(copy.deepcopy(HI_DAG_list))
    DFA.dag_data_initial(HI_DAG_list_M, DAGType=int(0), DAG_id=int(0), Period=Period, Critic=0)
    DFA.dag_param_critical_update(HI_DAG_list_M)
    DPC.Priority_Config('SELF', HI_DAG_list_M)
    min_makespan = Core.ret_makespan(LSS.Test_simulator_test(HI_DAG_list_M, core_num)) - 2  # 去掉合并后头尾的1
    for dag_x in HI_DAG_list:
        dag_x.graph['block'] = min_makespan
    print(min_makespan)

    # (1) 智能搜索样本初始化
    lo_dag_node_num = len(
        [node_x for dag_x in All_DAG_list if dag_x.graph['Criticality'] == 2 for node_x in dag_x.nodes()])
    random_sample_list = [list(range(lo_dag_node_num)) for _ in range(100)]
    ret_dag_list = []
    for random_sample_x in random_sample_list:
        random.shuffle(random_sample_x)
        print(random_sample_x)
        tdag_list = copy.deepcopy(All_DAG_list)
        tdag_list_lo = [dag_x for dag_x in All_DAG_list if dag_x.graph['Criticality'] == 2]
        for tdag_lo_x in tdag_list_lo:
            for node_x in tdag_lo_x.nodes(data=True):
                node_x[1]['PT'] = random_sample_x.pop(0)  # 为true则可以抢占
        ret_dag_list.append((1, 1, tdag_list))  # (1) cri 1 (2) makespan (3) dag_list


    for train_x in range(100):  # 10次迭代搜索：
        print(f'train start__{train_x}!')
        ret = []
        for c1, makespan, sample_list in ret_dag_list:
            Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(sample_list), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                           'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type5', 'Dynamic': False}])
            Dispatcher.run()
            ret_h = Dispatcher.Core_Data_List
            ret_h_MDATA = Core.ret_makespan(ret_h)
            ret_h_MDATA_C1 = Core.ret_dag_cri_makespan(ret_h, 1)
            ret_h_MDATA_C2 = Core.ret_dag_cri_makespan(ret_h, 2)
            tpt_list = [node_x[1]['PT'] for dag_x in sample_list if dag_x.graph['Criticality'] == 2 for node_x in dag_x.nodes(data=True)]

            print(f'{tpt_list}')
            print(f'ret_h_MAKESPAN:{ret_h_MDATA}', end='\t')
            print(f'ret_h_MAKESPAN_cri_1:{ret_h_MDATA_C1}', end='\t')
            print(f'ret_h_MAKESPAN_cri_2:{ret_h_MDATA_C2}', end='\t')
            print(f'surpass rade:{100 * (ret_h_MDATA_C1 - min_makespan) / min_makespan}')
            ret.append((ret_h_MDATA_C1, ret_h_MDATA, sample_list))
        retx = list(filter(lambda x: x[0] <= 1.05 * min_makespan, ret))
        if len(retx) < 1:
            ret_dag_list = []
            for random_sample_x in [list(range(lo_dag_node_num)) for _ in range(100)]:
                random.shuffle(random_sample_x)
                tdag_list = copy.deepcopy(All_DAG_list)
                tdag_list_lo = [dag_x for dag_x in All_DAG_list if dag_x.graph['Criticality'] == 2]
                for tdag_lo_x in tdag_list_lo:
                    for node_x in tdag_lo_x.nodes(data=True):
                        node_x[1]['PT'] = random_sample_x.pop(0)  # 为true则可以抢占
                ret_dag_list.append((1, 1, tdag_list))  # (1) cri 1 (2) makespan (3) dag_list
            continue
        else:
            retx.sort(key=lambda x: x[1], reverse=False)
            ret = retx[:10]

        # 交叉 7组
        for _ in range(80):
            tpt_list1 = [node_x[1]['PT'] for dag_x in random.choice(ret)[2] if dag_x.graph['Criticality'] == 2 for node_x in dag_x.nodes(data=True)]
            tpt_list2 = [node_x[1]['PT'] for dag_x in random.choice(ret)[2] if dag_x.graph['Criticality'] == 2 for node_x in dag_x.nodes(data=True)]
            random_sample_lox = [random.choice([tpt_list1[nx], tpt_list2[nx]]) for nx in range(lo_dag_node_num)]
            # eed = random.randint(0, lo_dag_node_num)
            # random_sample_lox = list(filter(lambda x: x >= eed, tpt_list1)) + list(filter(lambda x: x < eed, tpt_list2))
            tdag_list = copy.deepcopy(All_DAG_list)
            for tdag_x in tdag_list:
                if tdag_x.graph['Criticality'] == 2:
                    for node_x in tdag_x.nodes(data=True):
                        node_x[1]['PT'] = random_sample_lox.pop(0)  # 为true则可以抢占
            ret.append((1, 1, tdag_list))

        # 1组变异”
        for _ in range(10):
            lo_dag_node_num = len([node_x for dag_x in All_DAG_list if dag_x.graph['Criticality'] == 2 for node_x in dag_x.nodes()])
            random_sample_x = list(range(lo_dag_node_num))
            random.shuffle(random_sample_x)
            tdag_list = copy.deepcopy(All_DAG_list)
            tdag_list_lo = [dag_x for dag_x in All_DAG_list if dag_x.graph['Criticality'] == 2]
            for tdag_lo_x in tdag_list_lo:
                for node_x in tdag_lo_x.nodes(data=True):
                    node_x[1]['PT'] = random_sample_x.pop(0)  # 为true则可以抢占
            ret.append((1, 1, tdag_list))

        ret_dag_list = ret

    ret_dag_list.sort(key=lambda x: x[0], reverse=False)
    ret_dag_x = ret_dag_list.pop(0)[1]
    Dispatcher = SS.Dispatcher_Workspace(
        [copy.deepcopy(sample_list), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                                      'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type2',
                                      'Dynamic': False}])
    Dispatcher.run()
    ret_h = Dispatcher.Core_Data_List
    ret_h_MDATA = Core.ret_makespan(ret_h)
    ret_h_MDATA_C1 = Core.ret_dag_cri_makespan(ret_h, 1)
    ret_h_MDATA_C2 = Core.ret_dag_cri_makespan(ret_h, 2)
    print('***********************************')
    tpt_list = [node_x[1]['PT'] for dag_x in sample_list if dag_x.graph['Criticality'] == 2 for node_x in
                dag_x.nodes(data=True)]
    print(f'{tpt_list}')
    print(f'ret_MAKESPAN:{ret_h_MDATA}', end='\t')
    print(f'ret_MAKESPAN_cri_1:{ret_h_MDATA_C1}', end='\t')
    print(f'ret_MAKESPAN_cri_2:{ret_h_MDATA_C2}', end='\n')
    print(f'surpass rade:{100 * (ret_h_MDATA_C1 - min_makespan) / min_makespan}')
    展示图片
        # for dag_id in range(len(ct_dag_list)):
        #     for node_x in ct_dag_list[dag_id].nodes(data=True):
        #         node_x[1]['preemptable'] = random.choice([ret[0][dag_id].nodes[node_x[0]]['preemptable'],
        #                                                   ret[1][dag_id].nodes[node_x[0]][
        #                                                       'preemptable']])  # 为true则可以抢占
        #
        # ret.append(ct_dag_list)
        # 变异 1组

