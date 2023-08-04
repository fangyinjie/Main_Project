#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Randomized DAG Generator
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################
import random
import simpy

from . import Core
from ..DAG_Configurator import DAG_Priority_Config as DPC
from . import Light_Scheduling_Simulator_new as LSS
import copy


# 基于FIFO的列表式-非抢占-调度
# Enqueue_rank       True        False
# Priority_rank      True        False


class Dispatcher_Workspace(object):
    def __init__(self, Param_List):
        self.Dag_List   = Param_List[0]                 # DAG simble list
        self.Core_Num   = Param_List[1]['Core_Num']     # The number of cores
        self.Total_Time = Param_List[1]["Total_Time"]   # 系统整体的运行时间

        self.Enqueue_rank  = Param_List[1]['Enqueue_rank']    # 是否就绪结点入队排序；
        self.Priority_rank = Param_List[1]['Priority_rank']   # 是否就绪结点出队优先级排序；
        self.Preempt_type  = Param_List[1]['Preempt_type']    # 是否就绪结点出队优先级排序；

        self.Priority_Max_num = sum([dag_x.number_of_nodes() for dag_x in self.Dag_List])
        self.Dynamic = Param_List[1]['Dynamic']  # 是否采用动态调度；
        # self.Non_WC = Param_List[1]['Non_WC']  # 是否采用non-workconserving机制

        self.Ready_list = []  # 就绪结点列表；
        self.Core_Data_List = {i: Core.Core_Obj(i) for i in range(self.Core_Num)}  # core数据列表
        self.Temp_DAG_List = []  # append ['DAG_ID', 'DAGInstID', 'DAG_NUM', 'DAG_obj']

        self.env = simpy.Environment()  # simulation environment
        self.core_to_scheduler_event = [self.env.event() for _ in range(self.Core_Num)]  # 多event解决同时到达问题
        self.task_to_scheduler_event = [self.env.event() for _ in range(len(self.Dag_List))]
        self.scheduler_to_core_event = [self.env.event() for _ in range(self.Core_Num)]
        self.core_task_dict = {}

    def run(self):
        # (1) Task_Mannger
        for task_id in range(len(self.Dag_List)):
            self.env.process(self.__Task_Mannger(task_id))
        # (2) Core_Manager
        for core_id, core_data_x in self.Core_Data_List.items():
            self.core_task_dict[core_id] = self.env.process(self.__Core_Manager(self.Core_Data_List[core_id], core_id))
        # (3) Scheduler
        self.env.process(self.__Simulator())
        # (4) system running
        self.env.run(until=self.Total_Time)

    def __Task_Mannger(self, DAG_id):
        dag_num = 0
        target_dag = self.Dag_List[DAG_id]
        yield self.env.timeout(target_dag.graph['Arrive_time'])
        while dag_num := dag_num + 1:
            Arrive_dag = copy.deepcopy(target_dag)
            Arrive_dag.graph["DAG_NUM"] = dag_num
            # #### ########################## #### #
            self.Temp_DAG_List.append(Arrive_dag)
            self.task_to_scheduler_event[DAG_id].succeed('DAG_Arrive')
            self.task_to_scheduler_event[DAG_id] = self.env.event()
            yield self.env.timeout(target_dag.graph['Period'])

    def __Core_Manager(self, Core_data, core_id):
        assert Core_data.Core_ID == core_id
        start_time = None
        while True:
            yield self.scheduler_to_core_event[Core_data.Core_ID]  # waiting for the cmd of schedulor
            while len(Core_data.Task_allocation_list) > 0:
                try:
                    assert len(Core_data.Task_allocation_list) > 0
                    Core_data.Running_node.append(Core_data.Task_allocation_list.pop(0))
                    start_time = self.env.now
                    Core_data.Running_node[0] [1]['AST'] = start_time
                    Core_data.Running_node[0] [1]['AFT'] = start_time + Core_data.Running_node[0] [1]['WCET']
                    Core_data.Running_node[0] [1]['Status'] = "Running"
                    yield self.env.timeout(Core_data.Running_node[0] [1]['WCET'])
                    Core_data.Running_node[0] [1]['Status'] = "Finish"
                    # ########### 动态机制：更新执行时间后的优先级计算 ############# #
                    if self.Dynamic:
                        Core_data.Running_node[0] [1]['WCET_old'] = Core_data.Running_node[0] [1]['WCET']
                        for node_x in Core_data.Running_node[0] [1]['DAG'].nodes(data=True):
                            node_x[1]['WCET'], node_x[1]['WCET_old'] = node_x[1]['WCET_old'], node_x[1]['WCET']
                        DPC.DMDAG_Priority_Config('SELF', self.Temp_DAG_List)
                        for node_x in Core_data.Running_node[0] [1]['DAG'].nodes(data=True):
                            node_x[1]['WCET'], node_x[1]['WCET_old'] = node_x[1]['WCET_old'], node_x[1]['WCET']
                    # ####################################################### #
                    Core_data.Insert_Task_Info(node=copy.deepcopy(Core_data.Running_node.pop(0)), start_time=start_time, end_time=self.env.now)
                    self.Temp_DAG_List_Updata()
                    self.core_to_scheduler_event[Core_data.Core_ID].succeed('Job_Finish;{0}'.format(core_id))
                    self.core_to_scheduler_event[Core_data.Core_ID] = self.env.event()
                except simpy.Interrupt:
                    assert len(Core_data.Running_node) == 1
                    assert len(Core_data.Task_allocation_list) > 0
                    Core_data.Running_node[0] [1]['WCET'] = Core_data.Running_node[0] [1]['WCET'] - (self.env.now - start_time)
                    Core_data.Running_node[0] [1]['AST'] = self.env.now + Core_data.Running_node[0] [1]['WCET']
                    Core_data.Running_node[0] [1]['AFT'] = self.env.now + Core_data.Running_node[0] [1]['WCET'] + Core_data.Task_allocation_list[0] [1]['WCET']
                    Core_data.Running_node[0] [1]['L_S_T'] = Core_data.Running_node[0] [1]['L_S_T'] + (self.env.now - start_time)
                    Core_data.Insert_Task_Info(node=copy.deepcopy(Core_data.Running_node[0]), start_time=start_time, end_time=self.env.now)
                    Core_data.Task_allocation_list.insert(1, Core_data.Running_node.pop(0))


    def __Simulator(self):
        while True:
            ret = yield simpy.AnyOf(self.env, self.core_to_scheduler_event + self.task_to_scheduler_event)
            ret_data = [value.value for value in ret]  # Event that arrive as same time
            random.shuffle(ret_data)
            for ret_data_x in ret_data:
                cmd_list = ret_data_x.split(';')
                cmd = cmd_list[0]
                if cmd == "DAG_Arrive":
                    pass
                elif cmd == 'Job_Finish':
                    pass
                else:
                    print('cmd type error!')
                self.Ready_Node_Enqueue()
            self.Core_Task_Maping()

    def Temp_DAG_List_Updata(self):
        for dag_x in self.Temp_DAG_List:
            if all(nx[1]['Status'] == "Finish" for nx in dag_x.nodes(data=True)):
                self.Temp_DAG_List.remove(dag_x)

    def Ready_Node_Enqueue(self):
        # (1) Get the block node that all previous nodes have completed
        Ready_node_list = [nx for dag_x in self.Temp_DAG_List for nx in dag_x.nodes(data=True) if
                           (nx[1]["Status"] == 'Block') and all(dag_x.nodes[x]["Status"] == 'Finish' for x in list(dag_x.predecessors(nx[0])))]
        # (2) change the status of node
        for node_x in Ready_node_list:
            node_x[1]["Status"] = 'Ready'
        # (3) ready node enqueue
        if self.Enqueue_rank:
            self.Ready_list += sorted(Ready_node_list, key=lambda x: x[1]['Prio'], reverse=False)
        else:
            Ready_node_list = sorted(Ready_node_list, key=lambda x: x[0], reverse=False)  # index 入队排序
            # random.shuffle(Ready_node_list)  # 随机排序
            self.Ready_list += Ready_node_list

    # assign idle core to ready node
    def Core_Task_Maping(self):
        while len(self.Ready_list) > 0:
            idle_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Running_node) == 0 and len(cd.Task_allocation_list) == 0]
            if len(idle_core_list) > 0:
                # idle_core = random.choice(idle_core_list)                             # (1) 随机抽取一个核
                idle_core_list.sort(key=lambda x: x.last_finish_time, reverse=True)     # (2) 抽取完成时间最大的核（负载最大）
                # idle_core_list.sort(key=lambda x: x.last_finish_time, reverse=False)  # (3) 抽取完成时间最小的核（负载最小）
                idle_core = idle_core_list.pop(0)  # (2) 抽取完成最晚的
                re_node = self.Ready_Node_Dequeue()
                idle_core.Task_allocation_list.append(re_node)

                re_node[1]['AST'] = self.env.now
                re_node[1]['AFT'] = self.env.now + re_node[1]['WCET']
                re_node[1]['Status'] = "Running"

                self.scheduler_to_core_event[int(idle_core.Core_ID)].succeed('Job_Arrive')
                self.scheduler_to_core_event[int(idle_core.Core_ID)] = self.env.event()
            else:
                if self.Preempt_type is not False:   # 抢占模式
                    r_node = self.Ready_Node_Dequeue()      # 即将抢占的结点
                    s_core_list = []
                    if self.Preempt_type == 'type1':    # 全抢占
                        s_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Task_allocation_list) == 0
                                                and (cd.Running_node[0] [1]['Criticality'] > r_node[1]['Criticality'])]
                    elif self.Preempt_type == 'type2':  # 优先级阈值
                        s_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Task_allocation_list) == 0
                                                and (cd.Running_node[0] [1]['Criticality'] > r_node[1]['Criticality'])
                                                and (cd.Running_node[0] [1]['PT'] > r_node[1] ['Prio'])]
                    elif self.Preempt_type == 'type3':  # 关键结点不抢占
                        s_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Task_allocation_list) == 0
                                               and (cd.Running_node[0][1]['Criticality'] > r_node[1]['Criticality'])
                                               and (cd.Running_node[0][1]['critic'] == False)]
                    elif self.Preempt_type == 'type4':
                        # if r_node[1]['Criticality'] == 1:                            # （1） 判定r_node是否是高关键任务，不是则直接跳出；
                        test_time = self.Non_Preempt_makespan(r_node)            # （2） 如果是高关键，计算如果不抢占，高关键任务是否会超时 %5
                        if test_time > 1.05 * r_node[1]['DAG'].graph['block']:    # （3） 如果超时则抢占；否则不抢占；
                            s_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Task_allocation_list) == 0
                                           and (cd.Running_node[0][1]['Criticality'] > r_node[1]['Criticality'])]
                    elif self.Preempt_type == 'typex--':          # 如果 r_node 阻塞时间小于 deadline * 5 %  不抢占  # 下一个调度点：
                        if r_node[1] ['Criticality'] == 1:      # 只有高关键结点方可抢占
                            running_node_list = [node_x for dag_x in self.Temp_DAG_List for node_x in dag_x.nodes(data=True) if node_x[1]['Status'] == "Running"]
                            if len(running_node_list) != 0:
                                # ############### running time compute #################### #
                                next_sch_point = min([node_x[1]['AFT'] for node_x in running_node_list])  # 下一个抢占点
                                r_node[1]['WCET'] += next_sch_point - self.env.now  # 前期设置
                                hi_cri_dag_list = copy.deepcopy([hi_dag for hi_dag in self.Temp_DAG_List if hi_dag.graph['Criticality'] == 1])
                                for hi_dag_x in hi_cri_dag_list:
                                    finish_node = [hi_node_x[0] for hi_node_x in hi_dag_x.nodes(data=True) if hi_node_x[1]['Status'] == "Finish"]
                                    for finish_node_x in finish_node:
                                        hi_dag_x.remove_node(finish_node_x)
                                    for hi_node_x in hi_dag_x.nodes(data=True):
                                        if hi_node_x[1]['Status'] == "Running":
                                            hi_node_x[1]['WCET'] = hi_node_x[1]['WCET'] - (self.env.now - hi_node_x[1]['AST'])
                                        hi_node_x[1]['Status'] = "Block"
                                core_list = LSS.compute_sch_list(DPC.DAG_list_merge(hi_cri_dag_list), self.Core_Num)
                                r_node[1]['WCET'] -= next_sch_point - self.env.now  # 后期设置
                                test_time = self.env.now + Core.ret_makespan({core_id: core_x for core_id, core_x in enumerate(core_list)}) - 2
                                # ############### running time compute #################### #
                                if test_time > 1.05 * r_node[1]['DAG'].graph['block']:  # 如果超了必抢
                                    s_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Task_allocation_list) == 0
                                                   and (cd.Running_node[0][1]['Criticality'] > r_node[1]['Criticality'])]
                    elif self.Preempt_type == 'type5':  # %5 加 阈值如果 r_node 阻塞时间小于 deadline * 5 %  不抢占  # 下一个调度点：
                        # if r_node[1]['Criticality'] == 1:                            # （1） 判定r_node是否是高关键任务，不是则直接跳出；
                        test_time = self.Non_Preempt_makespan(r_node)            # （2） 如果是高关键，计算如果不抢占，高关键任务是否会超时 %5
                        if test_time > 1.05 * r_node[1]['DAG'].graph['block']:   # （3） 如果超时则抢占；否则不抢占；
                            s_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Task_allocation_list) == 0
                                           and (cd.Running_node[0][1]['Criticality'] > r_node[1]['Criticality'])]
                        else:
                            s_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Task_allocation_list) == 0
                                           and (cd.Running_node[0][1]['Criticality'] > r_node[1]['Criticality'])
                                           and (cd.Running_node[0][1]['PT'] > r_node[1]['Prio'])]
                    elif self.Preempt_type == 'type6':  # %5 加 抢占变量 如果 r_node 阻塞时间小于 deadline * 5 %  不抢占  # 下一个调度点：
                        # if r_node[1]['Criticality'] == 1:                           # （1） 判定r_node是否是高关键任务，不是则直接跳出；
                        test_time = self.Non_Preempt_makespan(r_node)           # （2） 如果是高关键，计算如果不抢占，高关键任务是否会超时 %5
                        if test_time > 1.05 * r_node[1]['DAG'].graph['block']:  # （3） 如果超时则抢占；否则不抢占；
                            s_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Task_allocation_list) == 0
                                            and (cd.Running_node[0][1]['Criticality'] > r_node[1]['Criticality'])]
                        else:
                            s_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Task_allocation_list) == 0
                                           and (cd.Running_node[0][1]['Criticality'] > r_node[1]['Criticality'])
                                           # and cd.Running_node[0][1]['preemptable']
                                           and (cd.Running_node[0][1]['PT'] > r_node[1]['PT'])]
                                           # and r_node[1]['preemptable'] ]
                    elif self.Preempt_type == 'type7':  # %5 加 抢占变量 如果 r_node 阻塞时间小于 deadline * 5 %  不抢占  # 下一个调度点：
                        # if r_node[1]['Criticality'] == 1:                           # （1） 判定r_node是否是高关键任务，不是则直接跳出；
                        test_time = self.Non_Preempt_makespan(r_node)           # （2） 如果是高关键，计算如果不抢占，高关键任务是否会超时 %5
                        if test_time > 1.05 * r_node[1]['DAG'].graph['block']:  # （3） 如果超时则抢占；否则不抢占；
                            s_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Task_allocation_list) == 0
                                            and (cd.Running_node[0][1]['Criticality'] > r_node[1]['Criticality'])]
                        else:
                            s_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Task_allocation_list) == 0
                                           and (cd.Running_node[0][1]['Criticality'] > r_node[1]['Criticality'])
                                           and (cd.Running_node[0][1]['preemptable'] or r_node[1]['preemptable'])]
                    elif self.Preempt_type == 'type8':  # %5 加 抢占智能阈值
                        test_time = self.Non_Preempt_makespan(r_node)           # （2） 如果是高关键，计算如果不抢占，高关键任务是否会超时 %5
                        if test_time > 1.05 * r_node[1]['DAG'].graph['block']:  # （3） 如果超时则抢占；否则不抢占；
                            s_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Task_allocation_list) == 0
                                            and (cd.Running_node[0][1]['Criticality'] > r_node[1]['Criticality'])]
                        else:
                            s_core_list = [cd for cid, cd in self.Core_Data_List.items() if len(cd.Task_allocation_list) == 0
                                           and (cd.Running_node[0][1]['Criticality'] > r_node[1]['Criticality'])
                                           and (cd.Running_node[0][1]['preemptable'] > r_node[1]['preemptable'])]
                    else:
                        print('error premmpt type') # and 抢占阈值 = cd.Running_node[0] [1]['Prio'] + (N - cd.Running_node[0] [1]['Prio']) * Ug..
                    if len(s_core_list) > 0:
                        s_core = max(s_core_list, key=lambda x: x.Running_node[0] [1]['Prio'])
                        s_core.Running_node[0] [1]['preempt_test'] = True
                        r_node[1]['preempt_test'] = True
                        s_core.Task_allocation_list.insert(0, r_node)

                        self.core_task_dict[s_core.Core_ID].interrupt()
                    else:
                        self.Ready_list.append(r_node)
                        break
                else:
                    break
        return True

    def Ready_Node_Dequeue(self):
        # (1) Priority rank    # self.Ready_list = sorted(self.Ready_list, key=lambda x: x[0], reverse=False)
        if self.Priority_rank:
            self.Ready_list = sorted(self.Ready_list, key=lambda x: x[1]['Prio'], reverse=False)
        # (2) Criticality rank
        self.Ready_list = sorted(self.Ready_list, key=lambda x: x[1]['Criticality'], reverse=False)
        # (*) non-workconserving 判断
        return self.Ready_list.pop(0)

    def Non_Preempt_makespan(self, r_node):
        running_node_list = []
        for core_id, core_x in self.Core_Data_List.items():
            if len(core_x.Running_node) > 0:
                running_node_list.append(core_x.Running_node[0])
            else:
                running_node_list.append(core_x.Task_allocation_list[0])
        assert len(running_node_list) > 0

        # (1) 获取下一完成时间结点；
        lo_running_node = [ln for ln in running_node_list if ln[1]['Criticality'] == 2]
        if len(lo_running_node) > 0:            # 下一个抢占点时间距离
            next_sch_point = min([node_x[1]['AFT'] for node_x in lo_running_node])
        else:
            next_sch_point = 0
        # (2) 抢占时间计算；
        r_node[1]['DAG'].add_node('Test', WCET=next_sch_point, Prio=r_node[1]['Prio'], Status='Block')
        r_node[1]['DAG'].add_edge('Test', r_node[0])

        hi_cri_dag_list = copy.deepcopy([hi_dag for hi_dag in self.Temp_DAG_List if hi_dag.graph['Criticality'] == 1])

        r_node[1]['DAG'].remove_node('Test')

        for hi_dag_x in hi_cri_dag_list:
            finish_node = [hi_node_x[0] for hi_node_x in hi_dag_x.nodes(data=True) if hi_node_x[1]['Status'] == "Finish"]
            for finish_node_x in finish_node:
                hi_dag_x.remove_node(finish_node_x)
            for hi_node_x in hi_dag_x.nodes(data=True):
                if hi_node_x[1]['Status'] == "Running":
                    hi_node_x[1]['WCET'] = hi_node_x[1]['WCET'] - (self.env.now - hi_node_x[1]['AST'])
                hi_node_x[1]['Status'] = "Block"

        core_list = LSS.compute_sch_list(copy.deepcopy(DPC.DAG_list_merge(hi_cri_dag_list)), self.Core_Num)

        return self.env.now + Core.ret_makespan({core_id: core_x for core_id, core_x in enumerate(core_list)}) - 2
