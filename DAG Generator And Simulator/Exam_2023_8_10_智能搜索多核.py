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


# (1) 生成新的种群成员
def random_PT_dag_list_new(dag_list, sample_num):
    ret_dag_list = [[1, 1, 1, copy.deepcopy(dag_list)] for _ in range(sample_num)]    # (1) cri 1 (2) makespan (3) dag_list
    for ret_dag_x in ret_dag_list:
        for tdag_x in ret_dag_x[3]:
            for node_x in tdag_x.nodes(data=True):
                node_x[1]['PT'] = random.randint(0, tdag_x.number_of_nodes() * 10)  # 为true则可以抢占
    return ret_dag_list

# (2) 成员随机变异
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
        # (2.1) 配置DAG的初始参数
        DFA.dag_data_initial(dag_x, DAGType=int(dag_x.graph['DAGTypeID']), DAG_id=int(dag_x.graph['DAGTypeID']), Period=Period, Critic=dag_x.graph['Criticality'])
        # (2.2) 配置DAG的关键参数
        DFA.dag_param_critical_update(dag_x)
    DPC.MDAG_Priority_Config('SELF', All_DAG_list)
    # (3)抢占阈值设置
    for dag_x in All_DAG_list:
        for node_x in dag_x.nodes(data=True):
            node_x[1]['PT'] = node_x[1]['Prio']

    HI_DAG_list = [dag_x for dag_x in All_DAG_list if dag_x.graph['Criticality'] == 1]
    LO_DAG_list = [dag_x for dag_x in All_DAG_list if dag_x.graph['Criticality'] == 2]

    DPC.MDAG_Priority_Config('SELF', HI_DAG_list)
    DPC.MDAG_Priority_Config('SELF', LO_DAG_list)

    for core_num in range(20 , 150):
        # (1) 全抢占             'type1',
        min_makespan = Core.ret_makespan(LSS.Test_simulator_test(DPC.DAG_list_merge(copy.deepcopy(HI_DAG_list)), core_num)) - 2  # 去掉合并后头尾的1
        print(f'core_num:{core_num}, min_makespan:{min_makespan}', end=',')

        Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(All_DAG_list), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                               'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type1', 'Dynamic': False}])
        Dispatcher.run()
        SELF_P_h = Dispatcher.Core_Data_List
        p_c1 = Core.ret_dag_cri_makespan(SELF_P_h, 1)
        p_c2 = Core.ret_dag_cri_makespan(SELF_P_h, 2)
        p_m  = Core.ret_makespan(SELF_P_h)
        print(f'P_MAKESPAN_c1:{p_c1}', end=',')
        print(f'P_MAKESPAN_c2:{p_c2}', end=',')
        print(f'P_MAKESPAN:{p_m}', end=',')
        # (2) 智能单边, 无5%；    'type4_1',
        simple_num = 40
        ret_dag_list = random_PT_dag_list_new(All_DAG_list, simple_num)
        for train_x in range(10):
            for sample_list_id, sample_list in enumerate(ret_dag_list):
                Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(sample_list[3]), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                              'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type4_1', 'Dynamic': False}])
                Dispatcher.run()
                ret_h = Dispatcher.Core_Data_List
                sample_list[2] = Core.ret_makespan(ret_h)
                sample_list[1] = Core.ret_dag_cri_makespan(ret_h, 2)
                sample_list[0] = Core.ret_dag_cri_makespan(ret_h, 1)

                # print(f'sample_list_id:{sample_list_id}', end='\t')
                # print(f'MAKESPAN_c1:{sample_list[0]}', end='\t')
                # print(f'MAKESPAN_c2:{sample_list[1]}', end='\t')
                # print(f'MAKESPAN:{sample_list[2]}', end='\t')
                # print(f'c1_surpass:{100 * (sample_list[0] - min_makespan) / min_makespan}', end='\t')
                # print(f'makespan_improve:{100 * (p_m - sample_list[2]) / p_m}')

            ret_dag_list = list(filter(lambda x: x[0] <= 1.05 * min_makespan, ret_dag_list))
            if len(ret_dag_list) < 5:
                ret_dag_list += random_PT_dag_list_new(All_DAG_list, simple_num - len(ret_dag_list))
                continue
            else:
                ret_dag_list.sort(key=lambda x: x[0], reverse=False)
                ret_dag_list.sort(key=lambda x: x[2], reverse=False)
                if len(list(set([ret_dag_x[2] for ret_dag_x in ret_dag_list]))) < 2:
                    break
                ret_dag_list = ret_dag_list[:5]  # 留下10个最好的样本

            ret_dag_list += random_PT_dag_list_cross(copy.deepcopy(ret_dag_list), All_DAG_list, 25)  # 交叉 80组
            ret_dag_list += random_PT_dag_list_mutation(random.sample(ret_dag_list, 5))  # 变异 10组
            ret_dag_list += random_PT_dag_list_new(All_DAG_list, 5)  # 外来 10组

        ret_dag_list.sort(key=lambda x: x[0], reverse=False)
        ret_dag_list.sort(key=lambda x: x[2], reverse=False)
        ret_dag_x = ret_dag_list.pop(0)
        Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(ret_dag_x[3]),{'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                       'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type4_1', 'Dynamic': False}])
        Dispatcher.run()
        ret_h = Dispatcher.Core_Data_List
        print(f'type4_1_MAKESPAN_c1:{Core.ret_dag_cri_makespan(ret_h, 1)}', end=',')
        print(f'type4_1_MAKESPAN_c2:{Core.ret_dag_cri_makespan(ret_h, 2)}', end=',')
        print(f'type4_1_MAKESPAN:{Core.ret_makespan(ret_h)}', end=',')
        print(f'type4_1_C1_surpass:{100 * (Core.ret_dag_cri_makespan(ret_h, 1) - min_makespan) / min_makespan}', end=',')
        print(f'type4_1_m_improve:{100 * (p_m - Core.ret_makespan(ret_h)) / p_m}', end=',')

        # (2) 智能双边, 无5%；    'type4_2'
        ret_dag_list = random_PT_dag_list_new(All_DAG_list, simple_num)
        for train_x in range(40):  # 10次迭代搜索：
            for sample_list_id, sample_list in enumerate(ret_dag_list):
                Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(sample_list[3]), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                               'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type4_2', 'Dynamic': False}])
                Dispatcher.run()
                ret_h = Dispatcher.Core_Data_List
                sample_list[2] = Core.ret_makespan(ret_h)
                sample_list[1] = Core.ret_dag_cri_makespan(ret_h, 2)
                sample_list[0] = Core.ret_dag_cri_makespan(ret_h, 1)

                # print(f'sample_list_id:{sample_list_id}', end='\t')
                # print(f'MAKESPAN_c1:{sample_list[0]}', end='\t')
                # print(f'MAKESPAN_c2:{sample_list[1]}', end='\t')
                # print(f'MAKESPAN:{sample_list[2]}', end='\t')
                # print(f'c1_surpass:{100 * (sample_list[0] - min_makespan) / min_makespan}', end='\t')
                # print(f'makespan_improve:{100 * (p_m - sample_list[2]) / p_m}')

            ret_dag_list = list(filter(lambda x: x[0] <= 1.05 * min_makespan, ret_dag_list))
            if len(ret_dag_list) < 10:
                ret_dag_list += random_PT_dag_list_new(All_DAG_list, simple_num - len(ret_dag_list))
                continue
            else:
                if len(list(set([ret_dag_x[2] for ret_dag_x in ret_dag_list]))) < 2:
                    break
                ret_dag_list.sort(key=lambda x: x[0], reverse=False)
                ret_dag_list.sort(key=lambda x: x[2], reverse=False)
                ret_dag_list = ret_dag_list[:10]
            ret_dag_list += random_PT_dag_list_cross(copy.deepcopy(ret_dag_list), All_DAG_list, 25)  # 交叉 80组
            ret_dag_list += random_PT_dag_list_mutation(random.sample(ret_dag_list, 5))  # 变异 10组
            ret_dag_list += random_PT_dag_list_new(All_DAG_list, 5)  # 外来 10组
        ret_dag_list.sort(key=lambda x: x[0], reverse=False)
        ret_dag_list.sort(key=lambda x: x[2], reverse=False)
        ret_dag_x = ret_dag_list.pop(0)
        Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(ret_dag_x[3]),{'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                           'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type4_2', 'Dynamic': False}])
        Dispatcher.run()
        ret_h = Dispatcher.Core_Data_List
        print(f'type4_2_MAKESPAN_c1:{Core.ret_dag_cri_makespan(ret_h, 1)}', end=',')
        print(f'type4_2_MAKESPAN_c2:{Core.ret_dag_cri_makespan(ret_h, 2)}', end=',')
        print(f'type4_2_MAKESPAN:{Core.ret_makespan(ret_h)}', end=',')
        print(f'type4_2_C1_surpass:{100 * (Core.ret_dag_cri_makespan(ret_h, 1) - min_makespan) / min_makespan}', end=',')
        print(f'type4_2_m_improve:{100 * (p_m - Core.ret_makespan(ret_h)) / p_m}')

