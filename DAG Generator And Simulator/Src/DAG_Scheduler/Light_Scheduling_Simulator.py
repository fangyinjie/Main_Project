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
import copy
from . import Core


# simulation environment
scheduler_to_core_event = {}  # [env.event() for _ in range(Core_Num)]
core_to_scheduler_event = {}  # [env.event() for _ in range(Core_Num)]
Core_Data_List = {}  # [Core.Core_Obj(i) for i in range(Core_Num)]  # core数据列表


# 计算一个DAG
def Test_simulator_test(Dag_Obj, Core_Num):
    env = simpy.Environment()
    task_to_scheduler_event = env.event()

    global scheduler_to_core_event  # [env.event() for _ in range(Core_Num)]
    global core_to_scheduler_event
    global Core_Data_List

    scheduler_to_core_event = {}  # [env.event() for _ in range(Core_Num)]
    core_to_scheduler_event = {}  # [env.event() for _ in range(Core_Num)]
    Core_Data_List = {}

    for core_id in range(Core_Num):
        core_to_scheduler_event[core_id] = env.event()
        scheduler_to_core_event[core_id] = env.event()
        Core_Data_List[core_id] = Core.Core_Obj(core_id)
    # (1) Core_Manager
    for core_id in range(Core_Num):
        assert core_id == Core_Data_List[core_id].Core_ID
        env.process(__Core_Manager(env, core_id))
    # (2) Scheduler
    sss = env.process(__Simulator(env, Dag_Obj, task_to_scheduler_event))
    # (*) start
    task_to_scheduler_event.succeed('DAG_Arrive')

    # (4) system running
    env.run(until=sss)
    return Core_Data_List


def __Core_Manager(env, core_id):
    global scheduler_to_core_event
    global Core_Data_List  # [Core.Core_Obj(i) for i in range(Core_Num)]  # core数据列表
    global core_to_scheduler_event
    while True:
        yield scheduler_to_core_event[core_id]
        while len(Core_Data_List[core_id].Task_allocation_list) > 0:
            Core_Data_List[core_id].Running_node.append(Core_Data_List[core_id].Task_allocation_list.pop(0))        # 预调度任务出队
            start_time = env.now
            Core_Data_List[core_id].Running_node[0] [1]['AST'] = start_time
            Core_Data_List[core_id].Running_node[0] [1]['AFT'] = start_time + Core_Data_List[core_id].Running_node[0] [1]['WCET']
            Core_Data_List[core_id].Running_node[0] [1]['Status'] = "Running"
            yield env.timeout(Core_Data_List[core_id].Running_node[0] [1]['WCET'])
            Core_Data_List[core_id].Running_node[0] [1]['Status'] = "Finish"
            Core_Data_List[core_id].Insert_Task_Info(node=copy.deepcopy(Core_Data_List[core_id].Running_node.pop(0)),
                                       start_time=start_time, end_time=env.now)
            core_to_scheduler_event[core_id].succeed('Job_Finish;{0}'.format(Core_Data_List[core_id].Core_ID))
            core_to_scheduler_event[core_id] = env.event()


def __Simulator(env, dag_x, task_to_scheduler_event):
    global scheduler_to_core_event
    global Core_Data_List  # [Core.Core_Obj(i) for i in range(Core_Num)]  # core数据列表
    global core_to_scheduler_event

    while True:
        ret = yield simpy.AnyOf(env, list(core_to_scheduler_event.values()) + [task_to_scheduler_event])
        task_to_scheduler_event = env.event()
        ret_data = [value.value for value in ret]  # Event that arrive as same time
        random.shuffle(ret_data)
        for ret_data_x in ret_data:                # 获取就绪结点
            if ret_data_x == 'DAG_Arrive':
                pass
            else:
                lst = ret_data_x.split(";")
                if lst[0] == 'Job_Finish':
                    pass
        Ready_list = Ready_Node_Enqueue(dag_x)
        # 就绪结点映射到core
        __Core_Task_Maping(env, Ready_list)
        if all(nx[1]['Status'] == "Finish" for nx in dag_x.nodes(data=True)):
            break


# assign idle core to ready node
def __Core_Task_Maping(env, Ready_list):
    global Core_Data_List
    global scheduler_to_core_event
    while len(Ready_list) > 0:
        idle_core_list = [cd for ci, cd in Core_Data_List.items() if
                          len(cd.Running_node) == 0 and
                          len(cd.Task_allocation_list) == 0]
        if len(idle_core_list) > 0:
            idle_core = idle_core_list.pop(0)  # random.choice(idle_core_list)  # 随机抽取一个核
            Ready_list = sorted(Ready_list, key=lambda x: x[1]['Prio'], reverse=False)
            idle_core.Task_allocation_list.append(Ready_list.pop(0))

            scheduler_to_core_event[int(idle_core.Core_ID)].succeed(f'Job_Arrive{idle_core.Core_ID}')
            scheduler_to_core_event[int(idle_core.Core_ID)] = env.event()
        else:
            break


def Ready_Node_Enqueue(dag_x):
    # (1) Get the block node that all previous nodes have completed
    Ready_list = [nx for nx in dag_x.nodes(data=True) if (nx[1]["Status"] == 'Ready') or
                       (nx[1]["Status"] == 'Block' and all(dag_x.nodes[x]["Status"] == 'Finish' for x in list(dag_x.predecessors(nx[0]))))]
    # (2) change the status of node
    for node_x in Ready_list:
        node_x[1]["Status"] = 'Ready'
    # (3) ready node enqueue
    return Ready_list