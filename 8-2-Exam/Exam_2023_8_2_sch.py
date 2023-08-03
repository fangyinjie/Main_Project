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
import graphviz as gz

import Src.Core as Core
import Src.DAG_Generator as DG
import Src.DAG_Features_Analysis as DFA
import Src.DAG_Priority_Config as DPC
import Src.Scheduling_Simulator_new_2 as SS
# import Scheduler.Scheduling_Simulator as SS
# import Scheduler.Scheduling_Simulator_new_4 as SS
import Src.Light_Scheduling_Simulator_new as LSS

TTL = 1130000


def exam_pic_show(dag_x, title):
    dot = gz.Digraph()
    dot.attr(rankdir='LR')
    for node_x in dag_x.nodes(data=True):
        temp_label = 'Node_ID:{0}\nPrio:{1}\nWCET:{2}\nIndex:{3}\n'.format(
            str(node_x[0]), str(node_x[1]['Prio']), str(node_x[1]['WCET']), str(node_x[1]['Node_ID']))
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
    dot.view(f'./pic_test_7-25/{title}')


if __name__ == "__main__":
    # (1) DAG input
    Total_Time = 20 * TTL
    # (1) DAG input 确定两DAG
    addr_str = 'D:/github/DAG_Scheduling_Summary/Exam_Main_new/Input_data/original_data/DAG_Data_flow_new.xlsx'
    All_flow_list = DG.Manual_Input('XLSX', [addr_str])

    for flow_id, flow_x in enumerate(All_flow_list):
        DFA.dag_data_initial(flow_x, DAGType=int(flow_id), DAG_id=int(flow_id), Period=Total_Time, Critic=1)
        DFA.dag_param_critical_update(flow_x)

    flow_num = 4  # 每组 10个DAG
    # core_num = int(2.125 * flow_num) + (2 * flow_num - 1)
    core_num = 10
    DAG1_ID_list = list(set([node_x[1]['Node_ID'] for node_x in All_flow_list[0].nodes(data=True)]))
    DAG2_ID_list = list(set([node_x[1]['Node_ID'] for node_x in All_flow_list[1].nodes(data=True)]))
    preempt_data_list = [
        {'DAG1': {node_id: random.randint(0, All_flow_list[0].number_of_nodes()) for node_id in DAG1_ID_list},
         'DAG2': {node_id: random.randint(0, All_flow_list[0].number_of_nodes()) for node_id in DAG2_ID_list}}
        for _ in range(10)]
    for preempt_data_x in preempt_data_list:
        preempt_data_x['DAG1']['source'] = random.randint(0, All_flow_list[0].number_of_nodes())
        preempt_data_x['DAG1']['sink'] = random.randint(0, All_flow_list[0].number_of_nodes())
        preempt_data_x['DAG2']['source'] = random.randint(0, All_flow_list[0].number_of_nodes())
        preempt_data_x['DAG2']['sink'] = random.randint(0, All_flow_list[0].number_of_nodes())

    for exam in range(1000):
        print(f'test:{exam}')
        # 每次实验初始化
        DAG1 = DG.Algorithm_input('FLOW', {'Flow_set': [All_flow_list[0]], 'flow_num': flow_num, 'WCET_interval': 0.5,
                                           'DAG_Num': 1, 'arrival_interval': [0, 20 * 2260]})[0]
        DFA.dag_data_initial(DAG1, DAGType=int(1), DAG_id=int(1), Period=Total_Time, Critic=1)
        DFA.dag_param_critical_update(DAG1)
        DAG2 = DG.Algorithm_input('FLOW', {'Flow_set': [All_flow_list[1]], 'flow_num': flow_num, 'WCET_interval': 0.5,
                                           'DAG_Num': 1, 'arrival_interval': [0, 20 * 2260]})[0]
        DFA.dag_data_initial(DAG2, DAGType=int(2), DAG_id=int(2), Period=Total_Time, Critic=2)
        DFA.dag_param_critical_update(DAG2)
        tdag_list = [copy.deepcopy(DAG1), copy.deepcopy(DAG2)]
        # （1） 阈值与优先级设置
        DPC.MDAG_Priority_Config('SELF', tdag_list)
        for dag_x in tdag_list:
            for node_x in dag_x.nodes(data=True):
                node_x[1]['PT'] = node_x[1]['Prio']
            DPC.MDAG_Priority_Config('SELF', [dag_x])
        # （2） 先赋优先级再换AFT
        HI_makespan_core_dict = {core_x.Core_ID: core_x for core_x in
                                 LSS.compute_sch_list(copy.deepcopy(DAG1), core_num)}
        min_makespan = Core.ret_makespan(HI_makespan_core_dict)  # 去掉合并后头尾的1
        for dag_x in tdag_list:
            dag_x.graph['block'] = min_makespan
            for node_x in dag_x.nodes(data=True):
                node_x[1]['WCET'] = node_x[1]['AET']

        for _ in range(5):
            print('test')
            ret = []
            for preempt_data_x in preempt_data_list:
                test_dag_list = copy.deepcopy(tdag_list)
                # 初始话生成DAG的抢占变量
                for node_x in test_dag_list[0].nodes(data=True):
                    node_x[1]['PT'] = preempt_data_x['DAG1'][node_x[1]['Node_ID']]
                for node_x in test_dag_list[1].nodes(data=True):
                    node_x[1]['PT'] = preempt_data_x['DAG2'][node_x[1]['Node_ID']]

                Dispatcher = SS.Dispatcher_Workspace(
                    [copy.deepcopy(test_dag_list), {'Core_Num': core_num, 'Total_Time': Total_Time,
                                                    'Enqueue_rank': False, 'Priority_rank': True,
                                                    'Preempt_type': 'type5', 'Dynamic': False}])
                Dispatcher.run()
                SELF_LP_h = Dispatcher.Core_Data_List
                LP_makespan = Core.ret_makespan(SELF_LP_h)
                LP_makespan_c1 = Core.ret_dag_cri_makespan(SELF_LP_h, 1)
                LP_makespan_c2 = Core.ret_dag_cri_makespan(SELF_LP_h, 2)
                LP_workload_rade = 100 * sum([DFA.get_dag_volume(dag_x) for dag_x in test_dag_list]) / sum(
                    [core_x.get_core_last_time() for core_id, core_x in SELF_LP_h.items()])
                LP_c1_surpass_rade = 100 * (LP_makespan_c1 - min_makespan) / LP_makespan_c1

                print(f'LP_makespan:{LP_makespan}', end='\t')
                print(f'LP_makespan_cri_1:{LP_makespan_c1}', end='\t')
                print(f'LP_makespan_cri_2:{LP_makespan_c2}', end='\t')
                print(f'LP_workload_rade:{LP_workload_rade}', end='\t')
                print(f'LP_cri_1 surpass rade:{LP_c1_surpass_rade}')
                ret.append((preempt_data_x, LP_workload_rade, LP_makespan))
            if len(set([(rc[1], rc[2]) for rc in ret])) == 1:
                break
            random.shuffle(ret)
            ret.sort(key=lambda x: x[2], reverse=False)
            ret.sort(key=lambda x: x[1], reverse=True)
            ret = [ret_x[0] for ret_x in ret[:2]]
            # 加4个交叉；
            for _ in range(6):
                ct_data = copy.deepcopy(ret[0])
                for dag_k, dag_dic in ct_data.items():
                    for node_k, node_dic in dag_dic.items():
                        if random.random() > 0.5:
                            ct_data[dag_k][node_k] = ret[0][dag_k][node_k]
                ret.append(ct_data)
            # 搞1个变异；
            for oid in range(2):
                ct_data = copy.deepcopy(ret[oid])
                for dag_k, dag_dic in ct_data.items():
                    for node_k, node_dic in dag_dic.items():
                        if random.random() > 0.95:
                            ct_data[dag_k][node_k] = random.randint(0, DAG1.number_of_nodes())

                ret.append(ct_data)
            preempt_data_list = copy.deepcopy(ret)
    # (1) 排序 ，记录excel
    # (6) 有限抢占方案5-智能搜索加5%抢占(抢占变量)； type7

