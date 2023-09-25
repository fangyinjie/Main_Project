import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm
import random


# dag_type_list = ['hil_lol', 'hil_low', 'hiw_lol', 'hiw_low']
dag_type_list = ['hiw_lol']
for dag_type_x in dag_type_list:
    df = pd.read_csv(f'D:/github/DAG_Scheduling_Summary/Data_Process/Data/6-10/preempt_test_{dag_type_x}.csv',
                     index_col=None, na_values=["NA"])

    FIFO_MAKESPAN = df['FIFO_MAKESPAN']
    FIFO_MAKESPAN_cri_1 = df['FIFO_MAKESPAN_cri_1']
    FIFO_MAKESPAN_cri_2 = df['FIFO_MAKESPAN_cri_2']

    SELF_NP_MAKESPAN = df['SELF_NP_MAKESPAN']
    SELF_NP_MAKESPAN_cri_1 = df['SELF_NP_MAKESPAN_cri_1']
    SELF_NP_MAKESPAN_cri_2 = df['SELF_NP_MAKESPAN_cri_2']

    SELF_P_MAKESPAN = df['SELF_P_MAKESPAN']
    SELF_P_MAKESPAN_cri_1 = df['SELF_P_MAKESPAN_cri_1']
    SELF_P_MAKESPAN_cri_2 = df['SELF_P_MAKESPAN_cri_2']

    cpc1 = 100 * (SELF_NP_MAKESPAN_cri_1 - SELF_P_MAKESPAN_cri_1) / SELF_NP_MAKESPAN_cri_1
    cpc2 = 100 * (SELF_NP_MAKESPAN_cri_2 - SELF_P_MAKESPAN_cri_2) / SELF_NP_MAKESPAN_cri_2

    for ccpp_id, ccpp_data in enumerate(cpc1):
        cpc1[ccpp_id] = random.random() * 0.00 + cpc1[ccpp_id] * 1
        # cpc1[ccpp_id] = cpc1[ccpp_id] * 10

    # df_np_c1_impro = cpc1.loc[(cpc1 > -1)]
    # df_np_c2_impro = cpc2.loc[(cpc2 > -1)]

    # sns.set(font='SimHei', font_scale=1.0)  # 解决Seaborn中文显示问题并调整字体大小
    # sns.distplot(cpc1, kde=True, rug=False, color='g', label='差分之和')
    # sns.kdeplot(cpc1[70:], color='green',)
    sns.kdeplot(cpc1, color='green')
    plt.title(f'dag_type_hi:{dag_type_x}')
    # colore_id = ['High_Critical_DAG', 'Low_Critical_DAG']
    # colore_list = [plt.scatter(0, 0, marker="s", color=cid) for cid in ['green', 'red']]
    # plt.legend(colore_list, colore_id, loc='upper right', title='', prop={'family': 'Times New Roman', 'size': 16})
    plt.grid(True)
    plt.show()
    # plt.savefig('./Industry_hi_{0}_new.png'.format(dag_type_x))

    sns.distplot(cpc1, kde=True, rug=False, color='g',)
    # plt.set_title('diff_sum_kde')
    plt.legend()
    plt.show()

    plt.close()
    sns.kdeplot(cpc2, color='red' )
    plt.title(f'dag_type_lo:{dag_type_x}')
    plt.grid(True)
    plt.show()
    # plt.savefig('./Industry_lo_{0}.png'.format(dag_type_x))
    plt.close()

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
