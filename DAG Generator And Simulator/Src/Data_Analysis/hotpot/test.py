import seaborn as sns
# import matplotlib.pyplot as mp
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import combinations
# 密度图

root_addr = "D:/github/DAG_Scheduling_Summary/Exam_Input_data/hotpot/4/Static_Exam_test_new_M2_S2_C1.csv"
df = pd.read_csv(root_addr)
df_s = df[['core_num', 'dag_num', 'FIFO_mean_Makespan', 'FIFO_min_Makespan', 'FIFO_max_Makespan', 'SELF_Makespan']]
max_core_num = int(df_s["core_num"].max())
min_core_num = int(df_s["core_num"].min())
max_dag_num  = int(df_s["dag_num"].max())
min_dag_num  = int(df_s["dag_num"].min())

ccc = np.ones((max_dag_num + 1, max_core_num + 1))     # y:dag_num , x:core_num

for dag_num in range(min_dag_num, max_dag_num + 1):
    for core_num in range(min_core_num, max_core_num + 1):
        data_s = df.loc[(df['dag_num'] == dag_num) & (df['core_num'] == core_num)]

        fifo_min  = float(data_s["FIFO_min_Makespan"])
        fifo_mean = float(data_s["FIFO_mean_Makespan"])
        fifo_max  = float(data_s["FIFO_max_Makespan"])
        self      = float(data_s["SELF_Makespan"])
        # data = round(100 * (fifo_min  - self) / fifo_min,  2)   # min
        # data = round(100 * (fifo_mean - self) / fifo_mean, 2)   # mean
        data = round(100 * (fifo_max - self) / fifo_max, 2)  # max
        ccc[dag_num][core_num] = data  # [y][x]
        print(data)

test_l = False
if test_l:
    yticklabels_list = range(0, max_dag_num + 1)     # dag_num
    xticklabels_list = range(0, max_core_num + 1)    # core_num
    sns.heatmap(ccc, center=0, annot=True, yticklabels=yticklabels_list,  xticklabels=xticklabels_list,)
else:
    show_core_min = 7  # min_core_num
    show_dag_min  = 2  # min_dag_num
    show_core_max = max_core_num
    show_dag_max  = max_dag_num
    ccc_new = ccc[show_dag_min: show_dag_max + 1, show_core_min: show_core_max + 1]
    yticklabels_list = range(show_dag_min, show_dag_max + 1)     # dag_num
    xticklabels_list = range(show_core_min, show_core_max + 1)     # core_num
    sns.heatmap(ccc_new, center=0, annot=True, yticklabels=yticklabels_list,  xticklabels=xticklabels_list,)

# for index in df_s.index:
#     # print(f'core_num:{int(df_s["core_num"].get(index))}')
#     # print(f'dag_num:{int(df_s["dag_num"].get(index))}')
#     # # print(f'FIFO_Makespan:{float(df_s["FIFO_Makespan"].get(index))}')
#     # print(f'FIFO_mean_Makespan:{float(df_s["FIFO_mean_Makespan"].get(index))}')
#     # print(f'SELF_Makespan:{float(df_s["SELF_Makespan"].get(index))}')
#     core_num = int(df_s["core_num"].get(index))
#     dag_num = int(df_s["dag_num"].get(index))
#     fifo_min  = float(df_s["FIFO_min_Makespan"].get(index))
#     fifo_mean = float(df_s["FIFO_mean_Makespan"].get(index))
#     fifo_max  = float(df_s["FIFO_max_Makespan"].get(index))
#     self = float(df_s["SELF_Makespan"].get(index))
#     # data = round(100 * (fifo_min  - self) / fifo_min,  2)   # min
#     # data = round(100 * (fifo_mean - self) / fifo_mean, 2)   # mean
#     data = round(100 * (fifo_max  - self) / fifo_max,  2)     # max
#     if core_num == 1 or dag_num == 1:
#         continue
#     ccc[int(df_s["dag_num"].get(index)) - 2][int(df_s["core_num"].get(index)) - 2] = data   # [y][x]
#     print(data)
#
# sns.heatmap(ccc, center=0, annot=True, yticklabels=yticklabels_list,  xticklabels=xticklabels_list,)

# matric = [
#   [11, 22, 33, 44, 55, 66, 77, 88, 99],
#   [10, 24, 30, 48, 50, 72, 70, 96, 90],
#   [91, 79, 72, 58, 53, 47, 34, 16, 10],
#   [55, 20, 98, 19, 17, 10, 77, 89, 14]]
# covariance_matrix = np.cov(matric)
# # 可视化
# print(covariance_matrix)
#
# sns.heatmap(covariance_matrix, center=0, annot=True, xticklabels=list('abcd'), yticklabels=list('ABCD'))
plt.xlabel('core_num')
plt.ylabel('dag_num')
plt.title('makespan performence(%)')
plt.show()

print(df_s)

"""

df_s = df['Ave_Degree']
df_s = df_s.dropna()    # remove missing values

uniform_data = np.random.rand(10, 12)  # 随机创建10行12列的数组
pd.DataFrame(uniform_data)  # 以一个数据框的格式来显示

f, ax = plt.subplots(figsize=(9, 6))  # 定义一个子图宽高为9和6 ax存储的是图形放在哪个位置
ax = sns.heatmap(uniform_data, vmin=-1, vmax=1)  # vmin,vmax定义了色彩图的上下界
# ax = sns.heatmap(uniform_data, center=0)        #参数center = 0

plt.show()
# sns.heatmap(uniform_data)  #此语句会默认图形的大小画热图
"""