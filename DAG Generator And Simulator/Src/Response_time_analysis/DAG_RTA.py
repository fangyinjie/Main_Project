import networkx as nx
from typing import List     #, Optional, Set, Union

#####################################
# Response time analysis arithmetic #
#####################################

# Single DAG
def Single_DAG_Response_Time_Analysis(RTA_Type: str, DAGx:nx.DiGraph, Core_Num: int):
    if RTA_Type == "non-preemptive":
        return __rta_basics_np_single(DAGx, Core_Num)
    elif RTA_Type == "preemptive":
        return __rta_basics_p_single(DAGx, Core_Num)
    elif RTA_Type == "Serrano2016":
        return __rta_basics_Serrano2016_single(DAGx, Core_Num)
    elif RTA_Type == "He2021":
        return __rta_basics_He2021_single(DAGx, Core_Num)
    elif RTA_Type == "Zhao2022":
        return __rta_basics_Zhao2022_single(DAGx, Core_Num)
    elif RTA_Type == "Chen2023":
        return __rta_basics_Chen2023_single(DAGx, Core_Num)
    else:
        print("RTA_Type input error!")

def __rta_basics_np_single(DAGx:nx.DiGraph,
                           Core_Num: int):
    return False

def __rta_basics_p_single(DAGx:nx.DiGraph,
                           Core_Num: int):
    return False

def __rta_basics_Serrano2016_single(DAGx:nx.DiGraph,
                                    Core_Num: int):
    return False

def __rta_basics_He2021_single(DAGx:nx.DiGraph,
                               Core_Num: int):
    return False

def __rta_basics_Zhao2022_single(DAGx:nx.DiGraph,
                                 Core_Num: int):
    return False

def __rta_basics_Chen2023_single(DAGx:nx.DiGraph,
                                 Core_Num: int):
    return False



# Multiple DAG
def Multiple_DAG_Response_Time_Analysis(RTA_Type: str, DAG_list: List[nx.DiGraph], Core_Num: int):
    if RTA_Type == "non-preemptive":
        return __rta_basics_np_multiple(DAG_list, Core_Num)
    elif RTA_Type == "preemptive":
        return __rta_basics_p_multiple(DAG_list, Core_Num)
    elif RTA_Type == "Serrano2016":
        return __rta_basics_Serrano2016_multiple(DAG_list, Core_Num)
    elif RTA_Type == "He2021":
        return __rta_basics_He2021_multiple(DAG_list, Core_Num)
    elif RTA_Type == "Zhao2022":
        return __rta_basics_Zhao2022_multiple(DAG_list, Core_Num)
    elif RTA_Type == "Chen2023":
        return __rta_basics_Chen2023_multiple(DAG_list, Core_Num)
    else:
        print("RTA_Type input error!")


def __rta_basics_np_multiple(DAG_list: List[nx.DiGraph],
                             Core_Num: int):
    return False

def __rta_basics_p_multiple(DAG_list: List[nx.DiGraph],
                            Core_Num: int):
    return False

def __rta_basics_Serrano2016_multiple(DAG_list: List[nx.DiGraph],
                                      Core_Num: int):
    return False

def __rta_basics_He2021_multiple(DAG_list: List[nx.DiGraph],
                                 Core_Num: int):
    return False

def __rta_basics_Zhao2022_multiple(DAG_list: List[nx.DiGraph],
                                   Core_Num: int):
    return False

def __rta_basics_Chen2023_multiple(DAG_list: List[nx.DiGraph],
                                   Core_Num: int):
    return False


"""
def rta_basics_non_preemptive(self, core_num):
    node_list = list(self.G.nodes())
    paths = list(nx.all_simple_paths(self.G, node_list[0], node_list[-1]))

    interference_node_list = []
    ret_path_and_rta = [0, 0, 0, [], []]
    for x in paths:
        temp_interference_node_list = []
        temp_path_weight = 0
        for y in x:
            temp_all_node = self.G.nodes(data=True)
            temp_ance = list(nx.ancestors(self.G, y))
            temp_desc = list(nx.descendants(self.G, y))
            temp_self = x
            sub_node = self.G.nodes[y]
            for z in temp_all_node:
                if (z[0] not in temp_ance) and (z[0] not in temp_desc) and (z[0] not in temp_self):  # 判断z是否是干扰节点
                    if z[1]['priority'] < sub_node.get('priority'):  # 判断此z的优先级是否大于y
                        if z not in temp_interference_node_list:  # 判断此z是否已经加入
                            temp_interference_node_list.append(z)
            temp_path_weight += sub_node.get('WCET')
            # 每个节点的非前驱和非后继节点
        temp_inter_weight = 0
        for y in temp_interference_node_list:
            temp_inter_weight += y[1]['WCET']
        interference_node_list.append(temp_interference_node_list)
        temp_rta = temp_path_weight + temp_inter_weight / core_num
        # 计算此路径的RTA
        # ret_path_and_rta.append((temp_rta, temp_path_weight, temp_inter_weight, x, temp_interference_node_list))
        if temp_rta > ret_path_and_rta[0]:
            ret_path_and_rta[0] = temp_rta
            ret_path_and_rta[1] = temp_path_weight
            ret_path_and_rta[2] = temp_inter_weight
            ret_path_and_rta[3] = x
            ret_path_and_rta[4] = temp_interference_node_list
    return math.ceil(ret_path_and_rta[0])


def rta_basics_preemptive(self, core_num):
    node_list = list(self.G.nodes())
    paths = list(nx.all_simple_paths(self.G, node_list[0], node_list[-1]))

    interference_node_list = []
    ret_path_and_rta = [0, 0, 0, [], []]
    for x in paths:
        temp_interference_node_list = []
        reserve_node_list = {}
        temp_path_weight = 0
        temp_WCET = []
        for y in x:
            temp_all_node = self.G.nodes(data=True)
            temp_ance = list(nx.ancestors(self.G, y))
            temp_desc = list(nx.descendants(self.G, y))
            temp_self = x
            sub_node = self.G.nodes[y]
            temp_path_weight += sub_node.get('WCET')
            temp_WCET.append(sub_node.get('WCET'))
            for z in temp_all_node:
                if (z[0] not in temp_ance) and (z[0] not in temp_desc) and (z[0] not in temp_self):  # 判断z是否是干扰节点
                    if z[1]['priority'] < sub_node.get('priority'):  # 判断此z的优先级是否大于y
                        if z not in temp_interference_node_list:  # 判断此z是否已经加入
                            temp_interference_node_list.append(z)
                    else:
                        reserve_node_list[z[0]] = z[1]['WCET']
        t_reserve_list = sorted(reserve_node_list.items(), key=lambda x: x[1])
        add_reserve = 0
        for y in range(0, min(core_num, len(t_reserve_list))):
            add_reserve += t_reserve_list[y][1]
        temp_inter_weight = 0
        for y in temp_interference_node_list:
            temp_inter_weight += y[1]['WCET']
        interference_node_list.append(temp_interference_node_list)
        temp_rta = temp_path_weight + (temp_inter_weight + add_reserve) / core_num
        # 计算此路径的RTA
        if temp_rta > ret_path_and_rta[0]:
            ret_path_and_rta[0] = temp_rta
            ret_path_and_rta[1] = temp_path_weight
            ret_path_and_rta[2] = temp_inter_weight
            ret_path_and_rta[3] = x
            ret_path_and_rta[4] = temp_interference_node_list
    return math.ceil(ret_path_and_rta[0])

"""

