


if __name__ == "__main__":
    Dag_ID_List = ['DAG_1', 'DAG_2', 'DAG_3']
    Dag_ID_List = ['M1_S1_C1']
    core1 = Core.Core('c1')
    core1.Insert_Task_Info('M1_S1_C1', node=(1, {'Node_ID': 'job_0', 'Flow_Num': 0}), start_time=0, end_time=1000)
    core1.Insert_Task_Info('DAG_1', node=(1, {'Node_ID': 'job_0'}), start_time=0, end_time=1000)

    core2 = Core.Core('c2')
    core2.Insert_Task_Info('M1_S1_C1', node=(1, {'Node_ID': 'job_1', 'Flow_Num': 0}), start_time=0, end_time=1000)
    core2.Insert_Task_Info('DAG_2', node=(1, {'Node_ID': 'job_1'}), start_time=0, end_time=1000)

    core3 = Core.Core('c3')
    core3.Insert_Task_Info('M1_S1_C1', node=(1, {'Node_ID': 'job_2', 'Flow_Num': 1}), start_time=0, end_time=1000)
    core3.Insert_Task_Info('DAG_3', node=(1, {'Node_ID': 'job_2'}), start_time=0, end_time=1000)
    show_dag_and_makespan(Dag_ID_List, [core1, core2, core3], makespan_res=2000)
    show_dag_and_makespan(Dag_ID_List, [core1, core2, core3], None, 2000, {}, 14)
