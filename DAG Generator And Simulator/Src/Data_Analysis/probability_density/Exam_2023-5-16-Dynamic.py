import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm


df = pd.read_csv('D:/github/DAG_Scheduling_Summary/Exam_Input_data/PD/Dynatic_Exam_test_old.csv', index_col=None, na_values=["NA"])

for dag_num in [3, 4, 5, 6, 7]:
    for jitter in [0.1, 0.3, 0.5]:
        df_filter = df.loc[(df['DAG_num'] == dag_num) & (df['jitter'] == jitter)]
        ret_data = {}
        for index in df_filter.index:
            FIFO_Mean_MAKESPAN = float(df_filter["FIFO_Mean_MAKESPAN"].get(index))
            FIFO_Max_MAKESPAN = float(df_filter["FIFO_Max_MAKESPAN"].get(index))
            SELF_S_MAKESPAN = float(df_filter["SELF_S_MAKESPAN"].get(index))
            SELF_D_MAKESPAN = float(df_filter["SELF_D_MAKESPAN"].get(index))

            print(f'FIFO_Mean_MAKESPAN:{FIFO_Mean_MAKESPAN}')
            print(f'FIFO_Max_MAKESPAN:{FIFO_Max_MAKESPAN}')
            print(f'SELF_S_MAKESPAN:{SELF_S_MAKESPAN}')
            print(f'SELF_D_MAKESPAN:{SELF_D_MAKESPAN}')

            dynamic_mean_impro = 100 * (FIFO_Mean_MAKESPAN - SELF_D_MAKESPAN) / FIFO_Mean_MAKESPAN
            dynamic_max_impro  = 100 * (FIFO_Max_MAKESPAN  - SELF_D_MAKESPAN) / FIFO_Max_MAKESPAN
            static_mean_impro  = 100 * (FIFO_Mean_MAKESPAN - SELF_S_MAKESPAN) / FIFO_Mean_MAKESPAN
            static_max_impro   = 100 * (FIFO_Max_MAKESPAN  - SELF_S_MAKESPAN) / FIFO_Max_MAKESPAN

            ret_data[index] = {'dynamic_improve': dynamic_max_impro, 'static_improve': static_max_impro}

        df1 = pd.DataFrame(ret_data)
        df1 = df1.T

        kde = sns.kdeplot(df1)
        plt.title(f'jitter:{jitter}__dag_num:{dag_num}')
        plt.grid(True)
        plt.show()

