import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm
import random



addr_list1 = 'D:/github/DAG_Scheduling_Summary/Data_Process/Data/7-14/7-14-hi_f2_workload.csv'
addr_list2 = 'D:/github/DAG_Scheduling_Summary/Data_Process/Data/7-14/7-14-hi_f3_workload.csv'
addr_list3 = 'D:/github/DAG_Scheduling_Summary/Data_Process/Data/7-14/7-14-hi_f4_workload.csv'


df1 = pd.read_csv(addr_list1, index_col=None, na_values=["NA"])
df2 = pd.read_csv(addr_list2, index_col=None, na_values=["NA"])
df = pd.read_csv(addr_list3, index_col=None, na_values=["NA"])

# df = pd.concat([df1, df2, df3])
# df = df.loc[df['LP4_workload_rade'] > df['P_workload_rade'] ]
# df = df.loc[(df['LP2_c1_surpass_rade'] >= 0)]
# df = df.loc[(df['LP1_c1_surpass_rade'] >= 0) & (df['LP1_c1_surpass_rade'] <= 5)]
# df = df.loc[df['LP2_c1_surpass_rade'] < 5]
# df = df.loc[df['LP3_c1_surpass_rade'] < 5]
# df = df.loc[df['LP4_c1_surpass_rade'] < 5]
# df = df1 + df2 + df3

LP1_c1_surpass_rade = df['LP1_c1_surpass_rade']
LP1_makespan = df['LP1_makespan']
LP1_makespan_c1 = df['LP1_makespan_c1']
LP1_makespan_c2 = df['LP1_makespan_c2']
LP1_workload_rade = df['LP1_workload_rade']
LP2_c1_surpass_rade = df['LP2_c1_surpass_rade']
LP2_makespan = df['LP2_makespan']
LP2_makespan_c1 = df['LP2_makespan_c1']
LP2_makespan_c2 = df['LP2_makespan_c2']
LP2_workload_rade = df['LP2_workload_rade']
LP3_c1_surpass_rade = df['LP3_c1_surpass_rade']
LP3_makespan = df['LP3_makespan']
LP3_makespan_c1 = df['LP3_makespan_c1']
LP3_makespan_c2 = df['LP3_makespan_c2']
LP3_workload_rade = df['LP3_workload_rade']
LP4_c1_surpass_rade = df['LP4_c1_surpass_rade']
LP4_makespan = df['LP4_makespan']
LP4_makespan_c1 = df['LP4_makespan_c1']
LP4_makespan_c2 = df['LP4_makespan_c2']
LP4_workload_rade = df['LP4_workload_rade']
NP_c1_surpass_rade = df['NP_c1_surpass_rade']
NP_makespan_c1 = df['NP_makespan_c1']
NP_makespan_c2 = df['NP_makespan_c2']
NP_workload_rade = df['NP_workload_rade']
P_c1_surpass_rade = df['P_c1_surpass_rade']
P_makespan = df['P_makespan']
P_makespan_c1 = df['P_makespan_c1']
P_makespan_c2 = df['P_makespan_c2']
P_workload_rade = df['P_workload_rade']
# """


# sns.distplot(a, bins=None, hist=True, kde=True, rug=False, fit=None, hist_kws=None, kde_kws=None, rug_kws=None, fit_kws=None, color=None, vertical=False, norm_hist=False, axlabel=None, label=None, ax=None)
sns.histplot(LP1_c1_surpass_rade, kde=True, color='green')
sns.histplot(LP2_c1_surpass_rade, kde=True, color='red')
sns.histplot(LP3_c1_surpass_rade, kde=True, color='black')
sns.histplot(LP4_c1_surpass_rade, kde=True, color='blue')
# sns.distplot(LP2_c1_surpass_rade, color='red')
# sns.kdeplot(LP1_c1_surpass_rade, color='green')
# sns.kdeplot(LP2_c1_surpass_rade, color='red')
# sns.kdeplot(LP3_c1_surpass_rade, color='black')
# sns.kdeplot(LP4_c1_surpass_rade, color='blue')


# colore_list = [plt.scatter(0, 0, marker="s", color='green'),  plt.scatter(0, 0, marker="s", color='red')]
# colore_id = ['FP', 'LP']
# plt.legend(colore_list, colore_id, loc='upper right', title='', prop={'family': 'Times New Roman', 'size': 16})
plt.title(f'test')
plt.grid(True)
plt.show()
# """
sns.kdeplot(100 * (LP1_workload_rade - P_workload_rade) / LP1_workload_rade, color='green')
sns.kdeplot(100 * (LP2_workload_rade - P_workload_rade) / LP2_workload_rade, color='red')
sns.kdeplot(100 * (LP3_workload_rade - P_workload_rade) / LP3_workload_rade, color='black')
sns.kdeplot(100 * (LP4_workload_rade - P_workload_rade) / LP4_workload_rade, color='blue')



# colore_list = [plt.scatter(0, 0, marker="s", color='green'),  plt.scatter(0, 0, marker="s", color='red')]
# colore_id = ['FP', 'LP']
# plt.legend(colore_list, colore_id, loc='upper right', title='', prop={'family': 'Times New Roman', 'size': 16})
plt.title(f'test')
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
