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
core_num = 48
Period = TTL # / 5000
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

    DFA.dag_data_initial(HW_DAG[1], DAGType=int(1), DAG_id=int(1), Period=Period, Critic=1)  # (2.1) 配置DAG的初始参数
    DFA.dag_data_initial(HW_DAG[5], DAGType=int(2), DAG_id=int(2), Period=Period, Critic=2)  # (2.1) 配置DAG的初始参数

    All_DAG_list = [copy.deepcopy(HW_DAG[1]) for _ in range(dag_num)] + [copy.deepcopy(HW_DAG[5]) for _ in range(dag_num)]

    for dag_id, dag_x in enumerate(All_DAG_list):
        DFA.dag_data_initial(dag_x, DAGType=int(dag_x.graph['DAGTypeID']), DAG_id=int(dag_x.graph['DAGTypeID']), Period=Period, Critic=dag_x.graph['Criticality'])  # (2.1) 配置DAG的初始参数
        DFA.dag_param_critical_update(dag_x)                                    # (2.2) 配置DAG的关键参数
    DPC.MDAG_Priority_Config('SELF', All_DAG_list)

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

    # (1) False 非抢占模式
    # (2) type1 全抢占模式
    # (3) type2 纯5%保障模式
    # (4) type3_1:  纯5%保障单边阈值
    # (5) type3_2:  纯5%保障双边阈值
    # (6) type4_1:  无5%保障单边阈值
    # (7) type4_2:  无5%保障双边阈值
    # (8) type6:    无5%保障优先级阈值
    Preempt_type_list = [False, 'type1', 'type2', 'type3_1', 'type3_2', 'type4_1', 'type4_2', 'type6']
    # Preempt_type_list = []
    ret_dict = {}
    for Preempt_type in Preempt_type_list:
        Dispatcher = SS.Dispatcher_Workspace(
            [copy.deepcopy(All_DAG_list), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                                           'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': Preempt_type,
                                           'Dynamic': False}])
        Dispatcher.run()
        SELF_NP_h = Dispatcher.Core_Data_List
        print(f'{Preempt_type}_MAKESPAN:{Core.ret_makespan(SELF_NP_h)}', end='\t\t')
        print(f'{Preempt_type}_MAKESPAN_cri_1:{Core.ret_dag_cri_makespan(SELF_NP_h, 1)}', end='\t\t')
        print(f'{Preempt_type}_MAKESPAN_cri_2:{Core.ret_dag_cri_makespan(SELF_NP_h, 2)}', end='\t\t')
        print(f'surpass rade:{100 * (Core.ret_dag_cri_makespan(SELF_NP_h, 1) - min_makespan) / min_makespan}', end='\t\t')
        print()
        if Preempt_type:
            ret_dict[Preempt_type] = SELF_NP_h
        else:
            ret_dict['NP'] = SELF_NP_h
    # """
    # （1）智能搜索单边
    # (1) 智能搜索样本初始化
    dag_node_num = len([node_x for dag_x in All_DAG_list  for node_x in dag_x.nodes()])
    ret_dag_list = random_PT_dag_list_new(All_DAG_list, 100)
    for train_x in range(10):  # 10次迭代搜索：
        print(f'*******************************************train start__{train_x}!')
        for sample_list_id, sample_list in enumerate(ret_dag_list):
            Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(sample_list[3]), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                           'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type4_1', 'Dynamic': False}])

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
            print(f'surpass rade:{100 * (sample_list[0] - min_makespan) / min_makespan}')
        ret_dag_list = list(filter(lambda x: x[0] <= 1.05 * min_makespan, ret_dag_list))
        if len(ret_dag_list) < 10:
            ret_dag_list += random_PT_dag_list_new(All_DAG_list, 100 - len(ret_dag_list))
            continue
        else:
            ret_dag_list.sort(key=lambda x: x[0], reverse=False)
            ret_dag_list.sort(key=lambda x: x[2], reverse=False)
            ret_dag_list = ret_dag_list[:10]  # 留下10个最好的样本

        ret_dag_list += random_PT_dag_list_cross(copy.deepcopy(ret_dag_list), All_DAG_list, 70)        # 交叉 80组
        ret_dag_list += random_PT_dag_list_mutation(random.sample(ret_dag_list, 10))                   # 变异 10组
        ret_dag_list += random_PT_dag_list_new(All_DAG_list, 10)                                       # 外来 10组

    ret_dag_list.sort(key=lambda x: x[0], reverse=False)
    ret_dag_list.sort(key=lambda x: x[2], reverse=False)
    ret_dag_x = ret_dag_list.pop(0)
    ret_dict['typeZS1'] = ret_dag_x[3]

    Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(ret_dag_x[3]), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2, 'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type4_1', 'Dynamic': False}])
    Dispatcher.run()
    ret_h = Dispatcher.Core_Data_List
    print(f'*******************************************')
    for dag_x in ret_dag_x[3]:
        print(f'{[node_x[1]["PT"] for node_x in dag_x.nodes(data=True)]}')
    print(f'*******************************************')
    print(f'ret_h_MAKESPAN_c1:{Core.ret_dag_cri_makespan(ret_h, 1)}', end='\t')
    print(f'ret_h_MAKESPAN_c2:{Core.ret_dag_cri_makespan(ret_h, 2)}', end='\t')
    print(f'ret_h_MAKESPAN:{Core.ret_makespan(ret_h)}', end='\t')
    print(f'surpass rade:{100 * (Core.ret_dag_cri_makespan(ret_h, 1) - min_makespan) / min_makespan}')
    # （2）智能搜索双边
    dag_node_num = len([node_x for dag_x in All_DAG_list  for node_x in dag_x.nodes()])
    ret_dag_list = random_PT_dag_list_new(All_DAG_list, 100)
    for train_x in range(15):  # 10次迭代搜索：
        print(f'*******************************************train start__{train_x}!')
        for sample_list_id, sample_list in enumerate(ret_dag_list):
            Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(sample_list[3]), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2, 'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type4_2', 'Dynamic': False}])
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
            print(f'surpass rade:{100 * (sample_list[0] - min_makespan) / min_makespan}')
        ret_dag_list = list(filter(lambda x: x[0] <= 1.05 * min_makespan, ret_dag_list))
        if len(ret_dag_list) < 10:
            ret_dag_list += random_PT_dag_list_new(All_DAG_list, 100 - len(ret_dag_list))
            continue
        else:
            ret_dag_list.sort(key=lambda x: x[0], reverse=False)
            ret_dag_list.sort(key=lambda x: x[2], reverse=False)
            ret_dag_list = ret_dag_list[:10]  # 留下10个最好的样本
        ret_dag_list += random_PT_dag_list_cross(copy.deepcopy(ret_dag_list), All_DAG_list, 70)     # 交叉 80组
        ret_dag_list += random_PT_dag_list_mutation(random.sample(ret_dag_list, 10))                # 变异 10组
        ret_dag_list += random_PT_dag_list_new(All_DAG_list, 10)                                    # 外来 10组
    ret_dag_list.sort(key=lambda x: x[0], reverse=False)
    ret_dag_list.sort(key=lambda x: x[2], reverse=False)
    ret_dag_x = ret_dag_list.pop(0)
    ret_dict['typeZS2'] = ret_dag_x[3]
    Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(ret_dag_x[3]), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2, 'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type4_2', 'Dynamic': False}])
    Dispatcher.run()
    ret_h = Dispatcher.Core_Data_List
    print(f'*******************************************')
    for dag_x in ret_dag_x[3]:
        print(f'{[node_x[1]["PT"] for node_x in dag_x.nodes(data=True)]}')
    print(f'*******************************************')
    print(f'ret_h_MAKESPAN_c1:{Core.ret_dag_cri_makespan(ret_h, 1)}', end='\t')
    print(f'ret_h_MAKESPAN_c2:{Core.ret_dag_cri_makespan(ret_h, 2)}', end='\t')
    print(f'ret_h_MAKESPAN:{Core.ret_makespan(ret_h)}', end='\t')
    print(f'surpass rade:{100 * (Core.ret_dag_cri_makespan(ret_h, 1) - min_makespan) / min_makespan}')
    # """
    """
    Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(ret_dag_x), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                                      'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type9', 'Dynamic': False}])
    Dispatcher.run()
    ret_h = Dispatcher.Core_Data_List
    ret_h_MDATA = Core.ret_makespan(ret_h)
    ret_h_MDATA_C1 = Core.ret_dag_cri_makespan(ret_h, 1)
    ret_h_MDATA_C2 = Core.ret_dag_cri_makespan(ret_h, 2)
    # print('***********************************')
    # print(f'{[node_x[1]["PT"] for dag_x in ret_dag_x for node_x in dag_x.nodes(data=True)]}')
    print(f'ret_MAKESPAN:{ret_h_MDATA}', end='\t\t')
    print(f'ret_MAKESPAN_cri_1:{ret_h_MDATA_C1}', end='\t\t')
    print(f'ret_MAKESPAN_cri_2:{ret_h_MDATA_C2}', end='\t\t')
    print(f'surpass rade:{100 * (ret_h_MDATA_C1 - min_makespan) / min_makespan}')


    for dag_x in ret_dag_x:
        print(f'DAG_ID:{dag_x.graph["DAG_ID"]}')
        print(f'{[node_x[1]["PT"] for node_x in dag_x.nodes(data=True)]}')
        exam_pic_show(dag_x, str(dag_x.graph['DAG_ID']))     # 展示图片
    """
    for ret_key, ret_value in ret_dict.items():
        SRS.show_core_data_list({ret_key:ret_value},
                                'Show', '',
                                # Data_Output_Addr,'Save',
                                copy.deepcopy([HW_DAG[1], HW_DAG[5]]), Period, cycle)
