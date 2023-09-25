import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm
import random



addr_list = ['D:/github/DAG_Scheduling_Summary/Data_Process/Data/7-3/preempt_test_71.csv']

for addr_x in addr_list:
    df = pd.read_csv(addr_x, index_col=None, na_values=["NA"])
    FLOW_NUM = df['FLOW_NUM']
    jitter = df['jitter']
    HI_DAG_ID = df['HI_DAG_ID']
    LO_DAG_ID = df['LO_DAG_ID']
    CORE_NUM = df['CORE_NUM']
    SELF_NP_MAKESPAN = df['SELF_NP_MAKESPAN']
    SELF_NP_C1_MAKESPAN = df['SELF_NP_C1_MAKESPAN']
    SELF_NP_C2_MAKESPAN = df['SELF_NP_C2_MAKESPAN']
    SELF_NP_Workload = df['SELF_NP_Workload']
    SELF_P_MAKESPAN = df['SELF_P_MAKESPAN']
    SELF_P_C1_MAKESPAN = df['SELF_P_C1_MAKESPAN']
    SELF_P_C2_MAKESPAN = df['SELF_P_C2_MAKESPAN']
    SELF_P_Workload = df['SELF_P_Workload']
    SELF_lP1_MAKESPAN = df['SELF_lP1_MAKESPAN']
    SELF_lP1_C1_MAKESPAN = df['SELF_lP1_C1_MAKESPAN']
    SELF_lP1_C1_lose_rate = df['SELF_lP1_C1_lose_rate']
    SELF_lP1_C2_MAKESPAN = df['SELF_lP1_C2_MAKESPAN']
    SELF_lP1_Workload = df['SELF_lP1_Workload']
    SELF_lP2_MAKESPAN = df['SELF_lP2_MAKESPAN']
    SELF_lP2_C1_MAKESPAN = df['SELF_lP2_C1_MAKESPAN']
    SELF_lP2_C1_lose_rate = df['SELF_lP2_C1_lose_rate']
    SELF_lP2_C2_MAKESPAN = df['SELF_lP2_C2_MAKESPAN']
    SELF_lP2_Workload = df['SELF_lP2_Workload']
    SELF_lP3_MAKESPAN = df['SELF_lP3_MAKESPAN']
    SELF_lP3_C1_MAKESPAN = df['SELF_lP3_C1_MAKESPAN']
    SELF_lP3_C1_lose_rate = df['SELF_lP3_C1_lose_rate']
    SELF_lP3_C2_MAKESPAN = df['SELF_lP3_C2_MAKESPAN']
    SELF_lP3_Workload = df['SELF_lP3_Workload']
    SELF_lP4_MAKESPAN = df['SELF_lP4_MAKESPAN']
    SELF_lP4_C1_MAKESPAN = df['SELF_lP4_C1_MAKESPAN']
    SELF_lP4_C1_lose_rate = df['SELF_lP4_C1_lose_rate']
    SELF_lP4_C2_MAKESPAN = df['SELF_lP4_C2_MAKESPAN']
    SELF_lP4_Workload = df['SELF_lP4_Workload']

    # 高关键 makespan
    # SELF_lP2_C2_MAKESPAN
    # SELF_lP2_C3_MAKESPAN
    # SELF_lP2_C4_MAKESPAN

    # 低关键 workload
    # """
    # sns.kdeplot(SELF_lP2_C1_lose_rate, color='green')
    # sns.kdeplot(SELF_lP3_C1_lose_rate, color='red')
    # sns.kdeplot(SELF_lP4_C1_lose_rate, color='black')

    sns.kdeplot((SELF_lP2_Workload - SELF_P_Workload) / SELF_lP2_Workload, color='green')
    sns.kdeplot((SELF_lP3_Workload - SELF_P_Workload) / SELF_lP3_Workload, color='red')
    sns.kdeplot((SELF_lP4_Workload - SELF_P_Workload) / SELF_lP4_Workload, color='black')

    # colore_list = [plt.scatter(0, 0, marker="s", color='green'),  plt.scatter(0, 0, marker="s", color='red')]
    # colore_id = ['FP', 'LP']
    # plt.legend(colore_list, colore_id, loc='upper right', title='', prop={'family': 'Times New Roman', 'size': 16})
    plt.title(f'dag_type_hi_C1')
    plt.grid(True)
    plt.show()
    # """

    # 低关键 workload
    FP_IMP_workload = 100 * (SELF_NP_Workload - SELF_P_Workload) / SELF_NP_Workload
    LP_IMP_workload = 100 * (SELF_NP_Workload - SELF_lP_Workload) / SELF_NP_Workload
    FLP_IMP_workload = 100 * (SELF_lP_Workload - SELF_P_Workload) / SELF_lP_Workload
    FLP_IMP_workload = FLP_IMP_workload.loc[(FLP_IMP_workload > -2)]
    # sns.kdeplot(FP_IMP_C1, color='green')
    # sns.kdeplot(LP_IMP_C1, color='red')
    sns.kdeplot(FLP_IMP_workload, color='black')
    # colore_list = [plt.scatter(0, 0, marker="s", color='green'),  plt.scatter(0, 0, marker="s", color='red')]
    # colore_id = ['FP', 'LP']
    # plt.legend(colore_list, colore_id, loc='upper right', title='', prop={'family': 'Times New Roman', 'size': 16})
    plt.title(f'dag_type_workload')
    plt.grid(True)
    plt.show()
    # df_np_c2_impro = cpc2.loc[(cpc2 > -1)]

    sns.kdeplot(FP_IMP_C1, color='green')
    sns.kdeplot(LP_IMP_C1, color='red')
    colore_list = [plt.scatter(0, 0, marker="s", color='green'),  plt.scatter(0, 0, marker="s", color='red')]
    colore_id = ['FP', 'LP']
    plt.legend(colore_list, colore_id, loc='upper right', title='', prop={'family': 'Times New Roman', 'size': 16})
    plt.title(f'dag_type_hi_C1')
    plt.grid(True)
    plt.show()

    # SELF_NP_MDATA_C1 = df['SELF_NP_MDATA_C1']
    # SELF_NP_MDATA_C2 = df['SELF_NP_MDATA_C2']
    # SELF_P_MDATA_C1 = df['SELF_P_MDATA_C1']
    # SELF_P_MDATA_C2 = df['SELF_P_MDATA_C2']
    # SELF_P4_MDATA_C1 = df['SELF_P4_MDATA_C1']
    # SELF_P4_MDATA_C2 = df['SELF_P4_MDATA_C2']

    # FP_IMP_C1 = 100 * (SELF_NP_MDATA_C1 - SELF_P_MDATA_C1) / SELF_NP_MDATA_C1
    # FP_IMP_C2 = 100 * (SELF_NP_MDATA_C2 - SELF_P_MDATA_C2) / SELF_NP_MDATA_C2
    # LP_IMP_C1 = 100 * (SELF_NP_MDATA_C1 - SELF_P4_MDATA_C1) / SELF_NP_MDATA_C1
    # LP_IMP_C2 = 100 * (SELF_NP_MDATA_C2 - SELF_P4_MDATA_C2) / SELF_NP_MDATA_C2

    # sns.set(font='SimHei', font_scale=1.0)  # 解决Seaborn中文显示问题并调整字体大小
    # sns.distplot(cpc1, kde=True, rug=False, color='g', label='差分之和')
    # sns.kdeplot(cpc1[70:], color='green',)
    sns.kdeplot(FP_IMP_C1, color='green')
    sns.kdeplot(LP_IMP_C1, color='red')
    colore_list = [plt.scatter(0, 0, marker="s", color='green'),  plt.scatter(0, 0, marker="s", color='red')]
    colore_id = ['FP', 'LP']
    plt.legend(colore_list, colore_id, loc='upper right', title='', prop={'family': 'Times New Roman', 'size': 16})
    plt.title(f'dag_type_hi_C1')
    plt.grid(True)
    plt.show()

    # plt.savefig('./Industry_hi_{0}_new.png'.format(dag_type_x))

    sns.kdeplot(FP_IMP_C2, color='green')
    sns.kdeplot(LP_IMP_C2, color='red')
    colore_list = [plt.scatter(0, 0, marker="s", color='green'),  plt.scatter(0, 0, marker="s", color='red')]
    colore_id = ['FP', 'LP']
    plt.legend(colore_list, colore_id, loc='upper right', title='', prop={'family': 'Times New Roman', 'size': 16})
    plt.title(f'dag_type_hi_C2')
    plt.grid(True)
    plt.show()

    # plt.title(f'C2_dag_type:{dag_type_x}')
    # plt.grid(True)
    # plt.show()
    # plt.savefig('./Industry{0}_C1.png'.format(dag_type_x))
    # plt.close()
    # sns.kdeplot(df_np_c2_impro, color='green' )
    # sns.kdeplot(df_p_c2_impro, color='red' )
    # plt.title(f'C2_dag_type:{dag_type_x}')
    # plt.grid(True)

    # # plt.show()
    # plt.savefig('./Industry{0}_C2.png'.format(dag_type_x))
    # plt.close()
