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

