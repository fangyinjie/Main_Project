#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Randomized DAG Generator
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################
import copy

import networkx as nx
import numpy as np
from . import DAG_WCET_Config as DWC    # 引入同一目录下的文件  from . import xxx
# from . import DAG_Generator as DG


# # #### (1) Get the median of DAG (中位数)#### #
def get_dag_median(DAG_obj):
    node_c = DAG_obj.number_of_nodes()
    wcet_list = sorted([node_x[1]['WCET'] for node_x in DAG_obj.nodes(data=True)])
    index = int(node_c / 2)
    if len(wcet_list) % 2 == 0:
        return (wcet_list[index] + wcet_list[index - 1]) / 2
    else:
        return wcet_list[index]



# # #### (2) Get the volume of DAG (workload)#### #
def get_dag_volume(DAG_obj):
    return sum([node_x[1]['WCET'] for node_x in DAG_obj.nodes(data=True)])


# # #### (3) The Rate Critical path of  volume #### #
def get_Rate_of_Cri_to_volume(DAG_obj):
    test_dag = copy.deepcopy(DAG_obj)
    dag_volume = get_dag_volume(test_dag)
    dag_critical_path_new(test_dag)
    cri_volume = sum([node_x[1]['WCET'] for node_x in test_dag.nodes(data=True) if node_x[1]['critic'] == True])
    return cri_volume/dag_volume

# # #### (4) The Rate Critical path of  volume #### #
def get_dag_jiter_comput(dag_obj):
    ret = 0.0
    node_num = 0
    for node_x in dag_obj.nodes(data=True):
        if node_x[1]['Node_ID'] == 'source' or node_x[1]['Node_ID'] == 'sink' or node_x[1]['Node_ID'] == 'start' or node_x[1]['Node_ID'] == 'end':
            continue
        ret += abs(node_x[1]['ET'] - node_x[1]['WCET']) / node_x[1]['WCET']
        node_num += 1
    return ret/node_num


# # #### (*) Get the entropy of DAG  #### #
# def get_dag_entropy(DAG_obj):
#   pass

# # #### (*) Communicate the similarity of the dag list #### #
# def get_similarity(DAG_list):
#   pass

#####################################
# todo Section_0: DAG Basic function
#####################################
# #### Gets the nodes in the ready state of the DAG #### #
# def get_ready_node_list(temp_DAG_list, run_list, ready_list):
#     temp_ready_list = [(ready_node_x[0], ready_node_x[1][0]) for ready_node_x in ready_list]
#     ret_list = []
#     for temp_DAG_x in temp_DAG_list:
#         ret_list += [(temp_DAG_x.graph['DAG_ID'], x) for x in temp_DAG_x.nodes(data=True) if
#                      (len(list(temp_DAG_x.predecessors(x[0]))) == 0) and
#                      ((temp_DAG_x.graph['DAG_ID'], x[0]) not in run_list) and
#                      ((temp_DAG_x.graph['DAG_ID'], x[0]) not in temp_ready_list)]
#     return ret_list


# # #### get the amount of node in the DAG #### #
# def get_node_num(temp_DAG_list):
#     node_num = 0
#     for temp_DAG_x in temp_DAG_list:
#         node_num += temp_DAG_x.number_of_nodes()
#     return node_num


def dag_critical_path_new(temp_dag):
    assert nx.is_directed_acyclic_graph(temp_dag)
    precision = 3
    # T-level
    temp_node_list = list(nx.topological_sort(temp_dag))
    for nid in temp_node_list:
        nodel = list(temp_dag.predecessors(nid))
        if len(nodel) == 0:
            temp_dag.nodes[nid]['T-level'] = temp_dag.nodes[nid]['WCET']
        else:
            temp_dag.nodes[nid]['T-level'] = max([temp_dag.nodes[nx_id]['T-level'] for nx_id in nodel]) + temp_dag.nodes[nid]['WCET']
    # B-level
    temp_re_node_list = reversed(list(nx.topological_sort(temp_dag)))
    for nid in temp_re_node_list:
        nodel = list(temp_dag.successors(nid))
        if len(nodel) == 0:
            temp_dag.nodes[nid]['B-level'] = temp_dag.nodes[nid]['WCET']
        else:
            temp_dag.nodes[nid]['B-level'] = max([temp_dag.nodes[nx_id]['B-level'] for nx_id in nodel]) + temp_dag.nodes[nid]['WCET']

    # length
    for node_x in temp_dag.nodes(data=True):
        node_x[1]['length'] = round(node_x[1]['B-level'] + node_x[1]['T-level'] - node_x[1]['WCET'], precision)

    # critic
    critical_path_length = round(max([node_x[1]['length'] for node_x in temp_dag.nodes(data=True)]), precision)
    for node_x in temp_dag.nodes(data=True):
        if node_x[1]['length'] == critical_path_length:
            node_x[1]['critic'] = True
        else:
            node_x[1]['critic'] = False

    # E_S_T
    temp_node_list = list(nx.topological_sort(temp_dag))
    for node_x_id in temp_node_list:
        if temp_dag.in_degree(node_x_id) == 0:
            temp_dag.nodes[node_x_id]['E_S_T'] = 0
            temp_dag.nodes[node_x_id]['E_F_T'] = temp_dag.nodes[node_x_id]['WCET']
        else:
            temp_dag.nodes[node_x_id]['E_S_T'] = max([temp_dag.nodes[pnode]['E_S_T'] + temp_dag.nodes[node_x_id]['WCET'] for pnode in temp_dag.predecessors(node_x_id)])
            temp_dag.nodes[node_x_id]['E_F_T'] = temp_dag.nodes[node_x_id]['E_S_T'] + temp_dag.nodes[node_x_id]['WCET']

    # L_S_T
    temp_re_node_list = reversed(list(nx.topological_sort(temp_dag)))
    for node_x_id in temp_re_node_list:
        if temp_dag.out_degree(node_x_id) == 0:
            temp_dag.nodes[node_x_id]['L_S_T'] = temp_dag.nodes[node_x_id]['E_S_T']
        else:
            temp_dag.nodes[node_x_id]['L_S_T'] = min([temp_dag.nodes[snode]['L_S_T'] for snode in temp_dag.successors(node_x_id)]) - temp_dag.nodes[node_x_id]['WCET']
    # L_L_F
    for node_x in temp_dag.nodes(data=True):
        node_x[1]['L_L_F'] = node_x[1]['L_S_T'] - node_x[1]['E_S_T']


def dag_data_initial(DAG_obj, DAGType, DAG_id, Period, Cycle=1, DAGInstID=0, Critic=0, Arrive_time=0):
    np_nodes = [nodex for nodex in DAG_obj.nodes() if len(list(DAG_obj.predecessors(nodex))) == 0]
    ns_nodes = [nodex for nodex in DAG_obj.nodes() if len(list(DAG_obj.successors(nodex))) == 0]
    if len(np_nodes) != 1:
        source_ni = max([nx for nx in DAG_obj.nodes()]) + 1  # DAG_obj.number_of_nodes() + 1
        DAG_obj.add_node(source_ni, JobTypeID='Source', Node_ID='Source', DAG=DAG_obj, BCET=0, AVET=0, WCET=0, WCET_old=0, Prio=1,
                         Node_Index=source_ni, RANDOM=0, Flow_Num=0, EDIT_ID='Source', PT=0)  # 'Node_Indes'
        for npx in np_nodes:
            DAG_obj.add_edge(source_ni, npx)
    assert len([nodex for nodex in DAG_obj.nodes() if len(list(DAG_obj.predecessors(nodex))) == 0]) == 1  # one source

    if len(ns_nodes) != 1:
        sink_ni = max([nx for nx in DAG_obj.nodes()]) + 1   # DAG_obj.number_of_nodes() + 1
        DAG_obj.add_node(sink_ni, JobTypeID='Sink', Node_ID='Sink', DAG=DAG_obj, BCET=0, AVET=0, WCET=0, WCET_old=0, Prio=1,
                         Node_Index=sink_ni, RANDOM=0, Flow_Num=0, EDIT_ID='Sink', PT=0)  # 'Node_Indes'
        for nsx in ns_nodes:
            DAG_obj.add_edge(nsx, sink_ni)

    assert len([nodex for nodex in DAG_obj.nodes() if len(list(DAG_obj.successors(nodex))) == 0]) == 1    # one sink

    DAG_obj.graph['DAG_ID']         = str(DAGType)
    DAG_obj.graph['DAGType']        = str(DAGType)      # 1 level
    DAG_obj.graph['DAGTypeID']      = int(DAG_id)       # 1 level
    DAG_obj.graph['DAGInst']        = str(DAGInstID)    # 2 level
    DAG_obj.graph['DAGInstID']      = int(DAGInstID)    # 2 level

    DAG_obj.graph['Criticality']    = int(Critic)
    DAG_obj.graph['CriticalityID']  = str(Critic)

    DAG_obj.graph['SlotLen']            = float(Arrive_time)
    DAG_obj.graph['DAGsubmitOffset']    = float(Arrive_time)
    DAG_obj.graph['Arrive_time']        = float(Arrive_time)
    DAG_obj.graph['Period']             = float(Period)

    DAG_obj.graph['Cycle']              = int(Cycle)       # 执行的周期数量
    DAG_obj.graph['DDL']                = float(Period)

    DAG_obj.graph['Median']             = get_dag_median(DAG_obj)
    DAG_obj.graph['Volume']             = get_dag_volume(DAG_obj)
    DAG_obj.graph['CriVolumeRate']      = get_Rate_of_Cri_to_volume(DAG_obj)

    DAG_obj.graph['block']              = 0
    DAG_obj.graph['FP_Makespan']        = 0

    for node_x in DAG_obj.nodes(data=True):
        node_x[1]['DAG'] = DAG_obj
        node_x[1]["Status"] = 'Block'
        node_x[1]['Criticality'] = Critic
        node_x[1]['WCET'] = float(node_x[1]['WCET'])
        node_x[1]['ACET'] = float(node_x[1]['WCET'])
        node_x[1]['BCET'] = float(node_x[1]['WCET'])
        node_x[1]['AET']  = float(node_x[1]['WCET'])


# ########################################################################
# Key parameter analysis & update for DAG
# Input: DAG with no attribute parameter
#       assume(1)： There's only one source node;
#       assume(2)： There's only one sink node;
# Output: Give the DAG with attribute parameter
# ########################################################################
def dag_param_critical_update(DAG_obj):
    # #### 2.1 shape #### #
    rank_list = [sorted(generation) for generation in nx.topological_generations(DAG_obj)]
    rank_num_list = [len(x) for x in rank_list]
    for rank_id, rank_l in enumerate(rank_list):
        for rank_x in rank_l:
            DAG_obj.nodes[rank_x]['rank'] = rank_id
    DAG_obj.graph['Shape_List'] = rank_num_list
    DAG_obj.graph['Ave_Shape'] = np.mean(rank_num_list)
    DAG_obj.graph['Std_Shape'] = np.std(rank_num_list)
    DAG_obj.graph['Max_Shape'] = max(rank_num_list)
    DAG_obj.graph['Min_Shape'] = min(rank_num_list)
    DAG_obj.graph['Number_Of_Level'] = len(rank_num_list)

    # #### 2.2 re-shape #### #
    re_rank_list = [sorted(generation) for generation in nx.topological_generations(nx.DiGraph.reverse(DAG_obj))]
    re_rank_list.reverse()
    re_rank_num_list = [len(x) for x in re_rank_list]

    DAG_obj.graph['Re_Shape_List'] = re_rank_num_list
    DAG_obj.graph['Ave_Re_Shape'] = np.mean(re_rank_num_list)
    DAG_obj.graph['Std_Re_Shape'] = np.std(re_rank_num_list)
    DAG_obj.graph['Max_Re_Shape'] = max(re_rank_num_list)
    DAG_obj.graph['Min_Re_Shape'] = min(re_rank_num_list)

    # #### 3.antichains #### #
    # anti_chains_list = list(nx.antichains(DAG_obj, topo_order=None))  # 3. "Width"
    # anti_chains_num_list = [len(x) for x in anti_chains_list]
    # DAG_obj.graph['Width'] = max(anti_chains_num_list)
    # temp_G1 = nx.transitive_closure(DAG_obj, reflexive=None)
    # temp_G1 = nx.transitive_reduction(DAG_obj)
    # temp_G3 = nx.maximal_matching(temp_G2)
    # temp_G4 = nx.min_edge_cover(temp_G2)
    # width_2 = nx.number_connected_components(temp_G2)
    # temp_G5 = nx.bipartite.maximum_matching(temp_G2)

    temp_G1 = nx.transitive_closure_dag(DAG_obj)
    temp_G2 = nx.DiGraph()
    for edge_x in temp_G1.edges():
        temp_G2.add_node('p' + str(edge_x[0]), bipartite=0)
        temp_G2.add_node('d' + str(edge_x[1]), bipartite=1)
        temp_G2.add_edge('p' + str(edge_x[0]), 'd' + str(edge_x[1]))
    u = [n for n in temp_G2.nodes if temp_G2.nodes[n]['bipartite'] == 0]
    matching = nx.bipartite.maximum_matching(temp_G2, top_nodes=u)
    DAG_obj.graph['Width'] = DAG_obj.number_of_nodes() - len(matching) / 2

    # #### 4.1 Degree #### #
    degree_list = [nx.degree(DAG_obj, self_node[0]) for self_node in DAG_obj.nodes(data=True)]
    DAG_obj.graph['Max_Degree'] = max(degree_list)
    DAG_obj.graph['Min_Degree'] = min(degree_list)
    DAG_obj.graph['Ave_Degree'] = np.mean(degree_list)
    DAG_obj.graph['Std_Degree'] = np.std(degree_list)

    # #### 4.2 In-Degree #### #
    degree_in_list = [DAG_obj.in_degree(self_node[0]) for self_node in DAG_obj.nodes(data=True)]
    DAG_obj.graph['Max_In_Degree'] = max(degree_in_list)
    DAG_obj.graph['Min_In_Degree'] = min(degree_in_list)
    DAG_obj.graph['Ave_In_Degree'] = np.mean(degree_in_list)
    DAG_obj.graph['Std_In_Degree'] = np.std(degree_in_list)

    # #### 4.3 Out-Degree #### #
    degree_out_list = [DAG_obj.out_degree(self_node[0]) for self_node in DAG_obj.nodes(data=True)]
    DAG_obj.graph['Max_Out_Degree'] = max(degree_out_list)
    DAG_obj.graph['Min_Out_Degree'] = min(degree_out_list)
    DAG_obj.graph['Ave_Out_Degree'] = np.mean(degree_out_list)
    DAG_obj.graph['Std_Out_Degree'] = np.std(degree_out_list)

    # #### 5. Density of DAG  #### #
    Dag_density = (2 * DAG_obj.number_of_edges()) / (DAG_obj.number_of_nodes() * (DAG_obj.number_of_nodes() - 1))
    DAG_obj.graph['Connection_Rate'] = Dag_density      # 2 * nx.density(DAG_obj)

    # #### 6.Jump level  #### #
    Edges_Jump_List = [DAG_obj.nodes[x[1]]['rank'] - DAG_obj.nodes[x[0]]['rank'] for x in DAG_obj.edges.data()]
    DAG_obj.graph['Jump_Level'] = max(Edges_Jump_List)  # 6 "Connection_Rate"

    # #### 7.WCET  #### #
    WCET_list = [x[1]['WCET'] for x in DAG_obj.nodes.data(data=True)]
    DAG_obj.graph['DAG_volume'] = int(np.sum(WCET_list))
    DAG_obj.graph['Max_WCET'] = float(max(WCET_list))
    DAG_obj.graph['Min_WCET'] = float(min(WCET_list))
    DAG_obj.graph['Ave_WCET'] = float(np.mean(WCET_list))
    DAG_obj.graph['Std_WCET'] = float(np.std(WCET_list))


    # #### 8.critical path configuration #### #
    dag_critical_path_new(DAG_obj)


#####################################
#   DAG_self-inspection
#####################################
def dag_self_checking(DAG_obj, DAG_Critical_Param, Algorithm):
    assert format(nx.is_directed_acyclic_graph(DAG_obj))
    if Algorithm == 'MINE':
        assert DAG_Critical_Param['Node_Num'] == DAG_obj.graph['Number_Of_Nodes']
        assert DAG_Critical_Param['Critic_Path'] == DAG_obj.graph['Number_Of_Level']
        assert DAG_Critical_Param['Jump_level'] == DAG_obj.graph['Jump_Level']
        assert DAG_Critical_Param['Conn_ratio'] >= DAG_obj.graph['Connection_Rate']
        assert DAG_Critical_Param['Max_in_degree'] >= DAG_obj.graph['Max_In_Degree']
        assert DAG_Critical_Param['Max_out_degree'] >= DAG_obj.graph['Max_Out_Degree']
        assert DAG_Critical_Param['Max_Shape'] >= DAG_obj.graph['Max_Shape']
        assert DAG_Critical_Param['Min_Shape'] <= DAG_obj.graph['Min_Shape']
        # assert DAG_Critical_Param['Width'] == DAG_obj.graph['Width']


if __name__ == "__main__":
    DAG_addr = 'D:/github/DAG_Scheduling_Summary/Exam_Input_data/xlsx_data/wireless/DAG_Data.xlsx'
    # All_DAG_list = DG.Manual_Input('HAISI', ['./Exam_data/haisi_data/DAG1.xlsx'])
    All_DAG_list = DG.Manual_Input('XLSX', [DAG_addr])
    # ############ WCET_Config ############## #
    for dag_x in All_DAG_list:
        DWC.WCET_Config(dag_x, 'Uniform', Virtual_node=True, a=10000, b=100)
    # ############ critical_Config ############## #
    for dag_x in All_DAG_list:
        dag_param_critical_update(dag_x, 'test')

    for dag_x in All_DAG_list:
        print('The median of DAG-{0}:{1}'.format(dag_x.graph['DAG_ID'], get_dag_median(dag_x)))
        print('The volume of DAG-{0}:{1}'.format(dag_x.graph['DAG_ID'], get_dag_volume(dag_x)))
    # print('The number of DAG_list:{0}'.format(get_dag_list_node_num(All_DAG_list)))
