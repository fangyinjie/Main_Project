import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm


df = pd.read_csv('D:/github/DAG_Scheduling_Summary/Data_Process/Data/6-9/end_data_6_9.csv', index_col=None, na_values=["NA"])

dag_type_list = ['hil_lol', 'hil_low', 'hiw_lol', 'hiw_low']
for dag_type_x in dag_type_list:
    df_np_c1_impro = df.loc[(df['addr_str_x'] == dag_type_x), 'SELF_NP_C1_Impro']
    df_np_c2_impro = df.loc[(df['addr_str_x'] == dag_type_x), 'SELF_NP_C2_Impro']
    df_p_c1_impro  = df.loc[(df['addr_str_x'] == dag_type_x), 'SELF_P_C1_Impro']
    df_p_c2_impro  = df.loc[(df['addr_str_x'] == dag_type_x), 'SELF_P_C2_Impro']
    # df_np_c1_impro = df.loc[(df['SELF_NP_C1_Impro'] >= 0), 'SELF_NP_C1_Impro']
    # df_np_c1_impro = df.loc[:, 'SELF_NP_C1_Impro']
    # df_np_c1_impro = df['SELF_NP_C1_Impro']
    # sns.kdeplot(df_np_c1_impro, color='red' )
    # sns.kdeplot(df_p_c1_impro, color='green' )

    sns.kdeplot(df_np_c1_impro, color='green' )
    sns.kdeplot(df_p_c1_impro, color='red' )
    plt.title(f'C1_dag_type:{dag_type_x}')
    plt.grid(True)
    colore_id = ['preempt', 'non-preempt']
    colore_list = [plt.scatter(0, 0, marker="s", color=cid) for cid in ['red', 'green']]
    plt.legend(colore_list, colore_id, loc='upper right', title='', prop={'family': 'Times New Roman', 'size': 16})
    # plt.show()
    plt.savefig('./Industry{0}_C1.png'.format(dag_type_x))
    plt.close()

    sns.kdeplot(df_np_c2_impro, color='green' )
    sns.kdeplot(df_p_c2_impro, color='red' )
    plt.title(f'C2_dag_type:{dag_type_x}')
    plt.grid(True)
    colore_id = ['preempt', 'non-preempt']
    colore_list = [plt.scatter(0, 0, marker="s", color=cid) for cid in ['red', 'green']]
    plt.legend(colore_list, colore_id, loc='upper right', title='', prop={'family': 'Times New Roman', 'size': 16})
    plt.show()
    plt.savefig('./Industry{0}_C2.png'.format(dag_type_x))
    plt.close()
