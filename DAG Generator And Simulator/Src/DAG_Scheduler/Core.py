#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Core config
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################

import os
import pandas as pd
import matplotlib.pyplot as plt
# import datetime
# from . import Simulation_Result_Show as SRS


class Core_Obj:
    def __init__(self, core_id):
        self.Core_ID              = core_id
        self.Core_Running_Task    = []            # the running log about this core (sch list)
        self.last_finish_time     = 0
        self.Running_node         = []
        self.Task_allocation_list = []


    def Insert_Task_Info(self, node, start_time, end_time):
        temp_dict = {'node': node, 'start_time': start_time, 'end_time': end_time}
        self.Core_Running_Task.append(temp_dict)
        # self.Core_Running_Task = sorted(self.Core_Running_Task, key=lambda d: d['end_time'], reverse=False)
        self.last_finish_time = max([core_data_x['end_time'] for core_data_x in self.Core_Running_Task])
        return True

    def get_core_last_time(self):
        return max([core_data_x['end_time'] for core_data_x in self.Core_Running_Task])


def ret_dag_cri_makespan(Ret_Core_Data_List, criticality):
    max_data_list = []
    for core_id, core_data_x in Ret_Core_Data_List.items():
        for node_data_x in core_data_x.Core_Running_Task:
            if node_data_x['node'][1]['Criticality'] == criticality:
                max_data_list.append(node_data_x['end_time'])
    if len(max_data_list) == 0:
        os.error(f'system error！__{criticality}')
    else:
        return max(max_data_list)


def ret_dag_DAG_NUM_makespan(Ret_Core_Data_List, DAG_NUM):
    max_data_list = []
    for core_id, core_data_x in Ret_Core_Data_List.items():
        for node_data_x in core_data_x.Core_Running_Task:
            if node_data_x['node'][1]['DAG'].graph['DAG_NUM'] == DAG_NUM:
                max_data_list.append(node_data_x['end_time'])
    if len(max_data_list) == 0:
        os.error(f'system error！__{DAG_NUM}')
    else:
        return max(max_data_list)

def ret_dag_CRI_DAG_NUM_makespan(Ret_Core_Data_List, criticality, DAG_NUM):
    max_data_list = []
    for core_id, core_data_x in Ret_Core_Data_List.items():
        for node_data_x in core_data_x.Core_Running_Task:
            if node_data_x['node'][1]['Criticality'] == criticality and node_data_x['node'][1]['DAG'].graph['DAG_NUM'] == DAG_NUM:
                max_data_list.append(node_data_x['end_time'])
    if len(max_data_list) == 0:
        os.error(f'system error！__{criticality} AND ！__{DAG_NUM} ')
    else:
        return max(max_data_list)

def ret_dag_id_makespan(Ret_Core_Data_List, DAG_ID):
    max_data_list = []
    for core_data_x in Ret_Core_Data_List:
        for node_data_x in core_data_x.Core_Running_Task:
            if node_data_x['node'][1]['DAG'].graph['DAG_ID'] == DAG_ID:
                max_data_list.append(node_data_x['end_time'])
    if len(max_data_list) == 0:
        os.error(f'system error！__{DAG_ID}')
    else:
        return max(max_data_list)


def ret_makespan(Ret_Core_Data_List):
    return max([node_data_x['end_time'] for core_id, core_data_x in Ret_Core_Data_List.items() for node_data_x in core_data_x.Core_Running_Task ])



if __name__ == "__main__":
    core = Core_Obj('c1')
    core.Insert_Task_Info((1, {'Node_ID': '1'}), 0, 100)
    core.Insert_Task_Info((2, {'Node_ID': '2'}), 0, 300)
    core.Insert_Task_Info((3, {'Node_ID': '3'}), 0, 200)
    core.Insert_Task_Info((4, {'Node_ID': '4'}), 0, 700)
    core.Insert_Task_Info((5, {'Node_ID': '4'}), 0, 500)
    core.Insert_Task_Info((6, {'Node_ID': '4'}), 0, 800)
    core.Insert_Task_Info((7, {'Node_ID': '5'}), 0, 400)
