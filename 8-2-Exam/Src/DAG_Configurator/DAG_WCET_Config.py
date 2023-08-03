#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Randomized DAG Generator
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################

import math
import numpy as np
import random


def WCET_Config(temp_dag, WCET_Config_type, Virtual_node, a, b):
    # 方式1（均匀分布）：在区间[a, b]中均匀分布方式生成 WCET
    if WCET_Config_type == "Uniform":
        for x in temp_dag.nodes(data=True):
            x[1]['WCET'] = math.ceil(np.random.uniform(a, b))
            x[1]['BCET'] = x[1]['WCET']
            x[1]['ACET'] = x[1]['WCET']
        if Virtual_node:
            temp_dag.nodes[0]['WCET'] = 0
            temp_dag.nodes[temp_dag.number_of_nodes() - 1]['WCET'] = 0

    # 方式2（正态分布）：以loc=a为均值，以scale=b为方差 # size:输出形式 / 维度
    elif WCET_Config_type == "normal":
        for x in temp_dag.nodes(data=True):
            while True:
                x[1]['WCET'] = math.ceil(np.random.normal(loc=a, scale=b, size=None))
                if x[1]['WCET'] > 0:
                    x[1]['BCET'] = x[1]['WCET']
                    x[1]['ACET'] = x[1]['WCET']
                    break

    # 方式3（高斯分布，gauss）以均值为mu=a，标准偏差为sigma=b的方式生成 WCET
    elif WCET_Config_type == "gauss":
        for x in temp_dag.nodes(data=True):
            while True:
                x[1]['WCET'] = math.ceil(random.gauss(a, b))
                if x[1]['WCET'] > 0:
                    x[1]['BCET'] = x[1]['WCET']
                    x[1]['ACET'] = x[1]['WCET']
                    break
    else:
        pass

