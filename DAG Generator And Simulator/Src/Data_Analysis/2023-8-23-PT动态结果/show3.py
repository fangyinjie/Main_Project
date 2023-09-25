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
from matplotlib.font_manager import FontProperties


if __name__ == "__main__":
    sns.set_theme()
    font_set = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=12)
    # data_addr = './9-8_data_00.csv'
    data_addr = './1/9-8_data_11.csv'
    df = pd.read_csv(data_addr, index_col=None, na_values=["NA"])
    """
    STP_C1_loss1  =  100 * (df1['PT_C1'] - df1['P_C1']) / df1['P_C1']
    STP_C1_loss1  = STP_C1_loss1.loc[(STP_C1_loss1 < 5)]
    STP_C1_loss1.index = [x for x in range(STP_C1_loss1.shape[0]) ]
    STP_C1_loss1  = pd.concat([STP_C1_loss1, pd.DataFrame(['10%' for _ in range(STP_C1_loss1.shape[0])])], axis=1)
    STP_C1_loss2  =  100 * (df2['PT_C1'] - df2['P_C1']) / df2['P_C1']
    STP_C1_loss2  = STP_C1_loss2.loc[(STP_C1_loss2 < 5)]
    STP_C1_loss2.index = [x for x in range(STP_C1_loss2.shape[0]) ]
    STP_C1_loss2  = pd.concat([STP_C1_loss2, pd.DataFrame(['30%' for _ in range(STP_C1_loss2.shape[0])])], axis=1)
    STP_C1_loss3  =  100 * (df3['PT_C1'] - df3['P_C1']) / df3['P_C1']
    STP_C1_loss3  = STP_C1_loss3.loc[(STP_C1_loss3 < 5)]
    STP_C1_loss3.index = [x for x in range(STP_C1_loss3.shape[0]) ]
    STP_C1_loss3  = pd.concat([STP_C1_loss3, pd.DataFrame(['50%' for _ in range(STP_C1_loss3.shape[0])])], axis=1)

    STP_C1_loss = pd.concat([STP_C1_loss1, STP_C1_loss2, STP_C1_loss3])
    STP_C1_loss.index = [x for x in range(STP_C1_loss.shape[0]) ]
    # STP_C1_loss = pd.concat([STP_C1_loss, pd.DataFrame(['PT' for _ in range(STP_C1_loss.shape[0])])], axis=1)
    STP_C1_loss.columns = ['data', 'label']
    sns.histplot(data=STP_C1_loss, x="data", hue='label', bins=50)

    plt.xlabel(u'高关键任务时延损失率（%）',fontproperties=font_set)
    plt.ylabel(u'损失率区间内的样本数量',fontproperties=font_set)
    """
    """
    STP_C2_Impro1 =  100 * (df1['P_MAKESPAN'] - df1['PT_MAKESPAN'])  / df1['P_MAKESPAN']
    STP_C2_Impro1  = STP_C2_Impro1.loc[(STP_C2_Impro1 >-3)]
    STP_C2_Impro1.index = [x for x in range(STP_C2_Impro1.shape[0]) ]
    STP_C2_Impro1  = pd.concat([STP_C2_Impro1, pd.DataFrame(['10%' for _ in range(STP_C2_Impro1.shape[0])])], axis=1)
    STP_C2_Impro2 =  100 * (df2['P_MAKESPAN'] - df2['PT_MAKESPAN'])  / df2['P_MAKESPAN']
    STP_C2_Impro2  = STP_C2_Impro2.loc[(STP_C2_Impro2 >-5)]
    STP_C2_Impro2.index = [x for x in range(STP_C2_Impro2.shape[0]) ]
    STP_C2_Impro2  = pd.concat([STP_C2_Impro2, pd.DataFrame(['30%' for _ in range(STP_C2_Impro2.shape[0])])], axis=1)
    STP_C2_Impro3 =  100 * (df3['P_MAKESPAN'] - df3['PT_MAKESPAN'])  / df3['P_MAKESPAN']
    STP_C2_Impro3  = STP_C2_Impro3.loc[(STP_C2_Impro3 >-7)]
    STP_C2_Impro3.index = [x for x in range(STP_C2_Impro3.shape[0]) ]
    STP_C2_Impro3  = pd.concat([STP_C2_Impro3, pd.DataFrame(['50%' for _ in range(STP_C2_Impro3.shape[0])])], axis=1)

    STP_C2_Impro = pd.concat([STP_C2_Impro1, STP_C2_Impro2, STP_C2_Impro3])
    STP_C2_Impro.index = [x for x in range(STP_C2_Impro.shape[0])]
    STP_C2_Impro.columns = ['data', 'label']
    sns.histplot(data=STP_C2_Impro, x="data", hue='label', bins=50)

    plt.xlabel(u'低关键任务时延改善率（%）',fontproperties=font_set)
    plt.ylabel(u'性能提升率区间内的样本数量',fontproperties=font_set)
    """
    """
    FP_C1_1 = df1['P_MAKESPAN']
    FP_C1_1  = pd.concat([FP_C1_1, pd.DataFrame([('10%', 'FP') for _ in range(FP_C1_1.shape[0])])], axis=1)
    FP_C1_1.columns = ['data', 'label', 'type']
    PT_C1_1 = df1['PT_MAKESPAN']
    PT_C1_1  = pd.concat([PT_C1_1, pd.DataFrame([('10%', 'PT') for _ in range(PT_C1_1.shape[0])])], axis=1)
    PT_C1_1.columns = ['data', 'label', 'type']
    # NP_C1_1 = df1['NP_MAKESPAN']
    # NP_C1_1  = pd.concat([NP_C1_1, pd.DataFrame([('10%', 'NP') for _ in range(NP_C1_1.shape[0])])], axis=1)
    # NP_C1_1.columns = ['data', 'label', 'type']

    FP_C1_2 = df2['P_MAKESPAN']
    FP_C1_2  = pd.concat([FP_C1_2, pd.DataFrame([('30%', 'FP') for _ in range(FP_C1_2.shape[0])])], axis=1)
    FP_C1_2.columns = ['data', 'label', 'type']
    PT_C1_2 = df2['PT_MAKESPAN']
    PT_C1_2  = pd.concat([PT_C1_2, pd.DataFrame([('30%', 'PT') for _ in range(PT_C1_2.shape[0])])], axis=1)
    PT_C1_2.columns = ['data', 'label', 'type']

    FP_C1_3 = df3['P_MAKESPAN']
    FP_C1_3  = pd.concat([FP_C1_3, pd.DataFrame([('50%', 'FP') for _ in range(FP_C1_3.shape[0])])], axis=1)
    FP_C1_3.columns = ['data', 'label', 'type']
    PT_C1_3 = df3['PT_MAKESPAN']
    PT_C1_3  = pd.concat([PT_C1_3, pd.DataFrame([('50%', 'PT') for _ in range(PT_C1_3.shape[0])])], axis=1)
    PT_C1_3.columns = ['data', 'label', 'type']


    sss = pd.concat([FP_C1_1, PT_C1_1,
                     FP_C1_2, PT_C1_2, 
                     FP_C1_3, PT_C1_3])

    sss.index = [x for x in range(sss.shape[0])]
    sns.boxplot(x="label", y="data", hue="type", data=sss, width=0.6)
    plt.xlabel(u'时间抖动比例(%))',fontproperties=font_set)
    plt.ylabel(u'低关键任务完成时间分布(cycle)',fontproperties=font_set)
    """
    df.insert(df.shape[1], 'c1_loss', 25 * (df['PT_C1'] - df['P_C1']) / df['P_C1'])
    df.insert(df.shape[1], 'c2_impro', 20 * (df['P_C2'] - df['PT_C2']) / df['P_C2'])


    # FP_C1_1 = df[['P_C1', 'jitter']]
    # FP_C1_1.columns = ['data', 'label', 'type']
    # PT_C1_1 = df1['PT_C1']
    # PT_C1_1  = pd.concat([PT_C1_1, pd.DataFrame([('10%', 'PT') for _ in range(PT_C1_1.shape[0])])], axis=1)
    # PT_C1_1.columns = ['data', 'label', 'type']
    #
    # FP_C1_2 = df2['P_C1']
    # FP_C1_2  = pd.concat([FP_C1_2, pd.DataFrame([('30%', 'FP') for _ in range(FP_C1_2.shape[0])])], axis=1)
    # FP_C1_2.columns = ['data', 'label', 'type']
    # PT_C1_2 = df2['PT_C1']
    # PT_C1_2  = pd.concat([PT_C1_2, pd.DataFrame([('30%', 'PT') for _ in range(PT_C1_2.shape[0])])], axis=1)
    # PT_C1_2.columns = ['data', 'label', 'type']
    #
    # FP_C1_3 = df3['P_C1']
    # FP_C1_3  = pd.concat([FP_C1_3, pd.DataFrame([('50%', 'FP') for _ in range(FP_C1_3.shape[0])])], axis=1)
    # FP_C1_3.columns = ['data', 'label', 'type']
    # PT_C1_3 = df3['PT_C1']
    # PT_C1_3  = pd.concat([PT_C1_3, pd.DataFrame([('50%', 'PT') for _ in range(PT_C1_3.shape[0])])], axis=1)
    # PT_C1_3.columns = ['data', 'label', 'type']

    #
    # sss = pd.concat([FP_C1_1, PT_C1_1,
    #                  FP_C1_2, PT_C1_2,
    #                  FP_C1_3, PT_C1_3])
    # df  = df.loc[(df['c2_impro'] > -10)]
    # df.index = [x for x in range(df.shape[0]) ]
    # sns.histplot(data=df, x="c2_impro", hue='jitter', bins=50, palette=sns.color_palette())

    df  = df.loc[(df['c1_loss'] < 5)]
    df.index = [x for x in range(df.shape[0]) ]
    sns.histplot(data=df, x="c1_loss", hue='jitter', bins=50, palette=sns.color_palette())
    plt.xlabel(u'高关键任务时延损率(%))',fontproperties=font_set)
    plt.ylabel(u'高关键任务完成时间分布(cycle)',fontproperties=font_set)
    plt.show()


    df  = df.loc[(df['c2_impro'] > -10)]
    df.index = [x for x in range(df.shape[0]) ]
    sns.histplot(data=df, x="c2_impro", hue='jitter', bins=50, palette=sns.color_palette())


    plt.xlabel(u'低关键任务时延提升率(%))',fontproperties=font_set)
    plt.ylabel(u'低关键任务完成时间分布(cycle)',fontproperties=font_set)
    plt.show()

    pass
