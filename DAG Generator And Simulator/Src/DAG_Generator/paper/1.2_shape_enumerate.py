#!/usr/bin/python3
# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # #
# Create Time: 2023/9/1317:42
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
# # # # # # # # # # # # # # # #
import os
import re
import math
import copy
import time
# import datetime
import itertools

import numpy as np
import pandas as pd
import networkx as nx
import graphviz as gz
import z3.z3
# from itertools import combinations
from z3.z3 import Int, Sum, If, Solver, Or, IntNumRef, Bool, And, Implies
from random import random, sample, uniform, randint
def shape_enumator(node_num, last_shape_num_list, shape_length=None):
    if shape_length==None:
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
    else:   # 定长 DAG 的 shape
        assert shape_length >= 3



"""
def shape_enumator(node_num, last_shape_num_list, sh_min=1, 
                                                  sh_max=float('inf') , 
                                                  deg_max_out=float('inf'), 
                                                  deg_max_in=float('inf'), 
                                                  sh_num=None):
    ret_shapa_list = []
    if last_shape_num_list is None:
        last_shape_num_list = [1]

    next_level_node_num = 1
    self_level_node_num = 1
    last_level_node_num = 1

    self_level_node_num_list = []
    for self_level_node_x in range( max(math.ceil(last_level_node_num / deg_max_in), sh_min),
                                    min(sh_max, last_level_node_num * deg_max_out) ):
        self_level_node_num_list.append(self_level_node_x)

    ret_shapa_list.append(source_num)
    if len(ret_shapa_list) == 0:
        return []
    else:
        return shape_enumator(node_num, ret_shapa_list, sh_num=None, sh_min=None, sh_max=None, deg_max_out=None, deg_max_in=None)
"""

if __name__ == "__main__":
    # Node_Num      确定      否则从小到大依次输出
    for node_num in range(4, 12):
        stime = time.time()
        ret_shape_list = shape_enumator(node_num, [1])
        etime = time.time()
        print(f'node_num :{node_num} _ shape_list_num:{len(ret_shape_list)} _ time:{etime - stime}')
        for ret_shape_x in ret_shape_list:
            print(ret_shape_x)
