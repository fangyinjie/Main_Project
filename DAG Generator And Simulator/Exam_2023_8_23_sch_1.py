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
import graphviz as gz
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
core_num = 40
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
# def random_PT_dag_list_new(dag_list, sample_num):
#     ret_dag_list = [[1, 1, 1, copy.deepcopy(dag_list)] for _ in range(sample_num)]    # (1) cri 1 (2) makespan (3) dag_list
#     for ret_dag_x in ret_dag_list:
#         for tdag_x in ret_dag_x[3]:
#             node_num_x = sum([ldag_x.number_of_nodes() for ldag_x in dag_list if dag_x.graph['Criticality'] == tdag_x.graph['Criticality']])
#             for node_x in tdag_x.nodes(data=True):
#                 node_x[1]['PT'] = random.randint(0, node_num_x)  # 为true则可以抢占
#     return ret_dag_list

def random_PT_dag_list_new(dag_list, sample_num):
    ret_dag_list = [[1, 1, 1, copy.deepcopy(dag_list)] for _ in range(sample_num)]    # (1) cri 1 (2) makespan (3) dag_list
    for ret_dag_x in ret_dag_list:
        for tdag_x in ret_dag_x[3]:
            for node_x in tdag_x.nodes(data=True):
                node_x[1]['PT'] = random.randint(0, tdag_x.number_of_nodes() * 10)  # 为true则可以抢占
    return ret_dag_list

# (2) 成员随机变异
# def random_PT_dag_list_mutation(dag_list_list):
#     for dag_list in dag_list_list:
#         for dag_x in dag_list:
#             node_num_x = sum([ldag_x.number_of_nodes() for ldag_x in dag_list if dag_x.graph['Criticality'] == dag_x.graph['Criticality']])
#             for node_x in dag_x.nodes(data=True):
#                 if random.random() > 0.8:
#                     node_x[1]['PT'] = random.randint(0, node_num_x)  # 为true则可以抢占
#     return dag_list_list
def random_PT_dag_list_mutation(dag_list_list):
    ret_dag_list = copy.deepcopy(dag_list_list)
    for dag_list in ret_dag_list:
        for dag_x in dag_list[3]:
            for node_x in dag_x.nodes(data=True):
                if random.random() > 0.8:
                    node_x[1]['PT'] = random.randint(0, dag_x.number_of_nodes() * 10 )  # 为true则可以抢占
    return ret_dag_list

# (3) 成员随机交叉
def random_PT_dag_list_cross(dag_list_list, target_dag_list, sample_num):
    test_ret_dag_list = random_PT_dag_list_new(target_dag_list, sample_num)
    for test_ret_dag_x in test_ret_dag_list:
        tpt_list1 = [node_x[1]['PT'] for dag_x in random.choice(dag_list_list)[3] for node_x in dag_x.nodes(data=True)]
        tpt_list2 = [node_x[1]['PT'] for dag_x in random.choice(dag_list_list)[3] for node_x in dag_x.nodes(data=True)]
        random_sample_x = [random.choice([tpt_list1[nx], tpt_list2[nx]]) for nx in range(len(tpt_list1))]
        for tdag_x in test_ret_dag_x[3]:
            for node_x in tdag_x.nodes(data=True):
                node_x[1]['PT'] = random_sample_x.pop(0)  # 为true则可以抢占
        return test_ret_dag_list



if __name__ == "__main__":
    HW_DAG = DG.Manual_Input('XLSX', [Data_Input_huawei_Addr])

    dag_id_list = [1, 5]
    for dag_cri, dag_id in enumerate(dag_id_list):
        DFA.dag_data_initial(HW_DAG[dag_id], DAGType=int(dag_cri)+ 1, DAG_id=int(dag_cri)+ 1, Period=Period, Critic=dag_cri + 1, Cycle=cycle)  # (2.1) 配置DAG的初始参数
        DFA.dag_param_critical_update(HW_DAG[dag_id])
    DPC.MDAG_Priority_Config('SELF', [HW_DAG[dag_id] for dag_id in dag_id_list])
    for dag_x in [HW_DAG[dag_id] for dag_id in dag_id_list]:
        for node_x in dag_x.nodes(data=True):
            node_x[1]['PT'] = node_x[1]['Prio']

    All_DAG_list = [copy.deepcopy(HW_DAG[dag_id])  for dag_id in dag_id_list for _ in  range(dag_num)]

    for dag_x in All_DAG_list:
        DFA.dag_data_initial(dag_x, DAGType=int(dag_x.graph['DAGTypeID']), DAG_id=int(dag_x.graph['DAGTypeID']), Period=Period, Critic=dag_x.graph['Criticality'], Cycle=cycle)
        # (2.1) 配置DAG的初始参数
        DFA.dag_param_critical_update(dag_x)
        # (2.2) 配置DAG的关键参数
    # DPC.MDAG_Priority_Config('SELF', All_DAG_list)

    # 抢占阈值赋予
    # for dag_x in All_DAG_list:
    #     for node_x in dag_x.nodes(data=True):
    #         node_x[1]['PT'] = node_x[1]['Prio']
    # All_DAG_list = [copy.deepcopy(HW_DAG[1]) for _ in range(dag_num)] + [copy.deepcopy(HW_DAG[5]) for _ in range(dag_num)]
    HI_DAG_list = [dag_x for dag_x in All_DAG_list if dag_x.graph['Criticality'] == 1]
    LO_DAG_list = [dag_x for dag_x in All_DAG_list if dag_x.graph['Criticality'] == 2]

    DPC.MDAG_Priority_Config('SELF', HI_DAG_list)
    DPC.MDAG_Priority_Config('SELF', LO_DAG_list)
    for dag_x in All_DAG_list:
        for node_x in dag_x.nodes(data=True):
            node_x[1]['PT'] = node_x[1]['Prio']
    print(f'core_num:{core_num}')

    ret_dict = {}
    # Preempt_type_dict = {'NP':False, 'P':'type1', 'HIP':'type2', 'HIP_SPT':'type3_1', 'HIP_MPT':'type3_2', 'NHP_SPT':'type4_1', 'NHP_MPT':'type4_2'}
    # Preempt_type_dict = {'NP':False, 'P':'type1', 'SPT':'type4_1', 'MPT':'type4_2'}
    Preempt_type_dict = {'NP':False,
                         'P':'type1',
                         # 'SPT':'type4_1'
                         }
    for type_name, Preempt_type in Preempt_type_dict.items():
        Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(All_DAG_list), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                                   'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': Preempt_type, 'Dynamic': False}])
        Dispatcher.run()
        SELF_NP_h = Dispatcher.Core_Data_List
        # print(f'{type_name}_MAKESPAN:{Core.ret_makespan(SELF_NP_h)}', end=',')
        # print(f'{type_name}_MAKESPAN_cri_1:{Core.ret_dag_cri_makespan(SELF_NP_h, 1)}', end=',')
        # print(f'{type_name}_MAKESPAN_cri_2:{Core.ret_dag_cri_makespan(SELF_NP_h, 2)}', end=',\t\t,')
        # print()
        for cycle_x in range(cycle):
            print(f'{type_name}_MAKESPAN:{Core.ret_dag_DAG_NUM_makespan(SELF_NP_h, cycle_x)}', end=',')
            print(f'{type_name}_MAKESPAN_cri_1:{Core.ret_dag_CRI_DAG_NUM_makespan(SELF_NP_h, 1, cycle_x)}', end=',')
            print(f'{type_name}_MAKESPAN_cri_2:{Core.ret_dag_CRI_DAG_NUM_makespan(SELF_NP_h, 2, cycle_x)}')
        ret_dict[type_name] = SELF_NP_h
        # print(f'surpass rade:{100 * (Core.ret_dag_cri_makespan(SELF_NP_h, 1) - min_makespan) / min_makespan}')
        # ret_dict['m'][type_name] = Core.ret_makespan(SELF_NP_h)
        # ret_dict['c1'][type_name] = Core.ret_dag_cri_makespan(SELF_NP_h, 1)
        # ret_dict['c2'][type_name] = Core.ret_dag_cri_makespan(SELF_NP_h, 2)
    print()
    # """
    # （1）智能搜索单边
    # (1) 智能搜索样本初始化
    Preempt_type = 'type4_1'
    min_makespan = Core.ret_makespan(LSS.Test_simulator_test(DPC.DAG_list_merge(copy.deepcopy(HI_DAG_list)), core_num)) - 2
    for dag_x in  All_DAG_list:
        for node_x in dag_x.nodes(data=True):
            dag_x.graph['block'] = min_makespan

    dag_node_num = len([node_x for dag_x in All_DAG_list  for node_x in dag_x.nodes()])

    cyclye_num = 100
    ret_dag_list = random_PT_dag_list_new(All_DAG_list, cyclye_num)
    for train_x in range(cyclye_num):  # 10次迭代搜索：
        for sample_list_id, sample_list in enumerate(ret_dag_list):
            Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(sample_list[3]), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                           'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': Preempt_type, 'Dynamic': False}])
            Dispatcher.run()
            ret_h = Dispatcher.Core_Data_List
            sample_list[2] = Core.ret_makespan(ret_h)
            sample_list[1] = Core.ret_dag_cri_makespan(ret_h, 2)
            sample_list[0] = Core.ret_dag_cri_makespan(ret_h, 1)

            # print(f'{[node_x[1]["PT"] for dag_x in sample_list[3] for node_x in dag_x.nodes(data=True)]}')
            print(f'sample_list_id:{sample_list_id}', end='\t')
            print(f'ret_h_MAKESPAN_c1:{sample_list[0]}', end='\t')
            print(f'ret_h_MAKESPAN_c2:{sample_list[1]}', end='\t')
            print(f'ret_h_MAKESPAN:{sample_list[2]}', end='\t')
            print(f'C1_SAT:{100 * (sample_list[0] - min_makespan) / min_makespan}')
        ret_dag_list = list(filter(lambda x: x[0] <= 1.05 * min_makespan, ret_dag_list))
        if len(ret_dag_list) < 10:
            ret_dag_list += random_PT_dag_list_new(All_DAG_list, 100 - len(ret_dag_list))
            continue
        else:
            ret_dag_list.sort(key=lambda x: x[0], reverse=False)
            ret_dag_list.sort(key=lambda x: x[2], reverse=False)
            ret_dag_list = ret_dag_list[:math.ceil(0.15 * cyclye_num)]  # 留下10个最好的样本

        ret_dag_list += random_PT_dag_list_cross(copy.deepcopy(ret_dag_list), All_DAG_list, math.ceil(0.55 * cyclye_num))       # 交叉 80组
        ret_dag_list += random_PT_dag_list_mutation(random.sample(ret_dag_list, math.ceil(0.15 * cyclye_num)))                   # 变异 10组
        ret_dag_list += random_PT_dag_list_new(All_DAG_list, math.ceil(0.15 * cyclye_num))                                       # 外来 10组

    ret_dag_list.sort(key=lambda x: x[0], reverse=False)
    ret_dag_list.sort(key=lambda x: x[2], reverse=False)
    ret_dag_x = ret_dag_list.pop(0)[3]

    cycle = 1
    for dag_x in ret_dag_x:
            dag_x.graph['Cycle'] = cycle

    Dispatcher = SS.Dispatcher_Workspace(
        [copy.deepcopy(ret_dag_x), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                                       'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': Preempt_type,
                                       'Dynamic': False}])
    Dispatcher.run()
    SELF_NP_h = Dispatcher.Core_Data_List
    # print(f'{type_name}_MAKESPAN:{Core.ret_makespan(SELF_NP_h)}', end=',')
    # print(f'{type_name}_MAKESPAN_cri_1:{Core.ret_dag_cri_makespan(SELF_NP_h, 1)}', end=',')
    # print(f'{type_name}_MAKESPAN_cri_2:{Core.ret_dag_cri_makespan(SELF_NP_h, 2)}', end=',\t\t,')
    # print()
    for cycle_x in range(cycle):
        print(f'Type_GA_MAKESPAN:{Core.ret_dag_DAG_NUM_makespan(SELF_NP_h, cycle_x)}', end=',')
        print(f'Type_GA_MAKESPAN_cri_1:{Core.ret_dag_CRI_DAG_NUM_makespan(SELF_NP_h, 1, cycle_x)}', end=',')
        print(f'Type_GA_MAKESPAN_cri_2:{Core.ret_dag_CRI_DAG_NUM_makespan(SELF_NP_h, 2, cycle_x)}')
    ret_dict['Type_GA'] = SELF_NP_h
    hi_dag_list = [dag_x for dag_x in ret_dag_x if dag_x.graph['Criticality'] == 1]
    lo_dag_list = [dag_x for dag_x in ret_dag_x if dag_x.graph['Criticality'] == 2]
    for dag_id, dag_x in enumerate(hi_dag_list):
        dag_x.graph['DAG_ID'] = f'1_{dag_id}'
    for dag_id, dag_x in enumerate(lo_dag_list):
        dag_x.graph['DAG_ID'] = f'2_{dag_id}'
    DDP.Exam_Data_Output(ret_dag_x, 'ALL', Data_Output_Addr + '2023_8_23_EXAM\\')

    for ret_key, ret_value in ret_dict.items():
        SRS.show_core_data_list({ret_key:ret_value},
                                'Show', '',
                                # Data_Output_Addr,'Save',
                                copy.deepcopy([HW_DAG[1], HW_DAG[5]]), Period, cycle)
