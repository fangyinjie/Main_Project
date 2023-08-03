#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Core config
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################

import copy
import os
import random
import networkx as nx
import pandas as pd
import simpy
import matplotlib.pyplot as plt
import sys
import graphviz as gz
import threading
import time
import datetime

import Scheduler.Core as Core
import Scheduler.DAG_Generator as DG
import Scheduler.DAG_Features_Analysis as DFA
import Scheduler.DAG_Data_Processing as DDP
import Scheduler.DAG_Priority_Config as DPC
import Scheduler.Scheduling_Simulator as SS


TTL = 1130000


def Exam_function(param):
    temp_dag_x = param['DAG']
    core_number = param['Core_Num']
    Total_Time = param['Total_Time']
    dag_id = param['dag_id']
    exam_address = './NEW_RET_M1/flow-{0}_jiter-{1}_{2}/'.format(flow_num, jiter_rate, dag_id)
    if param['Running_type'] == 'huawei':
        Ret_Core_FIFO_Data_List = []
        for node_x in temp_dag_x.nodes(data=True):
            node_x[1]['WCET'] = node_x[1]['ET']
        for _ in range(500):
            param_l = [copy.deepcopy([temp_dag_x]), {'Core_Num': core_number, "Total_Time": Total_Time, 'Dynamic': False, 'Enqueue_rank': False, 'Priority_rank': True, 'PE': False}]
            Dispatcher = SS.Dispatcher_Workspace(param_l)
            Dispatcher.run()
            Ret_Core_FIFO_Data_List.append(Dispatcher.Core_Data_List)
        ret_data = max(Ret_Core_FIFO_Data_List, key=lambda x: Core.ret_makespan(x))
    elif param['Running_type'] == 'self_s':
        DPC.Priority_Config("SELF", [temp_dag_x])
        for node_x in temp_dag_x.nodes(data=True):
            node_x[1]['WCET'] = node_x[1]['ET']
        param_l = [copy.deepcopy([temp_dag_x]),     {'Core_Num': core_number, "Total_Time": Total_Time, 'Dynamic': False, 'Enqueue_rank': False, 'Priority_rank': True, 'PE': False}]
        Dispatcher = SS.Dispatcher_Workspace(param_l)
        Dispatcher.run()
        ret_data = Dispatcher.Core_Data_List
    elif param['Running_type'] == 'self_d':
        for node_x in temp_dag_x.nodes(data=True):  # (2) WCET
            node_x[1]['WCET'] = node_x[1]['ET']
        DFA.dag_param_critical_update(temp_dag_x, temp_dag_x.graph['DAG_ID'], Total_Time)
        DPC.Priority_Config("SELF", [temp_dag_x])  # (3) 优先级
        param_l = [copy.deepcopy([temp_dag_x]),     {'Core_Num': core_number, "Total_Time": Total_Time, 'Dynamic': True, 'Enqueue_rank': False, 'Priority_rank': True, 'PE': False}]
        Dispatcher = SS.Dispatcher_Workspace(param_l)
        Dispatcher.run()
        ret_data = Dispatcher.Core_Data_List
    elif param['Running_type'] == 'he_2019':
        DPC.Priority_Config("He_2019", [temp_dag_x])  # (2) 优先级
        for node_x in temp_dag_x.nodes(data=True):  # (3) WCET
            node_x[1]['WCET'] = node_x[1]['ET']
        param_l = [copy.deepcopy([temp_dag_x]),     {'Core_Num': core_number, "Total_Time": Total_Time, 'Dynamic': False, 'Enqueue_rank': False, 'Priority_rank': True, 'PE': False}]
        Dispatcher = SS.Dispatcher_Workspace(param_l)
        Dispatcher.run()
        ret_data = Dispatcher.Core_Data_List
    elif param['Running_type'] == 'chen_2019':
        DPC.Priority_Config("WCET", [temp_dag_x])  # (2) 优先级
        for node_x in temp_dag_x.nodes(data=True):  # (3) WCET
            node_x[1]['WCET'] = node_x[1]['ET']
        param_l = [copy.deepcopy([temp_dag_x]),     {'Core_Num': core_number, "Total_Time": Total_Time, 'Dynamic': False, 'Enqueue_rank': False, 'Priority_rank': True, 'PE': False}]
        Dispatcher = SS.Dispatcher_Workspace(param_l)
        Dispatcher.run()
        ret_data = Dispatcher.Core_Data_List
    else:
        os.error('running type error!')
    Core.Core_Data_CSV_Output(ret_data, exam_address, param['Running_type'], dag_x.graph['DAG_ID'])  # (1) 华为实验结果
    return ret_data


class MyThread_2(threading.Thread):  # 重写threading.Thread类，加入获取返回值的函数
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url
    def run(self):
        self.result = Exam_function(self.url)
    def get_result(self):
        return self.result


class myThread(threading.Thread):
    def __init__(self, threadID, name, param_l, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.param_l = param_l
        self.counter = counter
        self.result = {}

    def run(self):
        for e_counter in range(self.counter):
            st = time.time()
            ############################
            # 1. data initial
            All_flow_list = self.param_l[0]
            flow_num = self.param_l[1]['flow_num']
            jiter_rate = self.param_l[1]['jiter_rate']
            DAG_Num = self.param_l[1]['DAG_Num']

            core_number = flow_num + 1
            Param_dict = {'Flow_set': All_flow_list, 'flow_num': flow_num, 'WCET_interval': jiter_rate, 'DAG_Num': DAG_Num, 'arrival_interval': [0, 20 * 2260]}  # 0 ~ 20us
            Total_DAG_list = DG.Algorithm_input('FLOW', Param_dict)     # 生成DAG
            # Critical Paramter：
            for dag_x in Total_DAG_list:
                DFA.dag_param_critical_update(dag_x, dag_x.graph['DAG_ID'], Total_Time)
                for node_x in dag_x.nodes(data=True):
                    node_x[1]['WCET'] = int(node_x[1]['WCET'])
            # 4 DATA OBT：
            csv_dict = {}
            for dag_id, dag_x in enumerate(Total_DAG_list):
                huawei = MyThread_2({'Running_type': 'huawei', 'DAG': copy.deepcopy(dag_x), 'Core_Num': core_number, "Total_Time": Total_Time, 'dag_id': dag_id})
                self_d = MyThread_2({'Running_type': 'self_d', 'DAG': copy.deepcopy(dag_x), 'Core_Num': core_number, "Total_Time": Total_Time, 'dag_id': dag_id})
                self_s = MyThread_2({'Running_type': 'self_s', 'DAG': copy.deepcopy(dag_x), 'Core_Num': core_number, "Total_Time": Total_Time, 'dag_id': dag_id})
                he_2019 = MyThread_2({'Running_type': 'he_2019', 'DAG': copy.deepcopy(dag_x), 'Core_Num': core_number, "Total_Time": Total_Time, 'dag_id': dag_id})
                chen_2019 = MyThread_2({'Running_type': 'chen_2019', 'DAG': copy.deepcopy(dag_x), 'Core_Num': core_number, "Total_Time": Total_Time, 'dag_id': dag_id})

                huawei.start()
                self_d.start()
                self_s.start()
                he_2019.start()
                chen_2019.start()

                huawei.join()
                self_d.join()
                self_s.join()
                he_2019.join()
                chen_2019.join()

                FIFO_Makespan = Core.ret_makespan(huawei.get_result())
                SELF_D_Makespan = Core.ret_makespan(self_d.get_result())
                SELF_S_Makespan = Core.ret_makespan(self_s.get_result())
                HE_Makespan = Core.ret_makespan(he_2019.get_result())
                WCET_Makespan = Core.ret_makespan(chen_2019.get_result())

                self_s_improve = 100 * (FIFO_Makespan - SELF_S_Makespan) / FIFO_Makespan
                self_d_improve = 100 * (FIFO_Makespan - SELF_D_Makespan) / FIFO_Makespan
                he_improve = 100 * (FIFO_Makespan - HE_Makespan) / FIFO_Makespan
                wcet_improve = 100 * (FIFO_Makespan - WCET_Makespan) / FIFO_Makespan

                self_conter_improve = 100 * (SELF_S_Makespan - SELF_D_Makespan) / SELF_S_Makespan

                print(f"Flow:{flow_num}-Jiter:{jiter_rate}-DAG_ID:{dag_id}", end="\t\t")
                print("DAG_CV_Rate:{0}".format(DFA.get_Rate_of_Cri_to_volume(dag_x)), end="\t\t")
                print(f"DAG_ID:{dag_x.graph['DAG_ID']}", end="\t\t")
                print(f"HUAWEI:{FIFO_Makespan}", end="\t\t")
                print(f"SELF_S:{SELF_S_Makespan}", end="\t\t")
                print(f"SELF_D:{SELF_D_Makespan}", end="\t\t")
                print(f"WCET:{WCET_Makespan}", end="\t\t")
                print(f"HE_2019:{HE_Makespan}", end="\t\t")

                print("SELF_S_improve:{0:.2f}".format(self_s_improve), end="\t\t")
                print("SELF_D_improve:{0:.2f}".format(self_d_improve), end="\t\t")
                print("WCET_improve:{0:.2f}".format(wcet_improve), end="\t\t")
                print("HE_2019_improve:{0:.2f}".format(he_improve), end="\t\t")
                print("SELF_conter_improve:{0:.2f}".format(self_conter_improve))

                test_dag_1 = copy.deepcopy(dag_x)
                for nx_tt in test_dag_1.nodes(data=True):
                    nx_tt[1]['WCET'] = nx_tt[1]['ET']

                csv_dict[str(dag_id) + '_' + dag_x.graph['DAG_ID'] + str(flow_num) + str(jiter_rate)] = { 'DAG_ID': dag_x.graph['DAG_ID'],
                                                                        'Flow_num': flow_num,
                                                                        'Jitter_Rate': jiter_rate,
                                                                        'HUAWEI': FIFO_Makespan,
                                                                        'SELF_S': SELF_S_Makespan,
                                                                        'SELF_D': SELF_D_Makespan,
                                                                        'HE': HE_Makespan,
                                                                        'WCET': WCET_Makespan,
                                                                        'SELF_S_improve': self_s_improve,
                                                                        'SELF_D_improve': self_d_improve,
                                                                        'WCET_improve': wcet_improve,
                                                                        'HE_improve': he_improve,
                                                                        'SELF_conter_improve': self_conter_improve,
                                                                        'DAG_CV_Rate': DFA.get_Rate_of_Cri_to_volume(dag_x)}
                exam_address = './NEW_RET_M1/flow-{0}_jiter-{1}_{2}/'.format(flow_num, jiter_rate, dag_id)
                DDP.Exam_Data_Output([dag_x], 'ALL', exam_address)  # 实验数据整合
            self.result.update( csv_dict )
            ############################
            et = time.time()
            print("##############################################")
            print("Flow %s —— Jiter %s excaution time = %.2f (ms)" % (flow_num, jiter_rate,((et - st) * 1000)))
            print("##############################################")

    def get_result(self):
        return self.result


if __name__ == "__main__":
    # (1) Environment parameter configuration
    Total_Time = 3 * TTL
    # (2) DAG generation
    root_addr = 'D:/github/DAG_Scheduling_Summary/Exam_Input_data/xlsx_data/wireless/DAG_Data_flow_new_m1.xlsx'
    All_flow_list = DG.Manual_Input('XLSX', [root_addr])

    for dag_x in All_flow_list:
        DFA.dag_param_critical_update(dag_x, dag_x.graph['DAG_ID'], Total_Time)

    exam_thread_dict = {}
    exam_data_id = 0
    for jiter_rate in [0.1, 0.3, 0.5, 0.7, 0.9]:
        exam_thread_dict[jiter_rate] = {}
        for flow_num in range(2, 8):
            param_l = [copy.deepcopy(All_flow_list), {'jiter_rate': jiter_rate, 'flow_num': flow_num, 'DAG_Num': 100}]
            exam_thread_dict[jiter_rate][flow_num] = myThread(exam_data_id, "Thread-{0}".format(exam_data_id), param_l, 1)
            exam_data_id += 1

    # thread start
    for t_id, t_value in exam_thread_dict.items():
        for tt_id, tt_value in t_value.items():
            tt_value.start()

    # thread join
    for t_id, t_value in exam_thread_dict.items():
        for tt_id, tt_value in t_value.items():
            tt_value.join()

    total_ret = {}
    for t_id, t_value in exam_thread_dict.items():
        for tt_id, tt_value in t_value.items():
            total_ret.update(tt_value.get_result())

    df = pd.DataFrame(total_ret).T
    df.to_csv('./result_data_m1.csv')

#####################################################
# def exam_pic_show(dag_x, title):
#     dot = gz.Digraph()
#     dot.attr(rankdir='LR')
#     for node_x in dag_x.nodes(data=True):
#         temp_label = 'Node_ID:{0}\nPrio:{1}\nWCET:{2}\nET:{3}\n'.format(
#             str(node_x[1]['Node_ID']), str(node_x[1]['Prio']), str(node_x[1]['WCET']), str(node_x[1]['ET']))
#         temp_node_dict = node_x[1]
#         if 'critic' in temp_node_dict:
#             if node_x[1]['critic']:
#                 color_t = 'red'
#             else:
#                 color_t = 'green'
#         else:
#             color_t = 'black'
#         dot.node('%s' % node_x[0], temp_label, color=color_t)
#     for edge_x in dag_x.edges():
#         dot.edge('%s' % edge_x[0], '%s' % edge_x[1])
#     dot.view('./pic_test/' + title)


