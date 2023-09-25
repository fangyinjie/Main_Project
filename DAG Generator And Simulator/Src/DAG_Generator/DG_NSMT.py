#!/usr/bin/python3
# -*- coding: utf-8 -*-
import copy
import networkx as nx

# # # # # # # # # # # # # # # # 
# Randomized DAG Generator
# Create Time: 2023/8/615:08
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
# # # # # # # # # # # # # # # #
import numpy as np
import itertools


# # 创建一个二维数组
# a = np.array([[1, 2, 3], [4, 5,6], [7, 8, 9]])
# # 创建一个新的一维数组
# b = np.array([10, 11, 12])
# # 在二维数组中插入一行
# c1 = np.insert(a, a.shape[0], b, axis=0)
# c2 = np.insert(a, a.shape[1], b, axis=1)
# print(c1)
# print(c2)

# 设计基本函数
def DAG_Generator(Source_Matrix, Node_Num):

    last_node_num = Source_Matrix.shape[0]
    ret_data = []
    for lnum in range(1, last_node_num + 1):        # insert_col_x = copy.deepcopy(insert_col)
        edge_list = list(itertools.combinations(list(range(last_node_num)), lnum))
        for edge_trup in edge_list:
            Source_Matrix_Cp = copy.deepcopy(Source_Matrix)
            insert_col = np.zeros((1, last_node_num))
            for edge_x in edge_trup:
                insert_col[0][edge_x] = 1
            Source_Matrix_Cp = np.insert(Source_Matrix_Cp, Source_Matrix_Cp.shape[1], insert_col, axis=1)    # 列
            Source_Matrix_Cp = np.insert(Source_Matrix_Cp, Source_Matrix_Cp.shape[0], np.zeros((1, Source_Matrix_Cp.shape[1])), axis=0)    # 行

            if Node_Num == 2:
                # 唯一的尾结点sink node；
                # ret_data.append(Source_Matrix_Cp)
                f_n1 = [n_x  for n_x in range(Source_Matrix_Cp.shape[0]) if np.sum(Source_Matrix_Cp[n_x]) == 0]  # 选择
                f_n2 = [n_x  for n_x in range(Source_Matrix_Cp.shape[0]) if np.sum(Source_Matrix_Cp[n_x]) != 0]  # 必连
                for lnum in range(len(f_n1) + 1):
                    test_1 = list(itertools.combinations(f_n1, lnum))
                    for s_node_list in list(itertools.combinations(f_n1, lnum)):
                        Source_Matrix_Cp_temp = copy.deepcopy(Source_Matrix_Cp)
                        temp_fn = copy.deepcopy(f_n2) + [s_node_x for s_node_x in s_node_list]
                        insert_col = np.zeros((1, Source_Matrix_Cp.shape[0]))
                        for edge_x in temp_fn:
                            insert_col[0][edge_x] = 1
                        Source_Matrix_Cp_temp = np.insert(Source_Matrix_Cp_temp, Source_Matrix_Cp_temp.shape[1], insert_col, axis=1)  # 列
                        Source_Matrix_Cp_temp = np.insert(Source_Matrix_Cp_temp, Source_Matrix_Cp_temp.shape[0], np.zeros((1, Source_Matrix_Cp_temp.shape[1])), axis=0)  # 行
                        ret_data.append(Source_Matrix_Cp_temp)
                #         Source_Matrix_Cp = np.c_[Source_Matrix_Cp, insert_col.T]
                #         insert_row = np.zeros((1, Source_Matrix_Cp.shape[1]))
                #         Source_Matrix_Cp = np.r_[Source_Matrix_Cp, insert_row]
                #         # 加入尾结点；没有后继的一定链接，其他的分配

            else:
                ret_data += DAG_Generator(Source_Matrix_Cp, Node_Num - 1)
    return ret_data


if __name__ == "__main__":
    for node_num in range(2, 10):
        ret_matrix_list = DAG_Generator(np.zeros((1, 1)), node_num)
        print(f'node_num:{node_num}, dag_num :{len(ret_matrix_list)}')
        # graph = nx.from_numpy_matrix(Matrix)
    pass



# for shape_num in range(node_num):