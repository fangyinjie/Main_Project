import datetime
from typing import List, Tuple
import networkx as nx

import json
from copy import deepcopy

from typing import Optional, Set
from graphviz import Digraph

from . import Core


class DAG(nx.DiGraph):
    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)
        self.dag_name = None

    @property
    def paths(self, start='S'):
        self.transform_add_source()
        self.transform_add_sink()
        path = []
        return list(self.get_path_iter(start, path))

    def get_path_iter(self, vertex, path):
        path.append(vertex)
        if vertex == 'E':
            yield deepcopy(path)
            path.remove('E')
            return
        for nxt in nx.neighbors(self, vertex):
            for result in self.get_path_iter(nxt, path):
                yield result
        path.remove(vertex)

    def path_length(self, path):
        length = 0
        for vertex in path:
            length += self.nodes[vertex]['WCET']
        return length

    @property
    def longest_paths(self):
        self.transform_add_source()
        self.transform_add_sink()

        longest_length = 0
        paths = []
        path = []
        # depth-first search
        for length, curr_path in self.get_longest_path_iter('S', path, 0):
            if length > longest_length:
                paths = [curr_path]
                longest_length = length
            elif length == longest_length:
                paths.append(curr_path)
        return paths

    def get_longest_path_iter(self, vertex, path, length):
        path.append(vertex)
        length += self.nodes[vertex]['WCET']
        if vertex == 'E':
            yield length, deepcopy(path)
            path.remove('E')
            return
        for nxt in nx.neighbors(self, vertex):
            for result in self.get_longest_path_iter(nxt, path, length):
                yield result

        path.remove(vertex)
        length -= self.nodes[vertex]['WCET']

    @property
    def longest_path_length(self):
        return len(self.longest_paths[0])

    @property
    def anti_chains(self):
        d = nx.DiGraph(self)
        return list(nx.antichains(d))

    @property
    def longest_anti_chain(self):
        anti_chains = self.anti_chains
        return [anti_chain for anti_chain in anti_chains if len(anti_chain) == self.longest_anti_chain_length]

    @property
    def longest_anti_chain_length(self):
        return max(len(anti_chain) for anti_chain in self.anti_chains)

    @property
    def sources(self):
        sources = []
        for node, in_degree in self.in_degree:
            if in_degree == 0:
                sources.append(node)
        return sources

    @property
    def sinks(self):
        sinks = []
        for node, in_degree in self.out_degree:
            if in_degree == 0:
                sinks.append(node)
        return sinks

    @property
    def max_in_degree(self):
        max_in_degree = 0
        for vertex, in_degree in self.in_degree:
            if in_degree > max_in_degree:
                max_in_degree = in_degree
        return max_in_degree

    @property
    def min_in_degree(self):
        min_in_degree = float('inf')
        for vertex, in_degree in self.in_degree:
            if in_degree < min_in_degree:
                min_in_degree = in_degree
        return min_in_degree

    @property
    def ave_in_degree(self):
        total = 0
        for vertex, in_degree in self.in_degree:
            total += in_degree
        return total / len(self)

    @property
    def max_out_degree(self):
        max_out_degree = 0
        for vertex, out_degree in self.out_degree:
            if out_degree > max_out_degree:
                max_out_degree = out_degree
        return max_out_degree

    @property
    def min_out_degree(self):
        min_out_degree = float('inf')
        for vertex, out_degree in self.out_degree:
            if out_degree < min_out_degree:
                min_out_degree = out_degree
        return min_out_degree

    @property
    def ave_out_degree(self):
        total = 0
        for vertex, out_degree in self.out_degree:
            total += out_degree
        return total / len(self)

    def get_in_degree(self, vertex):
        for v, in_degree in self.in_degree:
            if vertex ==  v:
                return in_degree

    def get_out_degree(self, vertex):
        for v, out_degree in self.out_degree:
            if vertex == v:
                return out_degree

    def get_ancestor(self, vertex) -> Set:
        return nx.ancestors(self, vertex)

    def get_descendant(self, vertex) -> Set:
        return nx.descendants(self, vertex)

    def get_parallel(self, vertex) -> Set:
        return set(self.nodes) - self.get_descendant(vertex) - self.get_ancestor(vertex) - {vertex}

    def transform_add_source(self):
        if 'S' in list(self.nodes):
            return
        self.add_node('S', WCET=0)
        for node in self.sources:
            if node != 'S' and node != 'E':
                self.add_edge('S', node)

    def transform_delete_source(self):
        for node in self.sources:
            self.remove_node(node)

    def transform_add_sink(self):
        if 'E' in list(self.nodes):
            return
        self.add_node('E', WCET=0)
        for node in self.sinks:
            if node != 'S' and node != 'E':
                self.add_edge(node, 'E')

    def transform_delete_sink(self):
        for node in self.sinks:
            self.remove_node(node)

    def draw(self, dir_path: Optional[str] = 'Graph/', format: Optional[str] = 'png'):
        g_graph = Digraph()

        # add vertex
        for vertex in self.nodes:
            if vertex == 'S':
                color = 'green'
            elif vertex == 'E':
                color = 'red'
            else:
                color = 'black'
            g_graph.node(name=str(vertex), color=color)

        # add edge
        for (start, end), _ in self.edges.items():
            g_graph.edge(str(start), str(end))

        g_graph.render(dir_path + self.dag_name, view=False, format=format)

    def networkx_export(self, dir_path: Optional[str] = 'Graph/'):
        data = nx.node_link_data(self)
        with open(dir_path + self.dag_name + '.json', 'w') as obj:
            json.dump(data, obj)


def get_optimal_scheduling(WCETs: List, edges: List[Tuple], processor_num: int):
    """ 求解最优调度表 """
    """ 构建DAG """
    d = DAG()
    for node, WCET in enumerate(WCETs):
        d.add_node(node + 1, WCET=WCET)
    d.transform_add_source()
    d.transform_add_sink()

    d.add_edges_from(edges)

    """ 变量设置 """
    # 对每个节点设置一个变量，变量的值为该节点开始的时间
    s_dict = {node: Int(f'start_{node}') for node in d.nodes}

    # 处理器分配设置
    p_dict = {node: Int(f'assign_{node}') for node in d.nodes}

    # m, n, u, v, x对应的0-1变量
    para_pairs = list()
    for node_i in d.nodes:
        for node_j in d.get_parallel(node_i):
            if (node_i, node_j) not in para_pairs and (node_j, node_i) not in para_pairs:
                para_pairs.append((node_i, node_j))

    m_dict = {pair: Int(f'm_{pair[0]}_{pair[1]}') for pair in para_pairs}
    n_dict = {pair: Int(f'n_{pair[0]}_{pair[1]}') for pair in para_pairs}
    u_dict = {pair: Int(f'u_{pair[0]}_{pair[1]}') for pair in para_pairs}
    v_dict = {pair: Int(f'v_{pair[0]}_{pair[1]}') for pair in para_pairs}
    x_dict = {pair: Int(f'x_{pair[0]}_{pair[1]}') for pair in para_pairs}

    """ 建模 """
    # 初始化求解器
    o = Optimize()

    # 0-1变量约束
    for var_dict in [m_dict, n_dict, u_dict, v_dict, x_dict]:
        for var in var_dict.values():
            o.add(var <= 1)
            o.add(var >= 0)

    for m, n, x in zip(m_dict.values(), n_dict.values(), x_dict.values()):
        o.add(m + n + x == 2)

    for u, v, x in zip(u_dict.values(), v_dict.values(), x_dict.values()):
        o.add(u + v + x == 1)

    # 开始时间约束
    o.add(s_dict['S'] == 0)

    # 前驱约束
    for succ in d.nodes:
        for pred in nx.DiGraph.predecessors(d, succ):
            s_pred = s_dict[pred]
            e_pred = d.nodes[pred]['WCET']
            s_succ = s_dict[succ]
            o.add(s_pred + e_pred <= s_succ)

    # 单个处理器同时只能处理一个节点 && 节点之间不overlap
    for node_i, node_j in para_pairs:
        s_i = s_dict[node_i]
        s_j = s_dict[node_j]
        p_i = p_dict[node_i]
        p_j = p_dict[node_j]
        x_ij = x_dict[(node_i, node_j)]
        m_ij = m_dict[(node_i, node_j)]
        n_ij = n_dict[(node_i, node_j)]
        u_ij = u_dict[(node_i, node_j)]
        v_ij = v_dict[(node_i, node_j)]
        e_i = d.nodes[node_i]['WCET']
        e_j = d.nodes[node_j]['WCET']
        M = 99999999999

        # o.add(Implies(p_i == p_j, Or(s_j >= s_i + exe_time_i, s_i >= s_j + exe_time_j)))
        o.add(p_i >= p_j - M * x_ij)
        o.add(p_j >= p_i - M * x_ij)
        o.add(p_i > p_j - M * m_ij)
        o.add(p_j > p_i - M * n_ij)

        o.add(s_i >= s_j + e_j - M * (1 - u_ij))
        o.add(s_j >= s_i + e_i - M * (1 - v_ij))

    # 节点能且只能分配到一个处理器上
    for p in p_dict.values():
        o.add(p >= 0)
        o.add(p < processor_num)

    # 目标函数
    o.minimize(s_dict['E'])

    """ 求解最优调度 """
    # 求解
    starttime = datetime.datetime.now()

    o.check()
    result = o.model()

    endtime = datetime.datetime.now()
    spend = (endtime - starttime).seconds

    make_span = result[s_dict['E']].as_long()

    # 输出运行信息
    start = {node: result[var] for node, var in s_dict.items()}
    p = {node: result[var] for node, var in p_dict.items()}

    # print(f'求解时间：{spend}，make_span：{make_span}')
    return [(start[node].as_long(), simplify(start[node] + d.nodes[node]['WCET']).as_long(), p[node].as_long(), node) for node in d.nodes]
    # for node in d.nodes:
    #     print(start[node], simplify(start[node] + d.nodes[node]['WCET']), p[node])


# 本算法只适用于单DAG
def Dispatcher_Workspace(Param_List):
    temp_dag = Param_List[0]
    core_num = Param_List[1]['Core_Num']
    minc = 1 - min(temp_dag.nodes())
    edges_list = [(edge_x + minc, edge_y + minc) for (edge_x, edge_y) in temp_dag.edges()]
    ret_ddd_list = get_optimal_scheduling(
        WCETs=[node_x[1]['WCET'] for node_x in temp_dag.nodes(data=True)],
        edges=edges_list,
        processor_num=core_num)
    Core_Data_List = [Core.Core_Obj(i) for i in range(core_num)]

    ret_ddd_list = list(sorted(ret_ddd_list, key=lambda x: x[0]))
    for ddd_x in ret_ddd_list:
        if isinstance(ddd_x[3], int):
            Core_Data_List[ddd_x[2]].Insert_Task_Info(
                dag_ID=temp_dag.graph['DAG_ID'], dag_NUM=0,
                node=[ddd_x[3] - minc, temp_dag.nodes[ddd_x[3] - minc]],
                start_time=ddd_x[0], end_time=ddd_x[1])  # data save

    return Core_Data_List
