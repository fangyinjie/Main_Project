#!/usr/bin/python3
# -*- coding: utf-8 -*-

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


# # # # # # # # # # # # # # # #
# (1) combination
# A004250
# 1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135, 176, 231, 297, 385, 490, 627, 792, 1002, 1255, 1575, 1958,
# 2436, 3010, 3718, 4565, 5604, 6842, 8349, 10143, 12310, 14883, 17977, 21637, 26015, 31185, 37338, 44583, 53174, 63261,
# 75175, 89134, 105558, 124754, 147273, 173525
# # # # # # # # # # # # # # # #
# 操作1，收尾；
# 操作2，分解；
# level_max\level_min\shape_min\shape_max = 可以取等
# def combination_exhaustion(node_num, level_min=1, level_max=float('Inf'),shape_min=1, shape_max=float('Inf')):
#     assert  level_min >= 1
#     assert  level_max >= level_min
#     ret_list = []
#     if level_min == 1:  # 一定有收尾，
#         if shape_min <= node_num <= shape_max:
#             ret_list.append((node_num,))    # 收尾
#         if level_max  > level_min:          # 还有分解
#             for local_node_num in range(shape_min, min(int(node_num / 2), shape_max) + 1):
#                 next_node_num = node_num - local_node_num
#                 sat_list = combination_exhaustion(next_node_num, max(level_min-1,1), level_max - 1, local_node_num, shape_max)
#                 for sat_x in sat_list:
#                     ret_list.append((local_node_num,) + sat_x)
#     else:
#         for local_node_num in range(shape_min, min(int(node_num/2), shape_max) + 1):
#             next_node_num = node_num - local_node_num
#             sat_list = combination_exhaustion(next_node_num, max(level_min-1,1), level_max-1, local_node_num, shape_max)
#             for sat_x in sat_list:
#                 ret_list.append((local_node_num,) + sat_x)
#
#     return ret_list
def combination_exhaustion(node_num, level_min=1, level_max=float('Inf'),shape_min=1, shape_max=float('Inf')):
    assert  level_min >= 1
    assert  level_max >= level_min
    ret_list = []
    if level_min == 1:  # 一定有收尾，
        if shape_min <= node_num <= shape_max:
            ret_list.append((node_num,))    # 收尾
    if (level_min > 1) or (level_max > level_min):  # 一定有收尾，
        for local_node_num in range(shape_min, min(int(node_num / 2), shape_max) + 1):
            next_node_num = node_num - local_node_num
            sat_list = combination_exhaustion(next_node_num, max(level_min-1,1), level_max - 1, local_node_num, shape_max)
            for sat_x in sat_list:
                ret_list.append((local_node_num,) + sat_x)
    return ret_list


# # # # # # # # # # # # # # # #
# (2) permutation
# 输入 combination不同的组合；
# 根据组合合成不同的排序；
# 不同的组合一定无法得到同样的排列；
# # # # # # # # # # # # # # # #
def permutation_exhaustion(combination_list):
    ret_list = []
    for combination_x in combination_list:
        ret_list += list(set(itertools.permutations(combination_x, len(combination_x))))
    return ret_list


if __name__ == "__main__":
    for n in range(100):
        stime = time.time()
        ret_list = list(set(itertools.permutations(list(range(n)), n)))
        etime = time.time()
        print(f'node_num:{n}_ tcexpansion pime:{etime - stime}_ length:{len(ret_list)}')
    # for node_num in range(3, 5):  # node_num = n + 2
    #     print('#########################################################################')
    #     stime = time.time()
    #     # ret_list_1 = combination_exhaustion(node_num, level_min=1, level_max=3,shape_min=1, shape_max=3)
    #     ret_list_1 = combination_exhaustion(node_num)
    #     ret_list_2 = permutation_exhaustion(ret_list_1)
    #
    #     etime = time.time()
    #     print(f'node_num:{node_num}_ time:{etime - stime}_'
    #           f'list1-length = {len(ret_list_1)}; '
    #           f'list2-length = {len(ret_list_2)};')
    #     print(ret_list_1)
    #     print(ret_list_2)

