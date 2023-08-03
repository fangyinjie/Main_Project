# from dag import *
# from union_set import *
import random
import json
from copy import deepcopy
import networkx as nx
from typing import Optional, Set, List, Dict, Any
from graphviz import Digraph
# from itertools import combinations
# import itertools


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

    def longest_paths(self, src='S'):
        self.transform_add_source()
        self.transform_add_sink()

        longest_length = 0
        paths = []
        path = []
        # depth-first search
        for length, curr_path in self.get_longest_path_iter(src, path, 0):
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

    def longest_path_length(self, src):
        return sum([self.nodes[node]['WCET'] for node in self.longest_paths(src=src)[0]])

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

    def mark_dom(self):
        for node in self.nodes:
            if len(list(self.successors(node))) > 1:
                self.nodes[node]['is_dominate'] = 1
            else:
                self.nodes[node]['is_dominate'] = 0

    def transform_add_source(self):
        if 'S' in list(self.nodes):
            return
        self.add_node('S', WCET=0, group=0, is_dominate=0)
        for node in self.sources:
            if node != 'S' and node != 'E':
                self.add_edge('S', node)

    def transform_delete_source(self):
        for node in self.sources:
            self.remove_node(node)

    def transform_add_sink(self):
        if 'E' in list(self.nodes):
            return
        self.add_node('E', WCET=0, group=7, is_dominate=0)
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


class UnionSet:
    def __init__(self, items: List, dag: DAG, groups: Dict[Any, Set]):
        self.sets = [[item] for item in items]
        self.dag = dag

    # abs(ave_weight(set_x), ave_weight(set_y))
    def get_distance(self, set_x, set_y):
        if set_x == set_y:
            return None
        # print(set_x, set_y)
        position_x = sum([self.dag.longest_path_length(src=s) for s in set_x]) / len(set_x)
        position_y = sum([self.dag.longest_path_length(src=s) for s in set_y]) / len(set_y)
        distance = abs(position_x - position_y)
        return distance

    def merge(self, item_x, item_y):
        if self.is_connected(item_x, item_y):
            return
        s_x = self.find(item_x)
        s_y = self.find(item_y)
        new_s = s_x + s_y
        self.sets.remove(s_x)
        self.sets.remove(s_y)
        self.sets.append(new_s)

    def is_connected(self, item_x, item_y):
        s_x = self.find(item_x)
        s_y = self.find(item_y)
        if s_x == s_y:
            return True
        return False

    def find(self, item):
        for s in self.sets:
            if item in s:
                return s
        return None

    # set的平均优先级
    def ave_set_prior(self, set: list):
        priors = [self.dag.nodes[node]['prior'] for node in set]
        return sum(priors) / len(priors)

    # 按照原有优先级平均值从高到低排序
    def sort_by_prior(self):
        self.sets.sort(key=lambda set: self.ave_set_prior(set))

    def __len__(self):
        return len(self.sets)


def limited_prior_merge(d: DAG, priority_queue_num: int):
    # 得到分组
    cnode_list = d.longest_paths()[0]  # critical path
    n_set = set(d.nodes)
    groups = dict()
    for cnt in range(len(cnode_list) - 1):
        node_l = cnode_list[cnt]
        node_r = cnode_list[cnt + 1]
        group = (d.get_ancestor(node_r) & n_set).union({node_l})
        n_set = n_set - group
        groups.update({node_l: group})
    groups.update({cnode_list[-1]: n_set})

    # 分配原有优先级
    prior = 0
    for cnode in cnode_list:
        group = list(groups[cnode])
        group.sort(key=lambda node: (d.longest_path_length(src=node),
                                     d.nodes[node]['WCET'], node in cnode_list,
                                     node),
                   reverse=True)
        for node in group:
            d.nodes[node].update({'prior': prior})
            prior += 1

    # Step 1: 每个结点设为一个集合
    us = UnionSet(list(d.nodes), d, groups)
    if len(us) <= priority_queue_num:
        return us

    # 若node_x有且仅有node_y这一后继，且node_y有且仅有node_x这一前驱，则合并
    for node_x in d.nodes:
        if len(list(d.successors(node_x))) != 1:  # 若node_x有且仅有node_y这一后继
            continue

        node_y = d.successors(node_x).__next__()
        if len(list(d.predecessors(node_y))) == 1:  # node_y有且仅有node_x这一前驱
            us.merge(node_x, node_y)

            if len(us) <= priority_queue_num:
                return us

    # Step 2: 合并结点权重相同且WCET相同的集合
    for node_x in d.nodes:
        for node_y in d.nodes:
            weight_x = d.longest_path_length(node_x)
            weight_y = d.longest_path_length(node_y)
            wcet_x = d.nodes[node_x]['WCET']
            wcet_y = d.nodes[node_y]['WCET']
            if weight_x == weight_y and wcet_x == wcet_y:
                us.merge(node_x, node_y)
            if len(us) <= priority_queue_num:
                return us

    # Step 3: 支配结点组最高优先级集合与前驱结点组最低优先级集合合并
    for dom_node in [node for node in d.nodes if d.nodes[node]['is_dominate']]:
        # 找到前驱节点中优先级最高的
        maxi = -1
        maxi_pred_node = None
        for pred_node in d.predecessors(dom_node):
            prior = d.nodes[pred_node]['prior']
            if prior > maxi:
                maxi = prior
                maxi_pred_node = pred_node
        us.merge(maxi_pred_node, dom_node)
        if len(us) <= priority_queue_num:
            return us

    # Step 4: 同组集合中的结点权重相同则合并
    for group in groups.values():
        for node_x in group:
            for node_y in group:
                weight_x = d.longest_path_length(node_x)
                weight_y = d.longest_path_length(node_y)
                wcet_x = d.nodes[node_x]['WCET']
                wcet_y = d.nodes[node_y]['WCET']
                if weight_x == weight_y and wcet_x == wcet_y:
                    us.merge(node_x, node_y)
                    if len(us) <= priority_queue_num:
                        return us

    # Step 5: 同组集合平均WCET之差的绝对值最小则合并
    while True:
        min_pair = None
        min_distance = 10000000
        for group in groups.values():
            for node_x in group:
                for node_y in group:
                    set_x = us.find(node_x)
                    set_y = us.find(node_y)
                    distance = us.get_distance(set_x, set_y)
                    if distance is None:
                        continue
                    if distance < min_distance:
                        min_distance = distance
                        min_pair = (node_x, node_y)
        if min_pair is None:
            break
        us.merge(min_pair[0], min_pair[1])
        if len(us) <= priority_queue_num:
            return us

    # Step 6: 支配结点平均执行时间相对前驱结点平均执行执行时间最长的集合与下一集合合并
    is_merged = {dom_node: False for dom_node in d.nodes if d.nodes[dom_node]['is_dominate']}

    while False in is_merged.values():
        maxi_ratio_dom_node = None
        maxi_ratio = 0

        for dom_node in [dom_node for dom_node in is_merged.keys() if not is_merged[dom_node]]:
            pred_WCETs = [d.nodes[pred_node]['WCET'] for pred_node in d.predecessors(dom_node)]
            if pred_WCETs == [] or pred_WCETs == [0]:
                continue
            ave_pred_WCETs = sum(pred_WCETs) / len(pred_WCETs)
            ratio = d.nodes[dom_node]['WCET'] / ave_pred_WCETs

            if ratio > maxi_ratio:
                maxi_ratio_dom_node = dom_node
                maxi_ratio = ratio

        if maxi_ratio_dom_node is None:
            maxi_ratio_dom_node = random.choice([dom_node for dom_node in is_merged.keys() if not is_merged[dom_node]])

        # 找到后继节点中优先级最高的集合合并
        maxi_prior = 100000
        maxi_prior_succ_node = None
        for succ_node in d.successors(maxi_ratio_dom_node):
            succ_prior = d.nodes[succ_node]['prior']
            if succ_prior < maxi_prior:
                maxi_prior = succ_prior
                maxi_prior_succ_node = succ_node
        us.merge(maxi_ratio_dom_node, maxi_prior_succ_node)
        is_merged.update({maxi_ratio_dom_node: True})
        if len(us) <= priority_queue_num:
            return us

    # Step 7: 合并临近集合,选取合并后各集合中最大跨组数最小的合并方案
    dom_nodes = [dom_node for dom_node in d.nodes if d.nodes[dom_node]['is_dominate']]

    while len(us) > priority_queue_num:
        us.sort_by_prior()
        min_cross_count_sum = None
        for cnt in range(len(us.sets) - 1):
            set_l = us.sets[cnt]
            set_r = us.sets[cnt + 1]
            cross_count_l = len([node for node in set_l if node in dom_nodes])
            cross_count_r = len([node for node in set_r if node in dom_nodes])
            if min_cross_count_sum is None or cross_count_l + cross_count_r < min_cross_count_sum:
                min_cross_count_sum = cross_count_l + cross_count_r
                min_cross_count_sum_pair = (set_l, set_r)
        us.merge(min_cross_count_sum_pair[0][0], min_cross_count_sum_pair[1][0])

    return us


# Step 8
def limited_prior_assign(d: DAG, priority_queue_num: int):
    us = limited_prior_merge(d, priority_queue_num)

    cnode_list = d.longest_paths()[0]  # critical path
    n_set = set(d.nodes)
    groups = dict()
    for cnt in range(len(cnode_list) - 1):
        node_l = cnode_list[cnt]
        node_r = cnode_list[cnt + 1]
        group = (d.get_ancestor(node_r) & n_set).union({node_l})
        n_set = n_set - group
        groups.update({node_l: group})
    groups.update({cnode_list[-1]: n_set})

    # 按照原有优先级分配压缩后优先级
    prior_val = 0
    for cnode in cnode_list:
        group = list(groups[cnode])
        group.sort(key=lambda node: (d.longest_path_length(src=node),
                                     d.nodes[node]['WCET'], node in cnode_list,
                                     node),
                   reverse=True)
        for node in group:
            if d.nodes[node].get('limited_prior') is None:
                s = us.find(node)
                for node_assigned in s:
                    d.nodes[node_assigned].update({'limited_prior': prior_val})
                prior_val += 1

    d.transform_delete_source()
    d.transform_delete_sink()


def init_dag(nodes, edges, WCETs):
    dag = DAG()

    for node, WCET in zip(nodes, WCETs):
        dag.add_node(node, WCET=WCET)
    for start, end in edges:
        dag.add_edge(start, end)
    dag.mark_dom()

    return dag


def priority_Press_config(dag_obj, prior_num):
    # 初始化DAG
    d = init_dag(dag_obj.nodes(), dag_obj.edges(), [node_x[1]['WCET'] for node_x in dag_obj.nodes(data=True)])

    # 优先级分配，prior_num为给定的优先级数量
    limited_prior_assign(d, prior_num)

    # 输出结果
    # print(f"{prior_num}优先级")
    # print('结点名称', '\t', '优先级')
    # for node in d.nodes:
    #     d.nodes[node].update({'prior': d.nodes[node]['limited_prior']})
    #     print(node, '\t\t', d.nodes[node]['limited_prior'])
    for node_x in dag_obj.nodes(data=True):
        node_x[1]['Group_{0}'.format(prior_num)] = d.nodes[node_x[0]]['limited_prior']
        node_x[1]['Prio'] = d.nodes[node_x[0]]['limited_prior']


if __name__ == "__main__":
    G = nx.DiGraph()
    G.add_node(0, Node_Index=0, Node_ID='0', Succ_Nodes=[1], BCET=1, ACET=1, WCET=1, rank=1, Group=1)
    G.add_node(1, Node_Index=1, Node_ID='1', Succ_Nodes=[2, 3, 4, 5, 6, 7, 8], BCET=1, ACET=1, WCET=1, rank=1, Group=1)
    G.add_node(2, Node_Index=2, Node_ID='2', Succ_Nodes=[9], BCET=1, ACET=1, WCET=1, rank=1, Group=1)
    G.add_node(3, Node_Index=3, Node_ID='3', Succ_Nodes=[9], BCET=1, ACET=1, WCET=1, rank=1, Group=1)
    G.add_node(4, Node_Index=4, Node_ID='4', Succ_Nodes=[9], BCET=1, ACET=1, WCET=1, rank=1, Group=1)
    G.add_node(5, Node_Index=5, Node_ID='5', Succ_Nodes=[9], BCET=1, ACET=1, WCET=1, rank=1, Group=1)
    G.add_node(6, Node_Index=6, Node_ID='6', Succ_Nodes=[9], BCET=1, ACET=1, WCET=1, rank=1, Group=1)
    G.add_node(7, Node_Index=7, Node_ID='7', Succ_Nodes=[9], BCET=1, ACET=1, WCET=1, rank=1, Group=1)
    G.add_node(8, Node_Index=8, Node_ID='8', Succ_Nodes=[9], BCET=1, ACET=1, WCET=1, rank=1, Group=1)
    G.add_node(9, Node_Index=9, Node_ID='9', Succ_Nodes=[],  BCET=1, ACET=1, WCET=1, rank=1, Group=1)
    G.add_edges_from([(0, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
                      (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9)])
    G.graph['DAG_ID'] = 'test'
    G.graph['Nodes_Number'] = 'test'

    priority_Press_config(G, 3)
