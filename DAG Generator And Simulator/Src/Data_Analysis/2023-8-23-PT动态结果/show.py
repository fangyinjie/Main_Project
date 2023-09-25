#!/usr/bin/python3
# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # 
# Randomized DAG Generator
# Create Time: 2023/8/2319:08
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
# # # # # # # # # # # # # # # #

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


if __name__ == "__main__":
    sns.set_theme()
    # data_addr = './8-25_data_jitter_10.0.csv'
    # data_addr = './9-21_data_jitter_50.0.csv'
    # data_addr = './9-22/9-21_data_jitter_50.0_00.csv'
    # data_addr = './9-22/9-21_data_jitter_50.0_01.csv'
    data_addr = './9-21_data_jitter_50.0_00.csv'
    # data_addr = './9-21_data_jitter_50.0_01.csv'
    # data_addr = './9-21_data_jitter_50.0_10.csv'
    # data_addr = './9-21_data_jitter_50.0_11.csv'
    df = pd.read_csv(data_addr, index_col=None, na_values=["NA"])
    STP1_C1_loss  =  100 * (df['PT1_C1'] - df['P_C1']) / df['P_C1']
    # STP_C1_loss = STP_C1_loss.loc[(STP_C1_loss < 5)]
    # STP_C1_loss.index = [x for x in range(STP_C1_loss.shape[0]) ]
    STP1_C1_loss = pd.concat([STP1_C1_loss, pd.DataFrame(['PT1' for _ in range(STP1_C1_loss.shape[0])])], axis=1)
    STP1_C1_loss.columns = ['data', 'label']

    NP_C1_loss  =  100 * (df['PT2_C1'] - df['P_C1']) / df['P_C1']
    NP_C1_loss = pd.concat([NP_C1_loss, pd.DataFrame(['NP' for _ in range(NP_C1_loss.shape[0])])], axis=1)
    NP_C1_loss.columns = ['data', 'label']

    STP2_C1_loss  =  100 * (df['PT2_C1'] - df['P_C1']) / df['P_C1']
    STP2_C1_loss = pd.concat([STP2_C1_loss, pd.DataFrame(['PT2' for _ in range(STP2_C1_loss.shape[0])])], axis=1)
    STP2_C1_loss.columns = ['data', 'label']

    STP3_C1_loss  =  100 * (df['PT3_C1'] - df['P_C1']) / df['P_C1']
    STP3_C1_loss = pd.concat([STP3_C1_loss, pd.DataFrame(['PT3' for _ in range(STP3_C1_loss.shape[0])])], axis=1)
    STP3_C1_loss.columns = ['data', 'label']

    STP6_C1_loss  =  100 * (df['PT6_C1'] - df['P_C1']) / df['P_C1']
    STP6_C1_loss = pd.concat([STP6_C1_loss, pd.DataFrame(['PT6' for _ in range(STP6_C1_loss.shape[0])])], axis=1)
    STP6_C1_loss.columns = ['data', 'label']

    result = pd.concat([STP1_C1_loss, NP_C1_loss ])
    # result = pd.concat([STP1_C1_loss,  STP2_C1_loss, STP3_C1_loss])
    # result = pd.concat([STP1_C1_loss, NP_C1_loss, STP3_C1_loss, STP2_C1_loss,STP6_C1_loss])
    print(result)
    # print(STP_C1_loss)
    # print(NP_C1_loss)
    # result['data']  =  result['data'] / 6
    # result = result.loc[(result['data'] < 5)]
    # result.index = [x for x in range(result.shape[0]) ]

    sns.histplot(data=result, x="data", hue='label',kde=True, bins=50)
    # sns.histplot(NP_C1_loss, binwidth=1, kde=False, color='#a6cee3')
    # sns.histplot(STP_C1_loss, binwidth=1, kde=False, color='#fdbf6f')
    plt.show()

    STP1_C2_Impro  =  100 * (df['P_MAKESPAN'] - df['PT1_MAKESPAN'])   / df['P_MAKESPAN']
    STP1_C2_Impro = pd.concat([STP1_C2_Impro, pd.DataFrame(['PT1' for x in range(STP1_C2_Impro.shape[0])])], axis=1)
    STP1_C2_Impro.columns = ['data', 'label']

    NP_C2_Impro =  100 * (df['P_MAKESPAN'] - df['NP_MAKESPAN'])   / df['P_MAKESPAN']
    NP_C2_Impro = pd.concat([NP_C2_Impro, pd.DataFrame(['NP' for x in range(NP_C2_Impro.shape[0])])], axis=1)
    NP_C2_Impro.columns = ['data', 'label']

    STP2_C2_Impro =  100 * (df['P_MAKESPAN'] - df['PT2_MAKESPAN'])   / df['P_MAKESPAN']
    STP2_C2_Impro = pd.concat([STP2_C2_Impro, pd.DataFrame(['PT2' for x in range(STP2_C2_Impro.shape[0])])], axis=1)
    STP2_C2_Impro.columns = ['data', 'label']

    STP3_C2_Impro =  100 * (df['P_MAKESPAN'] - df['PT3_MAKESPAN'])   / df['P_MAKESPAN']
    STP3_C2_Impro = pd.concat([STP3_C2_Impro, pd.DataFrame(['PT3' for x in range(STP3_C2_Impro.shape[0])])], axis=1)
    STP3_C2_Impro.columns = ['data', 'label']

    STP6_C2_Impro =  100 * (df['P_MAKESPAN'] - df['PT6_MAKESPAN'])   / df['P_MAKESPAN']
    STP6_C2_Impro = pd.concat([STP6_C2_Impro, pd.DataFrame(['PT6' for x in range(STP6_C2_Impro.shape[0])])], axis=1)
    STP6_C2_Impro.columns = ['data', 'label']

    # result = pd.concat([STP1_C2_Impro,STP2_C2_Impro, STP3_C2_Impro])
    result = pd.concat([STP1_C2_Impro,STP2_C2_Impro, STP3_C2_Impro,STP6_C2_Impro,NP_C2_Impro])


    # result['data']  =  -result['data']
    # result = result.loc[(3 + result['data'] > -20)]
    # sns.histplot(data=result, x = "data", hue='label', palette='rainbow', bins=50, element='step')
    sns.histplot(data=result, x="data", hue='label', kde=True, bins=50)
    # sns.histplot(NP_C2_Impro, binwidth=1, kde=False, color='yellow')
    # sns.histplot(STP_C2_Impro, binwidth=1, kde=False, color='black')
    plt.show()

    pass
