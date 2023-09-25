import pandas as pd


df = pd.read_csv('D:/github/DAG_Scheduling_Summary/Exam_Input_data/PD/Dynatic_Exam_test.csv', index_col=None, na_values=["NA"])


test_data = {}
test_num = 1
for dag_num in range(2, 8):
    for core_num in range(2, 8):
        s_impro = df.loc[(df['dag_count'] == dag_num) & (df['core_num'] == core_num), 'self_s_impro'].mean()
        d_impro = df.loc[(df['dag_count'] == dag_num) & (df['core_num'] == core_num), 'self_d_impro'].mean()
        ds_impro = df.loc[(df['dag_count'] == dag_num) & (df['core_num'] == core_num), 'S_D_impro'].mean()
        test_num += 1
        test_data[test_num] = {'dag_count': dag_num, 'core_num': core_num, 's_impro': s_impro, 'd_impro': d_impro, 'ds_impro': ds_impro}

df = pd.DataFrame(test_data).T
df.to_csv('./ret_ss.csv')
