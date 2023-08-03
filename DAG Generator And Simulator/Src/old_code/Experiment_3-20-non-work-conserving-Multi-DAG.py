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
import graphviz as gz

import Scheduler.Core as Core
import Scheduler.DAG_Generator as DG
import Scheduler.DAG_Features_Analysis as DFA
import Scheduler.DAG_Priority_Config as DPC
import Scheduler.Scheduling_Simulator as SS
import Scheduler._scheduler_optimal_2 as SOPT
import Scheduler.Simulation_Result_Show as SRS
# import limited_priority_assign as PP_lpa

TTL = 1130000


def exam_pic_show(dag_x, title):
    dot = gz.Digraph()
    dot.attr(rankdir='LR')
    for node_x in dag_x.nodes(data=True):
        temp_label = 'Node_ID:{0}\nPrio:{1}\nWCET:{2}\nET:{3}\n'.format(
            str(node_x[1]['Node_ID']), str(node_x[1]['Prio']), str(node_x[1]['WCET']), str(node_x[1]['ET']))
        temp_node_dict = node_x[1]
        if 'critic' in temp_node_dict:
            if node_x[1]['critic']:
                color_t = 'red'
            else:
                color_t = 'green'
        else:
            color_t = 'black'
        dot.node('%s' % node_x[0], temp_label, color=color_t)
    for edge_x in dag_x.edges():
        dot.edge('%s' % edge_x[0], '%s' % edge_x[1])
    dot.view('./non_worconserving-pic/' + title)


if __name__ == "__main__":
    # (1) Environment parameter configuration
    Total_Time = 3 * TTL
    # (2) DAG generation
    root_addr = 'D:/github/DAG_Scheduling_Summary/Exam_Input_data/xlsx_data/wireless/DAG_Data.xlsx'
    All_DAG_list = DG.Manual_Input('XLSX', [root_addr])
    # (3) Critical Paramter：
    for dag_x in All_DAG_list:
        DFA.dag_param_critical_update(dag_x, dag_x.graph['DAG_ID'], Total_Time)
        for node_x in dag_x.nodes(data=True):
            node_x[1]['WCET'] = int(node_x[1]['WCET'])

    core_num_dict = {"M1_S1_C1": 2, "M1_S2_C1": 3, "M1_S1_C2": 2, "M1_S2_C2": 3,
                     "M2_S1_C1": 2, "M2_S2_C1": 3, "M2_S3_C1": 5,
                     "M2_S1_C2": 2, "M2_S2_C2": 3, "M2_S3_C2": 5}

    # exam_dag_list = ["M1_S1_C1", "M1_S2_C1", "M1_S1_C2", "M1_S2_C2", "M2_S1_C1", "M2_S2_C1", "M2_S1_C2", "M2_S2_C2", "M2_S3_C1", "M2_S3_C2"]
    exam_dag_list = ["M1_S2_C2"]
    All_DAG_list = [dag_x for dag_x in All_DAG_list if dag_x.graph['DAG_ID'] in exam_dag_list]

    for dag_x in All_DAG_list:
        print(dag_x.graph['DAG_ID'])
        # 1) 最优调度；
        param_l = [copy.deepcopy(dag_x), {'Core_Num': core_num_dict[dag_x.graph['DAG_ID']]}]
        Ret_Core_OPT_Data = SOPT.Dispatcher_Workspace(param_l)
        OPT_MakeSpan = Core.ret_makespan(Ret_Core_OPT_Data)
        print('OPT_MakeSpan:{0} = {1:.4f}'.format(OPT_MakeSpan, OPT_MakeSpan/2260000))

        # 2) FIFO 结合华为优先级；
        Ret_Core_FIFO_Data_List = []
        temp_dag_list = copy.deepcopy([dag_x])
        for _ in range(100):
            param_l = [copy.deepcopy(temp_dag_list), {'Core_Num':  core_num_dict[dag_x.graph['DAG_ID']], 'Total_Time': Total_Time, 'Dynamic':False, 'Enqueue_rank': False, 'Priority_rank': True, 'PE': False, 'Non_WC':False}]
            Dispatcher = SS.Dispatcher_Workspace(param_l)
            Dispatcher.run()
            Ret_Core_FIFO_Data_List.append(Dispatcher.Core_Data_List)
        Ret_Core_FIFO_Data = max(Ret_Core_FIFO_Data_List, key=lambda x: Core.ret_makespan(x))
        FIFO_Makespan = Core.ret_makespan(Ret_Core_FIFO_Data)
        print('FIFO_Makespan:{0} = {1:.4f}'.format(FIFO_Makespan, FIFO_Makespan/2260000))

        # # 3.1) SELF 调度结果；_workconserving
        temp_dag_list = copy.deepcopy([dag_x])
        DPC.Priority_Config("SELF", temp_dag_list)
        param_l = [copy.deepcopy(temp_dag_list), {'Core_Num': core_num_dict[dag_x.graph['DAG_ID']], 'Total_Time': Total_Time, 'Dynamic': False, 'Enqueue_rank': False, 'Priority_rank': True, 'PE': False, 'Non_WC': False}]
        Dispatcher = SS.Dispatcher_Workspace(param_l)
        Dispatcher.run()
        Ret_Core_SELF_Data = Dispatcher.Core_Data_List
        SELF_Makespan = Core.ret_makespan(Ret_Core_SELF_Data)
        print('SELF_Makespan:{0} = {1:.4f}'.format(SELF_Makespan, SELF_Makespan / 2260000), end='       ')
        print('improve:{0}%'.format(100 * (FIFO_Makespan - SELF_Makespan) / FIFO_Makespan))

        # # 3.2) SELF 调度结果；_non-workconserving
        temp_dag_list = copy.deepcopy([dag_x])
        DPC.Priority_Config("SELF", temp_dag_list)
        param_l = [copy.deepcopy(temp_dag_list), {'Core_Num': core_num_dict[dag_x.graph['DAG_ID']], 'Total_Time': Total_Time, 'Dynamic': False, 'Enqueue_rank': False, 'Priority_rank': True, 'PE': False, 'Non_WC': True}]
        Dispatcher = SS.Dispatcher_Workspace(param_l)
        Dispatcher.run()
        Ret_Core_SELF_NC_Data = Dispatcher.Core_Data_List
        SELF_NC_Makespan = Core.ret_makespan(Ret_Core_SELF_NC_Data)
        print('SELF_Makespan_NC:{0} = {1:.4f}'.format(SELF_NC_Makespan, SELF_NC_Makespan / 2260000), end='       ')
        print('improve:{0}%'.format(100 * (FIFO_Makespan - SELF_NC_Makespan) / FIFO_Makespan))
        # 4) 业界横向对比；
        # 5) 有限优先级——待定；

        # core_data_list = Core.Core_Data_Input('test_core.csv', "CSV")
        fig = plt.figure()
        FontSize = 8
        ax = plt.subplot(4, 1, 1)
        SRS.show_makespan(Ret_Core_OPT_Data, ax, FontSize, 'OPT')
        ax = plt.subplot(4, 1, 2)
        SRS.show_makespan(Ret_Core_FIFO_Data, ax, FontSize, 'HUAWEI')
        ax = plt.subplot(4, 1, 3)
        SRS.show_makespan(Ret_Core_SELF_Data, ax, FontSize, 'SELF')
        ax = plt.subplot(4, 1, 4)
        SRS.show_makespan(Ret_Core_SELF_NC_Data, ax, FontSize, 'SELF_NC')
        plt.show()

    # plt.draw()
    # plt.show()
    plt.savefig('./pdf.pdf', format='pdf')

    # plt.plot()
    # plt.close()
    # plt.draw()    将重新绘制图形。这允许您在交互模式下工作，如果您更改了数据或格式，则允许图形本身更改。
    # plt.savefig('./img/pic-{}.png'.format(epoch + 1))
    # plt.pause(1)
    # plt.show()将显示您正在处理的当前图形。

    # plt.close('all')  # 关闭所有 figure windows
    # plt.cla()  # 清除axes，即当前 figure 中的活动的axes，但其他axes保持不变。
    # plt.clf()  # 清除当前 figure 的所有axes，但是不关闭这个 window，所以能继续复用于其他的 plot。
    # plt.close()  # 关闭 window，如果没有指定，则指当前 window。
