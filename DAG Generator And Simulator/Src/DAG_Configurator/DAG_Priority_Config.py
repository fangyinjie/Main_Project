#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Randomized DAG Generator
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################
import random

import networkx as nx
import numpy as np
import copy
import time
# import graphviz as gz

# import DAG_Generator as DG

from . import DAG_Features_Analysis as DFA
# from . import DAG_Generator as DG

def DMDAG_Priority_Config(Priority_Config_type, temp_dag_list):
    temp_dag_list_new = [tdagx.subgraph([node_x[0] for node_x in tdagx.nodes(data=True) if node_x[1]['Status'] != 'Finish']) for tdagx in temp_dag_list ]
    merge_dag = DAG_list_merge(temp_dag_list_new)
    DFA.dag_critical_path_new(merge_dag)
    if Priority_Config_type == "SELF":
        priority_DAG_Struct_Aware_Config(merge_dag)
    Priority_Config('SELF', [merge_dag])
    for node_x in merge_dag.nodes(data=True):
        tnode = node_x[1]['DAG'].nodes[node_x[1]['Node_Index']]
        tnode['Prio'] = node_x[1]['Prio']


def MDAG_Priority_Config(Priority_Config_type, temp_dag_list):
    merge_dag = DAG_list_merge(temp_dag_list)
    DFA.dag_critical_path_new(merge_dag)

    if Priority_Config_type == "SELF":
        priority_DAG_Struct_Aware_Config(merge_dag)
    elif Priority_Config_type == "HEFT":
        priority_blevel_config_brief(merge_dag)
    elif Priority_Config_type == "LFT":
        priority_blevel_config_brief(merge_dag)
    for node_x in merge_dag.nodes(data=True):
        tnode = node_x[1]['DAG'].nodes[node_x[1]['Node_Index']]
        tnode['Prio'] = node_x[1]['Prio']


def Priority_Config(Priority_Config_type, temp_dag_x):
    if Priority_Config_type == "random":
        priority_random_config(temp_dag_x)
    elif Priority_Config_type == "WCET":
        priority_WCET_config(temp_dag_x)
    elif Priority_Config_type == "Zhao":
        priority_Zhao_config(temp_dag_x)
    elif Priority_Config_type == "SELF":
        priority_DAG_Struct_Aware_Config(temp_dag_x)
    elif Priority_Config_type == "HEFT":
        priority_blevel_config_brief(temp_dag_x)
    elif Priority_Config_type == "He_2019":
        priority_He_2019_config(temp_dag_x)
    elif Priority_Config_type == "He_2021":
        priority_He_2021_config(temp_dag_x)
    elif Priority_Config_type == "HUAWEI":      # ( HUAWEI ID )
        priority_HUAWEI_config(temp_dag_x)
    elif Priority_Config_type == "LFT":
        priority_lft_config_brief(temp_dag_x)
    elif Priority_Config_type == "LPA":
        # priority_HUAWEI_config(temp_dag_x)
        pass
    else:
        print("priority config error!\n")

    # elif Priority_Config_type == "SJF":
    #     priority_SJF_config(temp_dag_list)
    # elif Priority_Config_type == "APB":
    #     priority_APB_config(temp_dag_list)


def priority_HUAWEI_config(DAG_x):
    prio_dict = {'start': 1, 'end': 1, 'source': 1, 'sink': 1, 'Job_0': 1, 'Job_1': 2, 'Job_3.2': 3, 'Job_3.3': 3,
                 'Job_3.1': 3, 'Job_7': 3, 'Job_35': 1, 'Job_36': 2, 'Job_4': 2, 'Job_4.1': 2, 'Job_4.2': 2, 'Job_4.3': 2,
                 'Job_4.4': 2, 'Job_4.5': 2,  'Job_4.6': 2, 'Job_4.7': 2, 'Job_10': 1,  'Job_11': 1, 'Job_12': 1}
    for node_x in DAG_x.nodes(data=True):
        node_x[1]['Prio'] = prio_dict[ node_x[1]['Node_ID'] ]

def priority_Zhao_config(temp_dag_x):
    pass

def priority_He_2021_config(temp_dag_x):
    temp_node_list = list(nx.topological_sort(temp_dag_x))
    temp_node_list = sorted(temp_node_list, key=lambda x: temp_dag_x.nodes[x]['length'], reverse=True)
    for priox, node_id in enumerate(temp_node_list):
        temp_dag_x.nodes[node_id]['Prio'] = priox


def TPDS_Assign_Priority(temp_dag_x, l, lf, lb, Prio, p):
    # note: p is assigned as array to be able to pass by reference! Only p[0] is used.
    # V = list(copy.deepcopy(temp_dag_x).nodes())
    G_copy = copy.deepcopy(temp_dag_x)
    while len(list(G_copy.nodes())) > 0:
        temp_v_list = [node_x for node_x in G_copy.nodes(data=True) if len(list(G_copy.predecessors(node_x[0]))) == 0]
        random.shuffle(temp_v_list)
        temp_v_list = sorted(temp_v_list, key=lambda x: x[1]['length'], reverse=True)
        v = temp_v_list[0][0]
        Prio[v] = p[0];
        p[0] = p[0] + 1;
        A = list(G_copy.successors(v))  # priority assignment
        G_copy.remove_node(v)  # removing v and its related edges
        while len(A) > 0:  # iterates A
            A_node_list = [(a_x, G_copy.nodes[a_x]) for a_x in A]
            random.shuffle(A_node_list)
            A_node_list = sorted(A_node_list, key=lambda x: x[1]['B-level'], reverse=True)
            A_node_list = sorted(A_node_list, key=lambda x: x[1]['length'], reverse=True)
            v = A_node_list[0]  # TPDS_max_l_max_lb(l, lb, A)
            if len(list(G_copy.predecessors(v[0]))) > 0:
                ans_v = list(nx.ancestors(G_copy, v[0]))
                G_prime = G_copy.subgraph(ans_v).copy()
                TPDS_Assign_Priority(G_prime, l, lf, lb, Prio, p)
                for ans_v_x in ans_v:
                    G_copy.remove_node(ans_v_x)
            Prio[v[0]] = p[0];
            p[0] = p[0] + 1;
            A = list(G_copy.successors(v[0]))
            G_copy.remove_node(v[0])


def priority_He_2019_config(temp_dag_x):
    # 1. Procedure compute length
    l = {node_x[0]: node_x[1]['length'] for node_x in temp_dag_x.nodes(data=True)}
    lf = {node_x[0]: node_x[1]['T-level'] for node_x in temp_dag_x.nodes(data=True)}
    lb = {node_x[0]: node_x[1]['B-level'] for node_x in temp_dag_x.nodes(data=True)}
    # 2. Procedure assign priority
    prio = {}
    p_next = [0]
    TPDS_Assign_Priority(temp_dag_x, l, lf, lb, Prio=prio, p=p_next)
    for node_x in temp_dag_x.nodes(data=True):
        node_x[1]['Prio'] = prio[node_x[0]]
    return prio


########################################################
# (1) Priority Algorithm Based on Structure Perception #
########################################################
def priority_DAG_Struct_Aware_Config(temp_dag):
    assert format(nx.is_directed_acyclic_graph(temp_dag))  # 判断是否是DAG
    for node_x in temp_dag.nodes(data=True):
        node_x[1]['Group'] = 0
    temp_node_list = list(nx.topological_sort(temp_dag))
    temp_dag.nodes[temp_node_list.pop(0)]['Group'] = 1
    for node_x_id in temp_node_list:
        if temp_dag.nodes[node_x_id]['critic']:
            temp_dag.nodes[node_x_id]['Group'] = 1 + max(map(lambda x: temp_dag.nodes[x]['Group'],
                                                             temp_dag.predecessors(node_x_id)))
    reversed_dag = temp_dag.reverse()
    temp_node_list = list(nx.topological_sort(reversed_dag))
    for node_x_id in temp_node_list:
        if not temp_dag.nodes[node_x_id]['critic']:
            temp_dag.nodes[node_x_id]['Group'] = min(map(lambda x: temp_dag.nodes[x]['Group'], filter(lambda x: temp_dag.nodes[x]['critic'], nx.descendants(temp_dag, node_x_id)))) - 1

    t_g = [node_x for node_x in temp_dag.nodes(data=True)]
    t_g = sorted(t_g, key=lambda x: x[0], reverse=False)
    t_g = sorted(t_g, key=lambda x: x[1]['critic'], reverse=True)
    t_g = sorted(t_g, key=lambda x: x[1]['WCET'], reverse=True)
    t_g = sorted(t_g, key=lambda x: x[1]['B-level'], reverse=True)
    t_g = sorted(t_g, key=lambda x: x[1]['Group'], reverse=False)
    # t_g = sorted(t_g, key=lambda x: x[1]['L_L_F'], reverse=False)
    # t_g = sorted(t_g, key=lambda x: x[1]['DAG'].out_degree(x[0]), reverse=True)
    for sx, tgx in enumerate(t_g):
        tgx[1]['Prio'] = sx


###########################################
# #### (2) Random priority algorithm #### #
###########################################
def priority_random_config(temp_dag_list):
    priority_random_list = list(range(0, temp_dag_list.number_of_nodes()))
    np.random.shuffle(priority_random_list)
    for x in temp_dag_list.nodes(data=True):
        x[1]['Prio'] = priority_random_list.pop()


################################
# #### (3) long job first #### #
################################
def priority_WCET_config(temp_dag):
    temp_node_wcet = nx.get_node_attributes(temp_dag, 'WCET')
    temp_node_wcet = dict(sorted(temp_node_wcet.items(), key=lambda x: x[1], reverse=True))
    Temp_1 = 1
    for k, v in temp_node_wcet.items():
        temp_dag.nodes[k]['Prio'] = Temp_1
        Temp_1 += 1
    return False


#################################
# #### (4) short job first #### #
#################################
def priority_SJF_config(temp_dag):
    temp_node_sjf = nx.get_node_attributes(temp_dag, 'WCET')
    temp_node_sjf = dict(sorted(temp_node_sjf.items(), key=lambda x: x[1], reverse=False))
    Temp_1 = 1
    for k, v in temp_node_sjf.items():
        temp_dag.nodes[k]['Prio'] = Temp_1
        Temp_1 += 1
    return False


######################
# #### (5) HEFT #### #
######################
def priority_blevel_config_brief(temp_dag):
    node_list = [nodex for nodex in temp_dag.nodes(data=True)]
    node_list = sorted(node_list, key=lambda x: x[1]['B-level'], reverse=True)
    for pri_x, nodex in enumerate(node_list):
        nodex[1]['Prio'] = pri_x


######################
# #### (5) HEFT #### #
######################
def priority_lft_config_brief(temp_dag):
    node_list = [nodex for nodex in temp_dag.nodes(data=True)]
    node_list = sorted(node_list, key=lambda x: x[1]['L_L_F'], reverse=False)
    for pri_x, nodex in enumerate(node_list):
        nodex[1]['Prio'] = pri_x

#####################
# #### (6) APB #### #
#####################
def priority_APB_config(temp_dag):
    head_node = None
    for tdn_x in temp_dag.nodes():  # 得到头结点和尾结点，赋PQ值=0
        if len(list(temp_dag.predecessors(tdn_x))) == 0:
            head_node = tdn_x
        if len(list(temp_dag.successors(tdn_x))) == 0:
            temp_dag.nodes[tdn_x]["PQ"] = 0

    DFS_blevel(temp_dag, head_node)  # 计算出口长度LQ

    for k in temp_dag:
        temp_dag.nodes[k]["LQ"] = temp_dag.nodes[k]["blevel"]  # 计算到出口长度LQ和后继节点数量RQ
        temp_dag.nodes[k]["RQ"] = len(list(temp_dag.successors(k)))
    # 深度优先搜索 求PQ
    DFS_APB(temp_dag, head_node)
    temp_dag.nodes[head_node]["PQ"] = 0
    # 排序，LQ大 RQ大 PQ大赋优先级
    temp_node_apb = nx.get_node_attributes(temp_dag, 'PQ')
    temp_node_apb = dict(sorted(temp_node_apb.items(), key=lambda x: x[1], reverse=True))
    temp_node_apb = nx.get_node_attributes(temp_dag, 'RQ')
    temp_node_apb = dict(sorted(temp_node_apb.items(), key=lambda x: x[1], reverse=True))
    temp_node_apb = nx.get_node_attributes(temp_dag, 'LQ')
    temp_node_apb = dict(sorted(temp_node_apb.items(), key=lambda x: x[1], reverse=True))
    Temp_1 = 1
    for k, v in temp_node_apb.items():
        temp_dag.nodes[k]['Prio'] = Temp_1
        Temp_1 += 1
    return False


def DFS_blevel(temp_dag, node):
    if len(list(temp_dag.successors(node))) == 0:
        return 0
    children = list(temp_dag.successors(node))
    max = 0
    for tdn_x in children:
        temp_dag.nodes[tdn_x]["blevel"] = temp_dag.nodes[tdn_x]["WCET"] + DFS_blevel(temp_dag, tdn_x)
        if max < temp_dag.nodes[tdn_x]["blevel"]:
            max = temp_dag.nodes[tdn_x]["blevel"]
    temp_dag.nodes[node]["blevel"] = temp_dag.nodes[node]["WCET"] + max
    return temp_dag.nodes[node]["blevel"]


def DFS_APB(temp_dag, node):
    if len(list(temp_dag.successors(node))) == 0:
        return 0

    children = list(temp_dag.successors(node))
    temp_dag.nodes[node]["PQ"] = 0
    for tdn_x in children:
        if (not "PQ" in temp_dag.nodes[tdn_x]) or temp_dag.nodes[tdn_x]["PQ"] == 0:
            DFS_APB(temp_dag, tdn_x)
        temp_dag.nodes[node]["PQ"] += (temp_dag.nodes[tdn_x]["PQ"] + temp_dag.nodes[tdn_x]["WCET"]) / len(list(temp_dag.predecessors(tdn_x)))
    return 0


# 需要node参数有DAG参数
def DAG_list_merge(Intput_DAG_set):
    dag_id = ''
    temp_dag = nx.DiGraph()
    for in_dag_x in Intput_DAG_set:
        dag_id += in_dag_x.graph['DAG_ID'] + '-'
        temp_dag = nx.disjoint_union(in_dag_x, temp_dag)

    p_node_list = [node_x for node_x in temp_dag.nodes() if temp_dag.in_degree(node_x) == 0]
    source_node_num = len(list(temp_dag.nodes()))
    temp_dag.add_node(source_node_num, Node_Index=source_node_num, Node_ID='source', name='source', WCET=1, Prio=0, ET=0, DAG=temp_dag, critic=True, Status='Finish')
    for pnodex in p_node_list:
        temp_dag.add_edge(source_node_num, pnodex)

    s_node_list = [node_x for node_x in temp_dag.nodes() if temp_dag.out_degree(node_x) == 0]
    sink_node_num = len(list(temp_dag.nodes()))
    temp_dag.add_node(sink_node_num, Node_Index=sink_node_num, Node_ID='sink', name='sink', WCET=1, Prio=0, ET=0, DAG=temp_dag, critic=True, Status='Finish')
    for snodex in s_node_list:
        temp_dag.add_edge(snodex, sink_node_num)

    temp_dag.graph['DAG_ID'] = dag_id
    return temp_dag


# def priority_Zhao_config(temp_dag_list):

# def priority_He2021_config(temp_dag_list):

# def priority_Mine_config(temp_dag_list):

# def Priority_Press(temp_dag_list, priority_num):
#     # (1) 每个结点设为一个集合；
#     # (2) 集合中的结点权重相同，且WCET相同则合并；
#     # (3) 支配节点组最高优先级集合与前驱节点组最低优先级集合合并
#     pass

# def priority_DAG_Struct_Aware_Config(temp_dag):
#     assert format(nx.is_directed_acyclic_graph(temp_dag))     # 判断是否是DAG
#     DFA.dag_critical_path(temp_dag)
#     curr_time_s = time.time()
#     temp_dag_c = copy.deepcopy(temp_dag)
#     curr_time_e = time.time()
#     print(f'dag_id:{temp_dag.graph["DAG_ID"]}___TEST delay : {1000 * 1000 * (curr_time_e - curr_time_s)} us')
#
#     group_num = 0
#     while temp_dag_c.number_of_nodes() > 0:
#         nullo_cpnode_list = [node_x for node_x in temp_dag_c.nodes(data=True) if node_x[1]['critic'] and
#                               temp_dag_c.out_degree(node_x[0]) == 0 ]
#         for no_cpn_x in nullo_cpnode_list:
#             temp_dag.nodes[no_cpn_x[0]]['Group'] = group_num
#             temp_dag_c.remove_node(no_cpn_x[0])
#         group_num += 1
#         while True:
#             nullo_node_list = [node_x for node_x in temp_dag_c.nodes(data=True) if
#                                node_x[1]['critic'] == False and temp_dag_c.out_degree(node_x[0]) == 0 ]
#             if len(nullo_node_list) == 0:
#                 break
#             for non_x in nullo_node_list:
#                 temp_dag.nodes[non_x[0]]['Group'] = group_num
#                 temp_dag_c.remove_node(non_x[0])
#
#     curr_time_s = time.time_ns()
#
#     t_g = [node_x for node_x in temp_dag.nodes(data=True)]
#     t_g = sorted(t_g, key=lambda x: x[1]['critic'], reverse=True)
#     t_g = sorted(t_g, key=lambda x: x[1]['WCET'], reverse=True)
#     t_g = sorted(t_g, key=lambda x: x[1]['sub_cpath'], reverse=True)
#     t_g = sorted(t_g, key=lambda x: x[1]['Group'], reverse=True)
#
#     curr_time_e = time.time_ns()
#     print(f'dag_id:{temp_dag.graph["DAG_ID"]}___TEST delay : {curr_time_e - curr_time_s} ns')
#
#     for sx, tgx in enumerate(t_g):
#         tgx[1]['Prio'] = sx     # tgx[1]['DAG'].nodes[tgx[1]['Node_Index']]['Group'] = tgx[1]['Group']
