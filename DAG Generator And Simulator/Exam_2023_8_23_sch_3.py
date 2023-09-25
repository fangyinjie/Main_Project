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



if __name__ == "__main__":
    print(f'core_num:{core_num}')
    HW_DAG = DG.Manual_Input('XLSX', [Data_Input_huawei_Addr])
    dag_id_list = [1, 5]
    jitter_rate = 0.5
    All_DAG_list = []
    for dag_cri, dag_id in enumerate(dag_id_list):
        DFA.dag_data_initial(HW_DAG[dag_id], DAGType=int(dag_cri)+ 1, DAG_id=int(dag_cri)+ 1, Period=Period, Critic=dag_cri + 1, Cycle=cycle)  # (2.1) 配置DAG的初始参数
        DFA.dag_param_critical_update(HW_DAG[dag_id])
        All_DAG_list.append( copy.deepcopy(HW_DAG[dag_id]) )

    for exam_num in range(1000):
        # (1) 实验DAG初始化；
        exam_dag_list = []
        for dag_x in All_DAG_list:
            Cx_DAG_list = [copy.deepcopy(dag_x) for _ in range(dag_num)]
            DPC.MDAG_Priority_Config('SELF', Cx_DAG_list)
            exam_dag_list += Cx_DAG_list

        for dag_x in exam_dag_list:
            for node_x in dag_x.nodes(data=True):
                node_x[1]['WCET'] = int((1 + random.uniform(-jitter_rate, jitter_rate)) * node_x[1]['WCET'])
        print(f'exam_num:{exam_num}')

        # (2) 基线实验测试；
        Preempt_type_dict = {'NP': False, 'P': 'type1'}
        ret_dict = {}
        for type_name, Preempt_type in Preempt_type_dict.items():
            Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(exam_dag_list), {'Core_Num': core_num, 'Dynamic': False,
                            'Total_Time': Period * cycle * 2, 'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': Preempt_type}])
            Dispatcher.run()
            ret_dict[type_name] = Dispatcher.Core_Data_List
            print(f'{type_name}', end='\t')
            print(f'MAKESPAN:{Core.ret_makespan(ret_dict[type_name])}', end=',\t')
            print(f'C1:{Core.ret_dag_cri_makespan(ret_dict[type_name], 1)}', end=',\t')
            print(f'C2:{Core.ret_dag_cri_makespan(ret_dict[type_name], 2)}')

        # (3) 阈值寻优；
        cyclye_num = 10
        min_makespan = Core.ret_dag_cri_makespan(ret_dict['P'], 1)
        ret_dag_list = random_PT_dag_list_new(exam_dag_list, All_DAG_list, cyclye_num)
        retcc1 = []
        retcc2 = []
        # for train_x in range(cyclye_num):
        for train_x in range(cyclye_num):
            print(f'exam_num:{train_x}')
            for sample_list_id, sample_list in enumerate(ret_dag_list):
                Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(sample_list[3]), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                             'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type4_2', 'Dynamic': False}])
                Dispatcher.run()
                ret_h = Dispatcher.Core_Data_List
                sample_list[2] = Core.ret_makespan(ret_h)
                sample_list[1] = Core.ret_dag_cri_makespan(ret_h, 2)
                sample_list[0] = Core.ret_dag_cri_makespan(ret_h, 1)

                print(f'sample_list_id:{sample_list_id}', end='\t')
                print(f'C1:{sample_list[0]}', end='\t')
                print(f'C2:{sample_list[1]}', end='\t')
                print(f'MAKESPAN:{sample_list[2]}', end='\t')
                print(f'C1_loss:{100 * (sample_list[0] - min_makespan) / min_makespan}')
            ret_dag_list = list(filter(lambda x: x[0] <= 1.05 * min_makespan, ret_dag_list))
            if len(ret_dag_list) < 10:
                ret_dag_list += random_PT_dag_list_new(exam_dag_list, All_DAG_list, 100 - len(ret_dag_list))
                continue
            else:
                ret_dag_list.sort(key=lambda x: x[0], reverse=False)
                ret_dag_list.sort(key=lambda x: x[2], reverse=False)
                ret_dag_list = ret_dag_list[:math.ceil(0.15 * cyclye_num)]  # 留下10个最好的样本

            ret_dag_list += random_PT_dag_list_cross(copy.deepcopy(ret_dag_list), exam_dag_list, All_DAG_list, math.ceil(0.55 * cyclye_num))  # 交叉 80组
            ret_dag_list += random_PT_dag_list_mutation(random.sample(ret_dag_list, math.ceil(0.15 * cyclye_num)))  # 变异 10组
            ret_dag_list += random_PT_dag_list_new(exam_dag_list, All_DAG_list,  math.ceil(0.15 * cyclye_num))

        ret_dag_list.sort(key=lambda x: x[0], reverse=False)
        ret_dag_list.sort(key=lambda x: x[2], reverse=False)
        ret_dag_x = ret_dag_list.pop(0)[3]
        Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(ret_dag_x), {'Core_Num': core_num, 'Total_Time': Period * cycle * 2,
                                             'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': 'type4_2', 'Dynamic': False}])

        Dispatcher.run()
        SELF_h = Dispatcher.Core_Data_List
        print(f'MAKESPAN:{Core.ret_makespan(SELF_h)}', end=',\t')
        print(f'C1:{Core.ret_dag_cri_makespan(SELF_h, 1)}', end=',\t')
        print(f'C2:{Core.ret_dag_cri_makespan(SELF_h, 2)}')

        retcc1.append([node_x[1]['PT'] for node_x in ret_dag_x[0 ].nodes(data=True)])
        retcc2.append([node_x[1]['PT'] for node_x in ret_dag_x[10].nodes(data=True)])


    retccc1 = []
    for x in range(HW_DAG[1].number_of_nodes()):
        ckk = [ret_cl[x] for ret_cl in retcc1]
        retccc1.append(max(set(ckk), key=ckk.count))

    retccc2 = []
    for x in range(HW_DAG[5].number_of_nodes()):
        ckk = [ret_cl[x] for ret_cl in retcc2]
        retccc2.append(max(set(ckk), key=ckk.count))
    retccc = [retccc1, retccc2]

    print(f'ret1:{retccc1}')
    print(f'ret2:{retccc2}')

    exam_dag_list = []
    for ret_id, dag_x in enumerate(All_DAG_list):
        for node_x in dag_x.nodes(data=True):
            node_x[1]['PT'] = retccc[ret_id].pop(0)
        Cx_DAG_list = [copy.deepcopy(dag_x) for _ in range(dag_num)]
        DPC.MDAG_Priority_Config('SELF', Cx_DAG_list)
        exam_dag_list += Cx_DAG_list
    # (2) 基线实验测试；
    Preempt_type_dict = {'NP': False, 'P': 'type1', 'PT': 'type4_2'}
    ret_dict = {}
    for type_name, Preempt_type in Preempt_type_dict.items():
        Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(exam_dag_list), {'Core_Num': core_num, 'Dynamic': False,
                        'Total_Time': Period * cycle * 2, 'Enqueue_rank': False, 'Priority_rank': True, 'Preempt_type': Preempt_type}])
        Dispatcher.run()
        ret_dict[type_name] = Dispatcher.Core_Data_List
        print(f'{type_name}', end='\t')
        print(f'MAKESPAN:{Core.ret_makespan(ret_dict[type_name])}', end=',\t')
        print(f'C1:{Core.ret_dag_cri_makespan(ret_dict[type_name], 1)}', end=',\t')
        print(f'C2:{Core.ret_dag_cri_makespan(ret_dict[type_name], 2)}')


        # ret_dict['Type_GA'] = SELF_h
        # hi_dag_list = [dag_x for dag_x in ret_dag_x if dag_x.graph['Criticality'] == 1]
        # lo_dag_list = [dag_x for dag_x in ret_dag_x if dag_x.graph['Criticality'] == 2]
        # for dag_id, dag_x in enumerate(hi_dag_list):
        #     dag_x.graph['DAG_ID'] = f'1_{dag_id}'
        # for dag_id, dag_x in enumerate(lo_dag_list):
        #     dag_x.graph['DAG_ID'] = f'2_{dag_id}'
        # DDP.Exam_Data_Output(ret_dag_x, 'ALL', Data_Output_Addr + '2023_8_23_EXAM\\')
        #
        # for ret_key, ret_value in ret_dict.items():
        #     SRS.show_core_data_list({ret_key: ret_value},
        #                             'Show', '',
        #                             # Data_Output_Addr,'Save',
        #                             copy.deepcopy([HW_DAG[1], HW_DAG[5]]), Period, cycle)


