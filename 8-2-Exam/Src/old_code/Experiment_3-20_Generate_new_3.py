#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Core config
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################

import re
import copy
import os
import random
import networkx as nx
import pandas as pd
import simpy
import matplotlib.pyplot as plt
import sys
import pygraphviz as pgz
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
import Scheduler.Simulation_Result_Show as SRS


# import Simulation_Result_Show as SRS
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
    # dot.view('./test.png')
    dot.view('./pic_test/' + title)


def exam_pic_self_show(dag_x, title):
    dot = gz.Digraph()
    dot.attr(rankdir='LR')
    for node_x in dag_x.nodes(data=True):
        temp_label = 'Node_ID:{0}\nPrio:{1}\nWCET:{2}\nET:{3}\nGroup:{4}\nsub_cpath:{5}\n'.format(
            str(node_x[1]['Node_ID']), str(node_x[1]['Prio']), str(node_x[1]['WCET']), str(node_x[1]['ET']),
            str(node_x[1]['Group']), str(node_x[1]['sub_cpath']))
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
    # dot.view('./test.png')
    dot.view('./pic_test/' + title)


class MyThread(threading.Thread):  # 重写threading.Thread类，加入获取返回值的函数
    def __init__(self, threadID, name, param_l, counter, function_id):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.param_l = param_l
        self.counter = counter
        self.function_id = function_id
        self.result_level_1 = []
        self.result_level_2 = {}

    def run(self):
        if self.function_id == 'level_1':
            self.result_level_1 = self.Exam_function_1(self.param_l)
        elif self.function_id == 'level_2':
            self.result_level_2 = self.Exam_function_2(self.param_l)

    def get_result(self):
        if self.function_id == 'level_1':
            return self.result_level_1
        elif self.function_id == 'level_2':
            return self.result_level_2

    def Max_Ret_Test(self, dag_list, param_l):    # 循环执行，找最大的结果
        Ret_Core_FIFO_Data_List = []
        for _ in range(500):
            Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(dag_list), param_l])
            Dispatcher.run()
            Ret_Core_FIFO_Data_List.append(Dispatcher.Core_Data_List)
        return max(Ret_Core_FIFO_Data_List, key=lambda x: Core.ret_makespan(x))


    def Ret_Test(self, dag_list, param_l):
        temp_dag_x = copy.deepcopy(dag_list)
        DPC.Priority_Config("SELF", temp_dag_x)
        Dispatcher = SS.Dispatcher_Workspace([copy.deepcopy(dag_list), param_l])
        Dispatcher.run()
        return Dispatcher.Core_Data_List


    def Exam_function_1(self, param):
        temp_dag_x = param['DAG']
        core_number = param['Core_Num']
        Total_Time = param['Total_Time']
        if param['Running_type'] == 'huawei':
            DFA.dag_critical_path(temp_dag_x)
            for node_x in temp_dag_x.nodes(data=True):
                node_x[1]['WCET'] = node_x[1]['ET']
            # exam_pic_show(temp_dag_x, self.name)
            return self.Max_Ret_Test([temp_dag_x], {'Core_Num': core_number, "Total_Time": Total_Time, 'Dynamic': False, 'Enqueue_rank': False, 'Priority_rank': True, 'PE': False, 'Non_WC': False})
        elif param['Running_type'] == 'self_s':
            DFA.dag_critical_path(temp_dag_x)
            DPC.Priority_Config("SELF", [temp_dag_x])
            # exam_pic_show(temp_dag_x, self.name)
            for node_x in temp_dag_x.nodes(data=True):
                node_x[1]['WCET'] = node_x[1]['ET']
            return self.Ret_Test(copy.deepcopy([temp_dag_x]), {'Core_Num': core_number, "Total_Time": Total_Time, 'Dynamic': False, 'Enqueue_rank': False, 'Priority_rank': True, 'PE': False, 'Non_WC': True})
        elif param['Running_type'] == 'self_d':
            for node_x in temp_dag_x.nodes(data=True):
                node_x[1]['WCET'] = node_x[1]['ET']
            # exam_pic_show(temp_dag_x, self.name)
            DFA.dag_critical_path(temp_dag_x)
            DPC.Priority_Config("SELF", [temp_dag_x])
            return self.Ret_Test(copy.deepcopy([temp_dag_x]), {'Core_Num': core_number, "Total_Time": Total_Time, 'Dynamic': True, 'Enqueue_rank': False, 'Priority_rank': True, 'PE': False, 'Non_WC': True})
        elif param['Running_type'] == 'he_2019':
            for node_x in temp_dag_x.nodes(data=True):
                node_x[1]['WCET'] = node_x[1]['ET']
            DPC.Priority_Config("He_2019", [temp_dag_x])
            # exam_pic_show(temp_dag_x, self.name)
            return self.Ret_Test(copy.deepcopy([temp_dag_x]), {'Core_Num': core_number, "Total_Time": Total_Time, 'Dynamic': False, 'Enqueue_rank': False, 'Priority_rank': True, 'PE': False, 'Non_WC': False})
        else:
            os.error('running type error!')


    def Exam_function_2(self, param_l):
        st = time.time()

        All_flow_list = param_l[0]
        flow_num = param_l[1]['flow_num']
        jiter_rate = param_l[1]['jiter_rate']
        DAG_Num = param_l[1]['DAG_Num']
        core_number = flow_num + 1
        Param_dict = {'Flow_set': All_flow_list, 'flow_num': flow_num, 'WCET_interval': jiter_rate, 'DAG_Num': DAG_Num, 'arrival_interval': [0, 20 * 2260]}  # 0 ~ 20us
        Total_DAG_list = DG.Algorithm_input('FLOW', Param_dict)
        for dag_x in Total_DAG_list:
            DFA.dag_param_critical_update(dag_x, dag_x.graph['DAG_ID'], Total_Time)
            for node_x in dag_x.nodes(data=True):
                node_x[1]['WCET'] = int(node_x[1]['WCET'])
        csv_dict = {}
        for dag_id, dag_x in enumerate(Total_DAG_list):
            huawei  = MyThread(dag_id * 10 + 1, "Thread-{0}-{1}-F_{2}-J_{3}".format(dag_id, 'HUAWEI', flow_num, jiter_rate), {'Running_type': 'huawei', 'DAG': copy.deepcopy(dag_x), 'Core_Num': core_number, "Total_Time": Total_Time, 'dag_id': dag_id}, 1, 'level_1')
            self_d  = MyThread(dag_id * 10 + 2, "Thread-{0}-{1}-F_{2}-J_{3}".format(dag_id, 'SELF_D', flow_num, jiter_rate), {'Running_type': 'self_d', 'DAG': copy.deepcopy(dag_x), 'Core_Num': core_number, "Total_Time": Total_Time, 'dag_id': dag_id}, 1, 'level_1')
            self_s  = MyThread(dag_id * 10 + 3, "Thread-{0}-{1}-F_{2}-J_{3}".format(dag_id, 'SELF_S', flow_num, jiter_rate), {'Running_type': 'self_s', 'DAG': copy.deepcopy(dag_x), 'Core_Num': core_number, "Total_Time": Total_Time, 'dag_id': dag_id}, 1, 'level_1')
            he_2019 = MyThread(dag_id * 10 + 4, "Thread-{0}-{1}-F_{2}-J_{3}".format(dag_id, 'He-2019', flow_num, jiter_rate), {'Running_type': 'he_2019', 'DAG': copy.deepcopy(dag_x), 'Core_Num': core_number, "Total_Time": Total_Time, 'dag_id': dag_id}, 1, 'level_1')

            huawei.start(); self_d.start(); self_s.start(); he_2019.start()
            huawei.join();  self_d.join();  self_s.join();  he_2019.join()

            Ret_Core_FIFO_Data = huawei.get_result()
            Ret_Core_SELF_S_Data = self_s.get_result()
            Ret_Core_SELF_D_Data = self_d.get_result()
            Ret_He_2019_Data = he_2019.get_result()

            FIFO_Makespan = Core.ret_makespan(Ret_Core_FIFO_Data)
            SELF_D_Makespan = Core.ret_makespan(Ret_Core_SELF_S_Data)
            SELF_S_Makespan = Core.ret_makespan(Ret_Core_SELF_D_Data)
            HE_Makespan = Core.ret_makespan(Ret_He_2019_Data)

            self_s_improve      = 100 * (FIFO_Makespan - SELF_S_Makespan) / FIFO_Makespan
            self_d_improve      = 100 * (FIFO_Makespan - SELF_D_Makespan) / FIFO_Makespan
            he_improve          = 100 * (FIFO_Makespan - HE_Makespan) / FIFO_Makespan
            self_conter_improve = 100 * (SELF_S_Makespan - SELF_D_Makespan) / SELF_S_Makespan
            se_he_conter_improve = 100 * (HE_Makespan - SELF_S_Makespan) / HE_Makespan

            print(f"Flow:{flow_num}-Jiter:{jiter_rate}-DAG_ID:{dag_id}\tDAG_CV_Rate:{DFA.get_Rate_of_Cri_to_volume(dag_x)}\tDAG_ID:{dag_x.graph['DAG_ID']}\t"
                  f"HUAWEI:{FIFO_Makespan}\tSELF_S:{SELF_S_Makespan}\tSELF_D:{SELF_D_Makespan}\tHE_2019:{HE_Makespan}\t")

            print("SELF_S_improve:{0:.2f}\tSELF_D_improve:{1:.2f}\tHE_2019_improve:{2:.2f}\t".format(self_s_improve, self_d_improve, he_improve))

            print("SELF_conter_improve:{0:.2f}\tse_he_conter_improve:{1:.2f}".format(self_conter_improve, se_he_conter_improve))

            exam_address = './NEW_RET_1/flow-{0}/jiter-{1}/{2}/'.format(flow_num, jiter_rate, dag_id)
            Core.Core_Data_CSV_Output(Ret_Core_FIFO_Data, exam_address, 'huawei', dag_x.graph['DAG_ID'])
            Core.Core_Data_CSV_Output(Ret_Core_SELF_S_Data, exam_address, 'self-s', dag_x.graph['DAG_ID'])
            Core.Core_Data_CSV_Output(Ret_Core_SELF_D_Data, exam_address, 'self-d', dag_x.graph['DAG_ID'])
            Core.Core_Data_CSV_Output(Ret_He_2019_Data, exam_address, 'he2019', dag_x.graph['DAG_ID'])

            DDP.Exam_Data_Output([dag_x], 'ALL', exam_address)  # 实验数据整合

            DFA.dag_param_critical_update(dag_x, dag_x.graph['DAG_ID'], None)  # (3) Critical paramter
            csv_dict[str(dag_id) + '_' + dag_x.graph['DAG_ID'] + str(flow_num) + str(jiter_rate)] = {
                'DAG_ID': dag_x.graph['DAG_ID'], 'DAG_Index': dag_id, 'Flow_num': flow_num, 'Jitter_Rate': jiter_rate,
                'Real_Jitter_Rate': DFA.dag_jiter_comput(dag_x), 'DAG_CV_Rate': DFA.get_Rate_of_Cri_to_volume(dag_x),

                'HUAWEI': FIFO_Makespan, 'SELF_S': SELF_S_Makespan, 'SELF_D': SELF_D_Makespan, 'HE': HE_Makespan,
                'SELF_S_improve': self_s_improve, 'SELF_D_improve': self_d_improve, 'HE_improve': he_improve,
                'SELF_conter_improve': self_conter_improve, 'se_he_conter_improve': se_he_conter_improve,

                'Number_Of_Level':dag_x.graph['Number_Of_Level'], 'Shape_List': dag_x.graph['Shape_List'], 'Ave_Shape': dag_x.graph['Ave_Shape'], 'Std_Shape': dag_x.graph['Std_Shape'], 'Max_Shape': dag_x.graph['Max_Shape'],
                'Re_Shape_List':dag_x.graph['Re_Shape_List'], 'Ave_Re_Shape': dag_x.graph['Ave_Re_Shape'], 'Std_Re_Shape': dag_x.graph['Std_Re_Shape'], 'Max_Re_Shape': dag_x.graph['Max_Re_Shape'], 'Min_Re_Shape': dag_x.graph['Min_Re_Shape'],
                'Width': dag_x.graph['Width'],
                'Max_Degree': dag_x.graph['Max_Degree'], 'Min_Degreedag_x':dag_x.graph['Min_Degree'], 'Ave_Degree':dag_x.graph['Ave_Degree'], 'Std_Degree':dag_x.graph['Std_Degree'],
                'Max_In_Degree':dag_x.graph['Max_In_Degree'], 'Min_In_Degree':dag_x.graph['Min_In_Degree'], 'Ave_In_Degree':dag_x.graph['Ave_In_Degree'], 'Std_In_Degree':dag_x.graph['Std_In_Degree'],

                'Max_Out_Degree':dag_x.graph['Max_Out_Degree'], 'Min_Out_Degree':dag_x.graph['Min_Out_Degree'], 'Ave_Out_Degree':dag_x.graph['Ave_Out_Degree'], 'Std_Out_Degree':dag_x.graph['Std_Out_Degree'],
                'Connection_Rate':dag_x.graph['Connection_Rate'], 'Jump_Level':dag_x.graph['Jump_Level'],
                'DAG_volume':dag_x.graph['DAG_volume'],
                'Max_WCET':dag_x.graph['Max_WCET'], 'Min_WCET':dag_x.graph['Min_WCET'], 'Ave_WCET':dag_x.graph['Ave_WCET'], 'Std_WCET':dag_x.graph['Std_WCET'],

                'Ret_Core_FIFO_Data': Ret_Core_FIFO_Data,
                'Ret_Core_SELF_S_Data': Ret_Core_SELF_S_Data,
                'Ret_Core_SELF_D_Data': Ret_Core_SELF_D_Data,
                'Ret_He_2019_Data': Ret_He_2019_Data}

        et = time.time()
        print("##############################################")
        print("Flow %s —— Jiter %s excaution time = %.2f (ms)" % (flow_num, jiter_rate, ((et - st) * 1000)))
        print("##############################################")
        return csv_dict


if __name__ == "__main__":
    Total_Time = 3 * TTL        # (1) Environment parameter configuration
    All_flow_list = DG.Manual_Input('XLSX', ['D:/github/DAG_Scheduling_Summary/Exam_Input_data/xlsx_data/wireless/DAG_Data_flow_new_2.xlsx'])    # (2) DAG generation
    for dag_x in All_flow_list:
        DFA.dag_param_critical_update(dag_x, dag_x.graph['DAG_ID'], Total_Time)     # (3) Critical paramter

    exam_thread_dict = {}
    exam_data_id = 0
    for jiter_rate in [0.1, 0.3, 0.5]:
    # for jiter_rate in [0.1]:
        exam_thread_dict[jiter_rate] = {}
        for flow_num in range(3, 7):
            param_l = [copy.deepcopy(All_flow_list), {'jiter_rate': jiter_rate, 'flow_num': flow_num, 'DAG_Num': 50}]
            exam_thread_dict[jiter_rate][flow_num] = MyThread(exam_data_id, "Thread-{0}".format(exam_data_id), param_l, 1, 'level_2')
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

    for dag_id, dag_data in total_ret.items():
        Ret_Core_FIFO_Data = dag_data.pop('Ret_Core_FIFO_Data')
        Ret_Core_SELF_S_Data = dag_data.pop('Ret_Core_SELF_S_Data')
        Ret_Core_SELF_D_Data = dag_data.pop('Ret_Core_SELF_D_Data')
        Ret_He_2019_Data = dag_data.pop('Ret_He_2019_Data')
        # core_data_list = Core.Core_Data_Input('test_core.csv', "CSV")
        # plt.figure(figsize=(30, 20))
        # FontSize = 8
        # ax = plt.subplot(4, 1, 1)
        # SRS.show_makespan(Ret_Core_FIFO_Data, ax, FontSize, 'HUAWEI')
        # ax = plt.subplot(4, 1, 2)
        # SRS.show_makespan(Ret_Core_SELF_S_Data, ax, FontSize, 'SELF_S')
        # ax = plt.subplot(4, 1, 3)
        # SRS.show_makespan(Ret_Core_SELF_D_Data, ax, FontSize, 'SELF_D')
        # ax = plt.subplot(4, 1, 4)
        # SRS.show_makespan(Ret_He_2019_Data, ax, FontSize, 'HE_2019')
        # plt.savefig('./NEW_RET_1/flow-{0}/jiter-{1}/{2}/pic-{2}.png'.format(dag_data['Flow_num'], dag_data['Jitter_Rate'], dag_data['DAG_Index']))
        # plt.close()

    df = pd.DataFrame(total_ret).T
    df.to_csv('./result_data.csv')

