import numpy as np
import os
import xlrd
import csv
import random
import matplotlib.pyplot as plt
import sys
import networkx as nx
import simpy
import Core
import copy
import DAG
import Makespan_pic_new_wj1 as Makespan_pic


TTL = 1130000


class Dispatcher_Workspace(object):
    """ 一个处理器（Processor），拥有特定数量的资源（core，内存，缓存等）。一个客户首先申请服务。在对应服务时间完成后结束并离开工作站 """
    def __init__(self, environment, Param_List):
        self.env = environment
        self.Dag_List = Param_List[0]
        self.Core_Num = Param_List[1]['Core_Num']
        self.Run_Type = Param_List[1]["Run_Type"]

        self.Ready_list = []
        self.Temp_DAG_Dict = {dag_x.graph["DAG_ID"]: {} for dag_x in self.Dag_List}
        self.Core_Data_List = []

        self.core_to_scheduler_event = [self.env.event() for i in range(self.Core_Num)]       # 多event解决同时到达问题
        self.task_to_scheduler_event = [self.env.event() for i in range(len(self.Dag_List))]
        self.scheduler_to_core_event = self.env.event()

    def run(self):
        for i in range(self.Core_Num):              # process list 1__# Core process
            core_data = Core.Core_Obj(i)
            self.Core_Data_List.append(core_data)
            self.env.process(self.Core_act(core_data, i))
        for task_id in range(len(self.Dag_List)):   # process list 2__# Task process
            self.env.process(self.Task_Mannger(task_id))
        self.env.process(self.Scheduler())          # process 3__# Scheduler

    def Task_Mannger(self, task_id):
        dag_num = 0
        target_dag = self.Dag_List[task_id]
        target_dag_id = target_dag.graph["DAG_ID"]
        yield self.env.timeout(target_dag.graph['Arrive_time'])
        while True:
            Arrive_dag = copy.deepcopy(target_dag)
            Arrive_dag.graph["DAG_NUM"] = dag_num
            Arrive_dag.graph["Status"] = "UnFinish"
            self.Temp_DAG_Dict[Arrive_dag.graph["DAG_ID"]][Arrive_dag.graph["DAG_NUM"]] = Arrive_dag
            self.task_to_scheduler_event[task_id].succeed('DAG_Arrive;{0};{1};'.format(target_dag_id, dag_num))
            self.task_to_scheduler_event[task_id] = self.env.event()
            yield self.env.timeout(target_dag.graph['Period'])
            dag_num += 1

    def Scheduler(self):
        while True:
            ret = yield simpy.AnyOf(self.env, self.core_to_scheduler_event + self.task_to_scheduler_event)
            ret_data = [[key, value.value] for key, value in enumerate(ret)]
            random.shuffle(ret_data)    # 随机打乱： 同时到达的event
            for ret_data_x in ret_data:
                ret_data_x_list = ret_data_x[1].split(';')  # 指令以及参数获取 cmd；{DAG_ID}；{DAG_NUM}；{--NODE_ID}
                cmd = ret_data_x_list[0]
                if cmd == "DAG_Arrive":
                    self.update_node_state()  # 更新系统的就绪结点 Ready
                    # (1) 如果NUM > 0 则， 检查NUM - 1的D此AG是否完成，
                    #   如果没有完成，马上终止所有运行此DAG的core进程，
                elif cmd == "Job_Finish":
                    dag_id = ret_data_x_list[1]
                    dag_num = int(ret_data_x_list[2])
                    node_id = int(ret_data_x_list[3])
                    self.Temp_DAG_Dict[dag_id][dag_num].nodes(data=True)[node_id]['Status'] = "Finish"  # node finish
                    self.update_node_state()
                else:
                    sys.exit("cmd input scheduler error! input cmd:\"" + cmd + "\"")

            self.scheduler_to_core_event.succeed('Job_Arrive')
            self.scheduler_to_core_event = self.env.event()

    def Core_act(self, Core_data, Core_ID):
        while True:
            ret = yield self.scheduler_to_core_event  # 目前ret只有"Job_Arrive"一种情况，后面添加再改
            if len(self.Ready_list) > 0:  # 有就绪结点数量，如果没有则直接跳过；
                if self.Run_Type != "FIFO":
                    self.Ready_list = sorted(self.Ready_list, key=lambda x: x[2][1]['Prio'], reverse=False)  # 优先级排序
                self.Ready_list = sorted(self.Ready_list, key=lambda x: x[2][1]['Criticality'], reverse=False)
                obj_node = self.Ready_list.pop(0)  # 选取一个节点；
                obj_dag_id = obj_node[0]
                obj_dag_num = obj_node[1]
                obj_node_id = obj_node[2][0]
                obj_node_data = obj_node[2][1]
                obj_node_data["Status"] = "Running"
                obj_node_data["Start_time"] = self.env.now
                obj_node_data["End_time"] = self.env.now + obj_node_data['WCET']
                Core_data.Insert_Task_Info(dag_ID=obj_dag_id, dag_NUM=obj_dag_num, node=obj_node[2], start_time=self.env.now, end_time=self.env.now + obj_node_data['WCET'])  # data save
                yield self.env.timeout(obj_node_data['WCET'])
                if len(list(self.Temp_DAG_Dict[obj_dag_id][obj_dag_num].successors(obj_node_id))) == 0:
                    self.Temp_DAG_Dict[obj_dag_id][obj_dag_num].graph["Status"] = "Finish"
                self.core_to_scheduler_event[Core_ID].succeed('Job_Finish;{0};{1};{2}'.format(obj_dag_id, obj_dag_num, obj_node_id))
                self.core_to_scheduler_event[Core_ID] = self.env.event()

    def get_makespan(self):
        all_core_data = []
        for core_data_x in self.Core_Data_List:
            all_core_data += core_data_x.Core_Running_Task
        all_core_data = sorted(all_core_data, key=lambda x: x['end_time'], reverse=True)
        return all_core_data[0]['end_time']

    def get_workload(self):
        vol = 0
        for dag_id, dag_obj_dict in self.Temp_DAG_Dict.items():
            for num_id, dag_obj in dag_obj_dict.items():
                for node_x in dag_obj.nodes(data=True):
                    vol += node_x[1]["WCET"]
        return vol


    def get_Dag_Etime(self, dag):
        if dag.graph['Status'] == "UnFinish":
            print("DAG_MAKESPAN_ERROR")
            return False
        dag_stime = min([node_x[1]["Start_time"] for node_x in dag.nodes(data=True)])
        dag_ftime = max([node_x[1]["End_time"] for node_x in dag.nodes(data=True)])
        return dag_ftime - dag_stime

    def update_node_state(self):
        ret = []
        for DAG_ID, DAG_Obj_Dict in self.Temp_DAG_Dict.items():     # target:   Temp_DAG_Dict ——》 DAG struct
            for DAG_Obj_NUM, DAG_x in DAG_Obj_Dict.items():         # target:   DAG struct ——》 DAG obj
                for node_x in DAG_x.nodes(data=True):               # target:   DAG obj ——》 node
                    if node_x[1]["Status"] == 'Block':              # target：  node中的Block结点；
                        Pnode_list = list(DAG_x.predecessors(node_x[0]))
                        # 选取 无前驱结点（source结点） -- 或者 -- 前驱结点都Finish的结点
                        if len([x for x in Pnode_list if DAG_x.nodes(data=True)[x]["Status"] != "Finish"]) == 0:
                            node_x[1]["Status"] = 'Ready'               # 改变结点状态
                            ret.append([DAG_ID, DAG_Obj_NUM, node_x])   # 进入就绪队列
        # # todo 入队策略 (3) 选择进入就绪队列的方式
        random.shuffle(ret)  # 1) 随机打乱
        self.Ready_list += ret

    def DAG_Result_Data_updata(self):
        # 计算DAG的执行时间和执行情况
        for ret_dag_id, ret_dag_obj_dict in self.Temp_DAG_Dict.items():
            for ret_dag_num, ret_dag_obj_x in ret_dag_obj_dict.items():
                if ret_dag_obj_x.graph['Status'] == "Finish":
                    node_start_time_list = []
                    node_finish_time_list = []
                    for node_x in ret_dag_obj_x:
                        node_start_time_list.append(ret_dag_obj_x.nodes(data=True)[node_x]['Start_time'])
                        node_finish_time_list.append(ret_dag_obj_x.nodes(data=True)[node_x]['End_time'])
                    ret_dag_obj_x.graph["start_time"] = min(node_start_time_list)
                    ret_dag_obj_x.graph["finish_time"] = max(node_finish_time_list)
                    ret_dag_obj_x.graph["excetion_time"] = ret_dag_obj_x.graph["finish_time"] - ret_dag_obj_x.graph["start_time"]


def self_prio_config(Intput_DAG_set):
    temp_dag = nx.DiGraph()

    for idag_x in Intput_DAG_set:
        temp_dag = nx.disjoint_union(idag_x, temp_dag)

    source_node_num = len(list(temp_dag.nodes()))
    temp_dag.add_node(source_node_num, Node_Index=source_node_num, name='source', WCET=1)
    nu_pred_node = [tdn_x for tdn_x in temp_dag.nodes() if len(list(temp_dag.predecessors(tdn_x))) == 0]
    for nup_x in nu_pred_node:
        temp_dag.add_edge(source_node_num, nup_x)

    sink_node_num = len(list(temp_dag.nodes()))
    temp_dag.add_node(sink_node_num, Node_Index=sink_node_num, name='sink', WCET=1)
    nu_succ_node = [tdn_x for tdn_x in temp_dag.nodes() if len(list(temp_dag.successors(tdn_x))) == 0]
    for nus_x in nu_succ_node:
        temp_dag.add_edge(nus_x, sink_node_num)

    all_path = [(path, sum([temp_dag.nodes[path_x]['WCET'] for path_x in path])) for path in
                nx.all_simple_paths(temp_dag, source_node_num, sink_node_num)]
    all_path = sorted(all_path, key=lambda x: x[1], reverse=True)
    all_cpath = [path_x[0] for path_x in all_path if path_x[1] == all_path[0][1]]
    cp = []
    for cpp in all_cpath:
        cp += cpp
    cp = [i for n, i in enumerate(cp) if i not in cp[:n]]
    group_l = {nodex[0]: [] for nodex in temp_dag.nodes(data=True)}

    for cpx in all_cpath:
        temp_dag_c = copy.deepcopy(temp_dag)
        temp_group = []
        for cp_node in cpx:
            cp_node_pred = nx.ancestors(temp_dag_c, cp_node)  # list(temp_dag.predecessors( cp_node ))
            if len(cp_node_pred) > 0:
                temp_group.append(cp_node_pred)
                for temp_n in cp_node_pred:
                    temp_dag_c.remove_node(temp_n)
        for x, t_l in enumerate(temp_group):
            for t_lx in t_l:
                tl = group_l[t_lx]
                tl.append(x)
    group_l = {key: min(node_x) for key, node_x in group_l.items() if len(node_x) != 0}

    # step2. 计算后继最长路径
    for node_x in temp_dag.nodes():
        wcet_list = []
        for path_x in nx.all_simple_paths(temp_dag, node_x, sink_node_num):
            temp_wcet_list = []
            for node_x_t in path_x:
                temp_wcet_list.append(temp_dag.nodes[node_x_t]["WCET"])
            wcet_list.append(sum(temp_wcet_list))
        # wcet_list = [sum( [node_x['WCET'] for node_x in path_x] ) for path_x in nx.all_simple_paths(temp_dag, node_x, sink_node_num)]
        # print(wcet_list)
        if len(wcet_list) == 0:
            temp_dag.nodes[node_x]['cl'] = 0
        else:
            temp_dag.nodes[node_x]['cl'] = max(wcet_list)

    # step3. wcet 排序 默认；
    # step4. w是否是关键路径；
    # 开始赋予优先级：
    t_g = []
    for sx, tx in group_l.items():
        # for sx, tx in enumerate(temp_group):
        #     for txx in tx:
        v = 1 if sx in cp else (2)
        t_g.append((sx, tx, temp_dag.nodes[sx]['cl'], temp_dag.nodes[sx]['WCET'], v))

    t_g = sorted(t_g, key=lambda x: x[4])  # 是否在关键路径中 默认从小到大
    t_g = sorted(t_g, key=lambda x: x[3], reverse=True)
    t_g = sorted(t_g, key=lambda x: x[2], reverse=True)
    t_g = sorted(t_g, key=lambda x: x[1])

    for sx, tgx in enumerate(t_g):
        temp_dag.nodes[tgx[0]]['Priority'] = sx

    Intput_DAG_dict = {idag_x.graph['DAG_ID']: idag_x for idag_x in Intput_DAG_set}
    for t_node_x in temp_dag.nodes(data=True):
        if (t_node_x[0] == source_node_num) or (t_node_x[0] == sink_node_num):
            continue
        s_node_x = Intput_DAG_dict[t_node_x[1]["DAG_ID"]].nodes[t_node_x[1]['Node_Index']]
        s_node_x['Prio'] = t_node_x[1]['Priority']


def input_dag_criticality(dag):
    # 1 "High" # 2 "Middle # 3 "Low"
    if dag.graph['Criticality'] == 1:
        return "H"  # "High"
    elif dag.graph['Criticality'] == 2:
        return "M"  # "Middle"
    elif dag.graph['Criticality'] == 3:
        return "L"  # "Low"
    else:
        return "Error"


Env_Param_Dict = {
    # 'Priority_Type': 'Mode-1',
    #                   Mode-1 ： 各DAG独自赋予优先级；
    # 总运行时间取最大周期，所有DAG只执行一次，计算最后的完成时间；
    #                   Mode-2 ： 以输入的总运行时间为准，每个个DAG运行（T/P向下取整）次，周期执行；
    #                   Mode-3 ： 以输入的总运行时间为准，每个个DAG运行（T/P向下取整）次，周期执行；
    # 'Merge':  True，DAG合并赋予优先级；
    #           False，DAG分别赋予优先级；

    "case1": {'Run_Type':    'HUAWEI',
              'DAG_ID_List': ['M1_S2_C1',           'M2_S2_C1',          'M1_S2_C2'],
              'Criticality': {'M1_S2_C1': 1,        'M2_S2_C1': 1,       'M1_S2_C2': 3},
              'Period':      {'M1_S2_C1': 1 * TTL,  'M2_S2_C1': 2 * TTL, 'M1_S2_C2': 1 * TTL},
              'Arrive_time': {'M1_S2_C1': 0,        'M2_S2_C1': 0,       'M1_S2_C2': 0},
              "Merge":      False
              },
    "case2": {'Run_Type':    'SELF',
              'DAG_ID_List': ['M1_S2_C1',           'M2_S2_C1',          'M1_S2_C2'],
              'Criticality': {'M1_S2_C1': 1,        'M2_S2_C1': 2,       'M1_S2_C2': 3},
              'Period':      {'M1_S2_C1': 1 * TTL,  'M2_S2_C1': 2 * TTL, 'M1_S2_C2': 1 * TTL},
              'Arrive_time': {'M1_S2_C1': 0,        'M2_S2_C1': 0,       'M1_S2_C2': 0},
              "Merge":      False
              },
    "case3": {'Run_Type':    'SELF',
              'DAG_ID_List': ['M1_S2_C1',           'M2_S2_C1',          'M1_S2_C2'],
              'Criticality': {'M1_S2_C1': 1,        'M2_S2_C1': 3,       'M1_S2_C2': 2},
              'Period':      {'M1_S2_C1': 1 * TTL,  'M2_S2_C1': 2 * TTL, 'M1_S2_C2': 1 * TTL},
              'Arrive_time': {'M1_S2_C1': 0,        'M2_S2_C1': 0,       'M1_S2_C2': 0},
              "Merge":      False
              },

    "case4": {'Run_Type':       'HUAWEI',  # 'FIFO',
              'DAG_ID_List':    ['M1_S2_C1',            'M2_S2_C1'],
              'Criticality':    {'M1_S2_C1': 1,         'M2_S2_C1': 1},
              'Period':         {'M1_S2_C1': 1 * TTL,   'M2_S2_C1': 2 * TTL},
              'Arrive_time':    {'M1_S2_C1': 0,         'M2_S2_C1': 0},
              "Merge":         False
              },
    "case5":  # 赋予DAG关键级别，分别赋予DAG结点优先级；
             {'Run_Type':       'SELF',
              'DAG_ID_List':    ['M1_S2_C1',            'M2_S2_C1'],
              'Criticality':    {'M1_S2_C1': 1,         'M2_S2_C1': 2},
              'Period':         {'M1_S2_C1': 1 * TTL,   'M2_S2_C1': 2 * TTL},
              'Arrive_time':    {'M1_S2_C1': 0,         'M2_S2_C1': 0},
              "Merge":         False
              },
    "case6":  # 不赋予DAG关键级别，但是合并赋予DAG结点优先级；
             {'Run_Type':       'SELF',
              'DAG_ID_List':    ['M1_S2_C1',            'M2_S2_C1'],
              'Criticality':    {'M1_S2_C1': 1,         'M2_S2_C1': 1},
              'Period':         {'M1_S2_C1': 1 * TTL,   'M2_S2_C1': 2 * TTL},
              'Arrive_time':    {'M1_S2_C1': 0,         'M2_S2_C1': 0},
              "Merge":         True
              },
    "case7":  # 不赋予DAG关键级别，但是合并赋予DAG结点优先级；
        {'Run_Type':        'SELF',
         'DAG_ID_List':     ['M1_S2_C1',            'M2_S2_C1'],
         'Criticality':     {'M1_S2_C1': 1,         'M2_S2_C1': 1},
         'Period':          {'M1_S2_C1': 1 * TTL,   'M2_S2_C1': 2 * TTL},
         'Arrive_time':     {'M1_S2_C1': 0,         'M2_S2_C1': 0},
         "Merge":           False
         }
}


def DAG_data_initial(all_dag_list, case, core_num):
    dag_list = []
    for dag_id_x in Env_Param_Dict[case]["DAG_ID_List"]:
        # （1）分配DAG的关键性；
        all_dag_list[dag_id_x].graph["Criticality"] = Env_Param_Dict[case]["Criticality"][dag_id_x]
        for node_x in all_dag_list[dag_id_x].nodes(data=True):
            node_x[1]["Criticality"] = all_dag_list[dag_id_x].graph["Criticality"]
        # （2）分配DAG的运行周期；
        all_dag_list[dag_id_x].graph["Period"] = Env_Param_Dict[case]["Period"][dag_id_x]
        # （3）分配DAG的到达时间；
        all_dag_list[dag_id_x].graph["Arrive_time"] = Env_Param_Dict[case]["Arrive_time"][dag_id_x]
        # （4）dag对象整合；
        dag_list.append(all_dag_list[dag_id_x])
    if Env_Param_Dict[case]["Run_Type"] == "SELF":
        if Env_Param_Dict[case]["Merge"]:
            self_prio_config(dag_list)
        else:
            for dag_x in dag_list:
                self_prio_config([dag_x])
    return [dag_list, {'Core_Num': core_num, 'Run_Type': Env_Param_Dict[case]["Run_Type"]}], Env_Param_Dict[case]["DAG_ID_List"]


def DAG_data_initial_MINE(all_dag_list, param_dict, core_num):
    # (1)执行时间分配；
    ret_list = []
    ret_dag_id_list = []
    for dag_i, dag_x in enumerate(all_dag_list):
        ret_temp_list = []
        for tdag_i in range(10):        # 每个DAG复制10个
            temp_dag_x = copy.deepcopy(dag_x)
            temp_dag_x.graph['DAG_ID'] = tdag_i + dag_i * len(all_dag_list)      # (1) DAG_ID 定义；
            temp_dag_x.graph['Criticality'] = dag_i + 1                          # (2) Criticality 定义；
            temp_dag_x.graph['Period'] = param_dict['Period']                    # (3) DAG的Period 定义；
            temp_dag_x.graph["Arrive_time"] = 0                                  # (4) DAG的到达时间 定义；
            for node_x in temp_dag_x.nodes(data=True):
                node_x[1]["Criticality"] = temp_dag_x.graph["Criticality"]
                node_x[1]["WCET"] = random.randint(param_dict['WCET'][0], param_dict['WCET'][1])
                node_x[1]["Node_Index"] = node_x[0]
            if param_dict['Virtual_node']:
                temp_dag_x[0]['WCET'] = 0
                temp_dag_x[temp_dag_x.number_of_nodes() - 1]['WCET'] = 0
            ret_temp_list.append(temp_dag_x)
        # 分配优先级
        if param_dict['Run_Type'] == 'SELF':
            self_prio_config(ret_temp_list)
        elif param_dict['Run_Type'] == 'FIFO':
            for tdag_x in ret_temp_list:
                for tnode_x in tdag_x.nodes(data=True):
                    tnode_x[1]["Prio"] = 1
        elif param_dict['Run_Type'] == 'ONLY_IN':
            self_prio_config(ret_temp_list)
        elif param_dict['Run_Type'] == 'P_PRESS':
            pass
        else:
            pass
        ret_list += ret_temp_list
    return [ret_list, {'Core_Num': core_num, 'Run_Type': param_dict["Run_Type"]}], ret_dag_id_list
    # for DAG_ID, DAG_x in enumerate(DAG_list):
    #     self.DAG_Param_Update(DAG_x)


if __name__ == "__main__":
    G = DAG.DAG_Generator()

    ret_up_list = []
    core_number = 4
    Total_Time = 2 * TTL

    case_list = ['case4', 'case5', 'case6', 'case7']
    case_x = 'case4'

    Generat_Type_List = ['GNM', 'GNP', 'MINE', 'USER']
    Generat_Type = 'MINE'

    example_type_list = ["FIFO", "SELF", 'ONLY_IN', 'P_PRESS']
    # for case_x in case_list:
    for exam_type_x in example_type_list:
        result_data_dict = {}
        Param_Dict = {'Node_Num':         37,
                      'Critic_Path':      7,
                      'Jump_level':       1,
                      'Max_in_degree':    15,
                      'Max_out_degree':   5,
                      'Width':            15,
                      'Max_Shape':        15,
                      'Min_Shape':        1,
                      'Connection_ratio': 0.0886
                      }
        # All_DAG_Dict = G.Main_Workbench('USER', {"Address": './data/DAG_Data.xlsx'})
        All_DAG_Dict = G.Main_Workbench(Generat_Type, Param_Dict, DAG_Num=1)
        if Generat_Type == 'MINE':
            param_dict = {'Period':         Total_Time,
                          'WCET':           [3032, 264088],
                          'Run_Type':       Generat_Type,
                          'Virtual_node':   True }
            param_l, dag_id_list = DAG_data_initial_MINE(All_DAG_Dict, param_dict, core_num=core_number)
        else:
            param_l, dag_id_list = DAG_data_initial(All_DAG_Dict, case_x, core_num=core_number)
        # (1)   FIFO    实验1 有关键级，无优先级，FIFO处理，同结点释放同时到达的结点随机分布；取最大值；
        # (2)   SELF    实验2 有关键级，同关键级DAG融合计算优先级，无优先级，FIFO处理；
        # (3)   ONLY_IN 实验3 有优先级，但是只在入队时使用；
        # (4)   P_PRESS 实验4
        ret_list = []
        for x in range(100):
            env = simpy.Environment()
            Dispatcher = Dispatcher_Workspace(env, param_l)
            Dispatcher.run()
            env.run(until=Total_Time)
            #  (1) 计算整个系统中的最后完成时间；
            temp_ret_dict = {"makespan": Dispatcher.get_makespan()}
            #  (2) 计算每个DAG【dag_obj1, obj2 ……】的最长运行时间；
            temp_dag_max_etime = {}
            for t_dag_id, t_dag_obj_dict in Dispatcher.Temp_DAG_Dict.items():
                temp_dag_max_etime[t_dag_id] = max([Dispatcher.get_Dag_Etime(tdo_x) for _, tdo_x in t_dag_obj_dict.items()])
            temp_ret_dict["etime_dict"] = temp_dag_max_etime
            #  (3) core_data_list
            temp_ret_dict["core_data_list"] = Dispatcher.Core_Data_List
            #  (4) work-load
            temp_ret_dict["workload"] = Dispatcher.get_workload()
            #  (5) 数据入队；
            ret_list.append(temp_ret_dict)
        ret_up_list.append(ret_list)

    ax = plt.subplot(5, 1, 1)
    ret_max_data = sorted(ret_up_list[0], key=lambda x: x["etime_dict"]['M1_S2_C1'], reverse=True)[0]
    Makespan_pic.show_dag_and_makespan(ret_max_data["core_data_list"], Total_Time, ax, font_size=8)
    ax.set_ylabel('HW_Prio Scheduling\n M1_S2_C1_max', fontdict={'family': 'Times New Roman', 'size': 10})
    print("M1_S2_C1 Etime = {0}".format(ret_max_data['etime_dict']['M1_S2_C1']))
    print("M2_S2_C1 Etime = {0}".format(ret_max_data['etime_dict']['M2_S2_C1']))

    ax = plt.subplot(5, 1, 2)
    ret_max_data = sorted(ret_up_list[0], key=lambda x: x["etime_dict"]['M2_S2_C1'], reverse=True)[0]
    Makespan_pic.show_dag_and_makespan(ret_max_data["core_data_list"], Total_Time, ax, font_size=8)
    ax.set_ylabel('HW_Prio Scheduling\n M2_S2_C1_max', fontdict={'family': 'Times New Roman', 'size': 10})
    print("M1_S2_C1 Etime = {0}".format(ret_max_data['etime_dict']['M1_S2_C1']))
    print("M2_S2_C1 Etime = {0}".format(ret_max_data['etime_dict']['M2_S2_C1']))

    ax = plt.subplot(5, 1, 3)
    # ret_max_data = sorted(ret_up_list[1], key=lambda x: x["etime_dict"]['M2_S2_C1'], reverse=True)[0]
    ret_max_data = ret_up_list[1][0]
    Makespan_pic.show_dag_and_makespan(ret_max_data["core_data_list"], Total_Time, ax, font_size=8)
    ax.set_ylabel('MINE_Prio Scheduling\n', fontdict={'family': 'Times New Roman', 'size': 10})
    print("MINE_M1_S2_C1 Etime = {0}".format(ret_max_data['etime_dict']['M1_S2_C1']))
    print("MINE_M2_S2_C1 Etime = {0}".format(ret_max_data['etime_dict']['M2_S2_C1']))

    ax = plt.subplot(5, 1, 4)
    # ret_max_data = sorted(ret_up_list[1], key=lambda x: x["etime_dict"]['M2_S2_C1'], reverse=True)[0]
    ret_max_data = ret_up_list[2][0]
    Makespan_pic.show_dag_and_makespan(ret_max_data["core_data_list"], Total_Time, ax, font_size=8)
    ax.set_ylabel('MINE_Prio Scheduling\n', fontdict={'family': 'Times New Roman', 'size': 10})
    print("MINE_M1_S2_C1 Etime = {0}".format(ret_max_data['etime_dict']['M1_S2_C1']))
    print("MINE_M2_S2_C1 Etime = {0}".format(ret_max_data['etime_dict']['M2_S2_C1']))

    ax = plt.subplot(5, 1, 5)
    # ret_max_data = sorted(ret_up_list[1], key=lambda x: x["etime_dict"]['M2_S2_C1'], reverse=True)[0]
    ret_max_data = ret_up_list[3][0]
    Makespan_pic.show_dag_and_makespan(ret_max_data["core_data_list"], Total_Time, ax, font_size=8)
    ax.set_ylabel('MINE_Prio Scheduling\n', fontdict={'family': 'Times New Roman', 'size': 10})
    print("MINE_M1_S2_C1 Etime = {0}".format(ret_max_data['etime_dict']['M1_S2_C1']))
    print("MINE_M2_S2_C1 Etime = {0}".format(ret_max_data['etime_dict']['M2_S2_C1']))

    print("workload = {0}".format( round( 100 * ret_max_data['workload']/(core_number * Total_Time) ) ))

    plt.show()
