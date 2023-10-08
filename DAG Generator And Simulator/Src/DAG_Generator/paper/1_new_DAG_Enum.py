#!/usr/bin/python3
# -*- coding: utf-8 -*-
import copy
# # # # # # # # # # # # # # # #
# Randomized DAG Generator
# Create Time: 2023/9/1921:20
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
# # # # # # # # # # # # # # # #
import os
import math
import time
import itertools
import networkx as nx


# # # # # # # # # # # # # # # #
# (1) combination
# A000041
# 1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135, 176, 231, 297, 385, 490, 627, 792, 1002, 1255, 1575, 1958,
# 2436, 3010, 3718, 4565, 5604, 6842, 8349, 10143, 12310, 14883, 17977, 21637, 26015, 31185, 37338, 44583, 53174, 63261,
# 75175, 89134, 105558, 124754, 147273, 173525
# # # # # # # # # # # # # # # #
def combination_exhaustion(node_num,
                           level_min=1, level_max=float('Inf'),
                           shape_min=1, shape_max=float('Inf')):
    assert (level_max >= level_min >= 1) and (shape_max >= shape_min >= 1)
    ret_list = []
    if level_min == 1:
        if shape_min <= node_num <= shape_max:
            ret_list.append([node_num])
    if level_max > 1:
        for X_i in range(shape_min, min(int(node_num/2), shape_max)+1):
            X_ipp = node_num - X_i
            sat_list = combination_exhaustion(X_ipp, max(level_min-1, 1), level_max-1, X_i, shape_max)
            ret_list += [[X_i] + sat_x for sat_x in sat_list]
            # for sat_x in sat_list:
            #     ret_list.append([X_i] + sat_x)
    return ret_list


# # # # # # # # # # # # # # # #
# (2) permutation
# A000079		Powers of 2: a(n) = 2^n.
# 2, 4, 8, 16, 32, 64, 128
# 输入 combination不同的组合；
# 根据组合合成不同的排序；不同的组合一定无法得到同样的排列；
# # # # # # # # # # # # # # # #
def permutation_exhaustion_total(CShapeList):
    ret_list = []
    for CShapex in CShapeList:
        ret_list += permutation_exhaustion(CShapex, 1)
    return ret_list

def permutation_exhaustion(CShape, sh_pre, out_degree=float('Inf')):
    ret_list = []
    for X_i in list(set(CShape)):
        if X_i <= sh_pre * out_degree:
            if len(CShape) == 1:
                ret_list.append([X_i])
            else:
                NShape = copy.deepcopy(CShape)
                NShape.remove(X_i)
                sat_list = permutation_exhaustion(NShape, X_i, out_degree)
                ret_list += [[X_i] + sat_x for sat_x in sat_list]
    return ret_list


# # # # # # # # # # # # # # # #
# (3) connection
# # # # # # # # # # # # # # # #
def gen_mine_new(all_shape_list):
    ret_dag_list = []
    for shape_num_list in all_shape_list:
        shape_list = shape_list_trance(shape_num_list)
        dag_list = [nx.DiGraph()]
        for level_id, self_node_list in enumerate(shape_list):
            if (level_id + 1) == len(shape_list):
                for dag_x in dag_list:
                    p_nodes = [nodex for nodex in dag_x.nodes() if len(list(dag_x.successors(nodex))) == 0]
                    dag_x.add_nodes_from([(self_node_list[0], {'level_num': level_id})])

                    for p_node_x in p_nodes:
                        dag_x.add_edge(p_node_x, self_node_list[0])
            else:
                temp_dag_list = []
                for dag_x in dag_list:
                    temp_dag_list += shape_dag_generator(dag_x, self_node_list, level_id)
                dag_list = temp_dag_list
        ret_dag_list += dag_list
    return ret_dag_list


# #### DAG generator new mine 算法  #### #
def __gen_mine_new(Param_Dict):
    node_num = Param_Dict['Node_Num']
    all_shape_list = shape_enumator(node_num, [1])
    ret_dag_list = []
    for shape_num_list in all_shape_list:
        shape_list = shape_list_trance(shape_num_list)
        dag_list = [nx.DiGraph()]
        for level_id, self_node_list in enumerate(shape_list):
            if (level_id + 1) == len(shape_list):
                for dag_x in dag_list:
                    p_nodes = [nodex for nodex in dag_x.nodes() if len(list(dag_x.successors(nodex))) == 0]
                    dag_x.add_nodes_from([(self_node_list[0], {'level_num': level_id})])

                    for p_node_x in p_nodes:
                        dag_x.add_edge(p_node_x, self_node_list[0])
            else:
                temp_dag_list = []
                for dag_x in dag_list:
                    temp_dag_list += shape_dag_generator(dag_x, self_node_list, level_id)
                dag_list = temp_dag_list
        ret_dag_list += dag_list
    return ret_dag_list

def shape_enumator(node_num, last_shape_num_list):
    reset_node_num = node_num - sum(last_shape_num_list)
    assert reset_node_num > 0
    if reset_node_num == 1:
        temp_new_last_shape_num_list = copy.deepcopy(last_shape_num_list)
        temp_new_last_shape_num_list.append(1)
        return [temp_new_last_shape_num_list]
    else:
        ret_list = []
        for slevel_node_num in range(1, reset_node_num):
            temp_new_last_shape_num_list = copy.deepcopy(last_shape_num_list)
            temp_new_last_shape_num_list.append(slevel_node_num)
            ret_list += shape_enumator(node_num, temp_new_last_shape_num_list)
        return ret_list

def shape_list_trance(shape_num_list):
    node_num = sum(shape_num_list)
    node_id_list = list(range(node_num))
    ret_shape_list = []
    for shape_num_x in shape_num_list:
        ret_shape_list.append(node_id_list[:shape_num_x])
        del node_id_list[:shape_num_x]
    return  ret_shape_list

def shape_dag_generator(dag_x, self_node_list, level_num):
    ret_dag_list = []

    for level_id in range(level_num):
        if level_id == level_num - 1:
            up_same_level_node_iso_label_comput(dag_x, level_id)        # 按层计算 up_iso_label(只算最后一层，其他的之前算过了)
        down_same_level_node_iso_label_comput(dag_x, level_id)          # 按层计算 down_iso_label(所有层都更新一遍)
    # (2) 加新边 pnode_list_enumerate
    # (2.1) 前驱sink点集合  sink_node_list; 2.前驱内点集合  inter_node_list
    total_label_dict = {}
    for node_x in dag_x.nodes(data=True):
        node_x_label = (node_x[1]['level_num'], node_x[1]['up_iso_label'],node_x[1]['down_iso_label'])
        if node_x_label in total_label_dict:
            total_label_dict[node_x_label].append(node_x[0])
        else:
            total_label_dict[node_x_label] = [node_x[0]]

    last_level_node_list = [node_x[0] for node_x in dag_x.nodes(data=True) if node_x[1]['level_num'] == level_num - 1]
    # inte_level_node_list = [(node_x[0]['level_num'], node_x[0]['up_iso_label'],node_x[0]['down_iso_label'])
    #                             for node_x in dag_x.nodes(data=True) if node_x[1]['level_num'] < level_num - 1]

    # (2.3) 穷举所有可行连接前驱 pnode_list_enumerate [(p1,p2,p3...),()], 至少1个sink——node,
    last_level_node_id_enumerate_list = []
    for sn_num in range(len(last_level_node_list)):
        temp_id_enumerate_list_1 = list(itertools.combinations(last_level_node_list, sn_num + 1))
        temp_label_enumerate_list = list(set([tuple([(dag_x.nodes[temp_id_x]['level_num'], dag_x.nodes[temp_id_x]['up_iso_label'],dag_x.nodes[temp_id_x]['down_iso_label']) for temp_id_x in temp_id_list])
                                            for temp_id_list in temp_id_enumerate_list_1]))
        temp_id_enumerate_list_2 = []
        for temp_label_list in temp_label_enumerate_list:
            temp_total_label_dict = copy.deepcopy(total_label_dict)
            temp_id_enumerate_list_2.append([temp_total_label_dict[temp_label_x].pop(0) for temp_label_x in temp_label_list])
        last_level_node_id_enumerate_list += temp_id_enumerate_list_2

    # last_level_node_enumerate_list = []
    # for last_level_node_enumerate_list in last_level_node_enumerate_list:
    # inter_level_node_enumerate_list = []
    # for sn_num in range(len(inte_level_node_list) + 1):
    #     inter_level_node_enumerate_list += list(set(itertools.combinations(inte_level_node_list, sn_num)))

    # (2.4) sink的对抗链
    pnode_list_enumerate = []
    for last_level_node_enumerate_x in last_level_node_id_enumerate_list:
        # 1) 样例DAG 删除sink node的所有祖先；
        sample_dag = copy.deepcopy(dag_x)
        rem_set = set(last_level_node_list)
        for last_level_node_x in last_level_node_enumerate_x:
            rem_set.update(nx.ancestors(sample_dag, last_level_node_x))
        sample_dag.remove_nodes_from(rem_set)
        # (2) 获取剩下DAG的对抗链子；
        pred_node_opt_list = list(nx.antichains(sample_dag, topo_order=None))
        for pred_node_opt_x in pred_node_opt_list:
            pred_node_opt_x += last_level_node_enumerate_x
        pnode_list_enumerate += pred_node_opt_list
    # (1) 加新结点
    temp_dag_x = copy.deepcopy(dag_x)
    # 添加向上同构label，添加level_num
    # temp_dag_x.add_nodes_from(self_node_list)
    temp_dag_x.add_nodes_from([(self_node_x, {'level_num':level_num}) for self_node_x in self_node_list])
    # (2.4) 根据本层结点搭配组合 edge_pnode_ret_list      [ [1:[p11,p12,p13],2:[p21,p22,p23],3:[p31,p32,p33]], [1:[p11,p12,p13],2:[p21,p22,p23],3:[p31,p32,p33]] ]
    if len(pnode_list_enumerate) == 0:
        ret_dag_list.append(temp_dag_x)
    else:
        edge_p_list = list(itertools.combinations_with_replacement(pnode_list_enumerate, len(self_node_list))) # 从可行解法中抽取 len(sn)个
        for edge_p_list_x in edge_p_list:
            temp_dag_list_x = copy.deepcopy(temp_dag_x)
            for self_node_id, edges_p_x in enumerate(edge_p_list_x):
                for edge_p_x in edges_p_x:
                    temp_dag_list_x.add_edge(edge_p_x, self_node_list[self_node_id])
            ret_dag_list.append(temp_dag_list_x)
    return ret_dag_list

def up_same_level_node_iso_label_comput(dag_x, level_id):
    self_level_node_list = [node_x[0] for node_x in dag_x.nodes(data=True) if node_x[1]['level_num'] == level_id]
    up_iso_node_list = [[self_level_node_list.pop()]]
    for node_x in self_level_node_list:
        t_step = True
        sn_subg = dag_x.subgraph(list(nx.ancestors(dag_x, node_x)) + [node_x])
        for node_id_list in up_iso_node_list:
            tsn_subg = dag_x.subgraph(list(nx.ancestors(dag_x, node_id_list[0])) + [node_id_list[0]] )
            if nx.isomorphism.GraphMatcher(sn_subg, tsn_subg).is_isomorphic():
                node_id_list.append(node_x)            # 如果同构，直接加入label对应的list中
                t_step = False
                break
        if t_step:
            up_iso_node_list.append([node_x])
    # print(sink_node_up_iso_list)
    for up_iso_label, node_list in enumerate(up_iso_node_list):
        for node_x in node_list:
            dag_x.nodes[node_x]['up_iso_label'] = up_iso_label



def down_same_level_node_iso_label_comput(dag_x, level_id):
    self_level_node_list = [node_x[0] for node_x in dag_x.nodes(data=True) if node_x[1]['level_num'] == level_id]
    down_iso_node_list = [[self_level_node_list.pop(0)]]
    for node_x in self_level_node_list:
        t_step = True
        sn_subg = dag_x.subgraph(list(dag_x.successors(node_x)) + [node_x])

        for node_id_list in down_iso_node_list:
            tsn_subg = dag_x.subgraph(list(dag_x.successors(node_id_list[0])) + [node_id_list[0]] )
            if nx.isomorphism.GraphMatcher(sn_subg, tsn_subg).is_isomorphic():
                node_id_list.append(node_x)            # 如果同构，直接加入label对应的list中
                t_step = False
                break
        if t_step:
            down_iso_node_list.append([node_x])
    for down_iso_label, node_list in enumerate(down_iso_node_list):
        for node_x in node_list:
            dag_x.nodes[node_x]['down_iso_label'] = down_iso_label


if __name__ == "__main__":
    for n in range(30):
        stime = time.time()
        ret_list1 = combination_exhaustion(n)
        ret_list2 = permutation_exhaustion_total(ret_list1)
        etime = time.time()
        print(f'node_num:{n}_expansion pime:{etime - stime:.2f}_ length1:{len(ret_list1)}_ length2:{len(ret_list2)}')
        # print(ret_list1)
        # print(ret_list2)
        # ret_list1 = list(itertools.permutations(list(range(n)), n))
        # ret_list2 = list(set(itertools.permutations(list(range(n)), n)))
