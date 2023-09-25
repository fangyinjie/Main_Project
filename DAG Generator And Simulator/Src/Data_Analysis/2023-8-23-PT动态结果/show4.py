# !/usr/bin/python3
# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # 
# Randomized DAG Generator
# Create Time: 2023/9/87:57
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
# # # # # # # # # # # # # # # #

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


if __name__ == "__main__":
    sns.set_theme()
    font_set = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=12)
    # data_addr = './9-8_data_00.csv'
    data_addr = 'D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\PT_data\\9-21_data_jitter_50.0.csv'
    # data_addr = 'D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\PT_data\\1\\9-8_data_11_cri2.csv'
    # data_addr = 'D:\\github\\Exam_Data\\Output_data\\DAG_Generator\\PT_data\\1\\9-8_data_00_cri2'
    df = pd.read_csv(data_addr, index_col=None, na_values=["NA"])
    for i, j in df.iterrows():
        # print(i, j)
        k = j.value_counts().idxmax()
        print(k)