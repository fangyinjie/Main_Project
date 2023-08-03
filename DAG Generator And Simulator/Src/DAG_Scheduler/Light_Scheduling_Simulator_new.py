#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Randomized DAG Generator
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################
import copy
import networkx as nx
from . import Simulation_Result_Show as SRS
from . import Core
# import Simulation_Result_Show as SRS
# import Core
# import Scheduler.Scheduling_Simulator_new_2 as SS


def compute_sch_list(dag_x, core_num):
    Core_list = [Core.Core_Obj(core_id) for core_id in range(core_num)]
    dag_test = copy.deepcopy(dag_x)
    for node_x in dag_test.nodes(data=True):
        node_x[1]['R'] = 0
    while dag_test.number_of_nodes() > 0:
        # (1) 获取当前avail最小的core
        Core_list = sorted(Core_list, key=lambda x: x.Core_ID, reverse=False)
        Core_x = sorted(Core_list, key=lambda x: x.last_finish_time, reverse=False)[0]
        fnode = [node_x for node_x in dag_test.nodes(data=True) if node_x[1]['R'] <= Core_x.last_finish_time
                                                                   and len(list(dag_test.predecessors(node_x[0]))) == 0]
        if len(fnode) > 0:        # (2) 获取avail前或同时就释放的结点，选优先级最高的
            fnode = sorted(fnode, key=lambda x: x[1]['Prio'], reverse=False)  # 优先级排序
            node_x = fnode.pop(0)
        else:                     # (2) 否则选择最早释放的结点，上处理器运行
            rnode = [node_x for node_x in dag_test.nodes(data=True) if len(list(dag_test.predecessors(node_x[0]))) == 0]
            rnode = sorted(rnode, key=lambda x: x[1]['Prio'], reverse=False)    # 优先级排序（同时释放）
            rnode = sorted(rnode, key=lambda x: x[1]['R'], reverse=False)       # 释放时间排序
            node_x = rnode.pop(0)
        # (3) 执行结点时间以及调度表更新；
        AST = max(node_x[1]['R'], Core_x.last_finish_time)
        AFT = AST + node_x[1]['WCET']
        Core_x.Insert_Task_Info(node=node_x[0], start_time=AST, end_time=AFT)
        # (3) 更新所有后继结点的释放时间；
        for dnode in dag_test.successors(node_x[0]):
            dag_test.nodes[dnode]['R'] = max(AFT, dag_test.nodes[dnode]['R'])
        # (3) 删除执行结点
        dag_test.remove_node(node_x[0])
    return Core_list


# for node_x in dag_x.nodes(data=True):
#   (1) 选择核，avail最小的，核号最小的；
#   (2) AST = max{avail, ART(node_x)}
#   (3) 更新核的avail = AST + AET(node_x)
#           和调度列表，加入（node_id, AST,  AFT）
if __name__ == "__main__":
    G = nx.DiGraph()

    G.add_node(1, WCET=4, Prio=8)
    G.add_node(2, WCET=5, Prio=1)
    G.add_node(3, WCET=6, Prio=6)
    G.add_node(4, WCET=7, Prio=5)
    G.add_node(5, WCET=8, Prio=4)
    G.add_node(6, WCET=9, Prio=3)
    G.add_node(7, WCET=10, Prio=2)
    G.add_node(8, WCET=11, Prio=7)

    G.add_edge(1, 8, weight=4)
    G.add_edge(1, 3, weight=4)
    G.add_edge(1, 4, weight=4)
    G.add_edge(8, 5, weight=4)
    G.add_edge(8, 6, weight=4)
    G.add_edge(3, 6, weight=4)
    G.add_edge(4, 7, weight=4)
    G.add_edge(5, 2, weight=4)
    G.add_edge(6, 2, weight=4)
    G.add_edge(7, 2, weight=4)

    core_list = compute_sch_list(G, 3)
    print(G.nodes(data=True))
    print(G.edges(data=True))
    print("_________")
    for core_x in core_list:
        print("_________")
        for node_data in core_x.Core_Running_Task:
            print(node_data)

    SRS.show_core_data_list({'test': {core_x.Core_ID: core_x for core_x in core_list}}, 'Show', '')

    # nx.draw_networkx(G, pos=nx.circular_layout(G), arrows=True, node_size=400, edge_color='r')

    # nx.draw(G, pos=pos, with_labels=True)
    # nx.draw(g_1, pos=nx.spectral_layout(g_1), nodecolor='r', edge_color='b')
    # nx.draw(G, pos=nx.spectral_layout(G), edge_color='r')

    # plt.show()

# 1. 应用经典的图操作，例如：
# subgraph（G，nbunch）                  返回在 nbunch 中的节点上诱导的子图。
# union（G，H[，重命名，名称]）             返回图 G 和 H 的并集。
# disjoint_union(G, H)                  返回图 G 和 H 的不相交并集。
# cartesian_product(G, H)               返回 G 和 H 的笛卡尔积。
# compose(G, H)                         返回由 H 组成的 G 的新图。
# complement（G）                        返回 G 的图补集。
# create_empty_copy(G[, with_data])     返回删除所有边的图 G 的副本。
# to_undirected（图形）                   返回图的无向视图graph。
# to_directed（图形）                     返回图形的有向视图graph。

# 2. 使用对经典小图之一的调用，例如，
# petersen_graph（[创建_使用]）             返回彼得森图。
# tutte_graph（[创建_使用]）                返回 Tutte 图。
# sedgewick_maze_graph（[创建_使用]）       返回一个带循环的小迷宫。
# tetrahedral_graph（[创建_使用]）          返回 3 正则柏拉图四面体图。

# 3. 为经典图使用（建设性）生成器，例如，
# complete_graph(n[, create_using])                 返回K_n具有 n 个节点的完整图。
# complete_bipartite_graph(n1, n2[, create_using])  返回完整的二分图K_{n_1,n_2}。
# barbell_graph(m1, m2[, create_using])             返回杠铃图：通过路径连接的两个完整图。
# lollipop_graph(m, n[, create_using])              返回棒棒糖图；K_m连接到P_n.

# 4. 使用随机图生成器，例如
# erdos_renyi_graph(n, p[, 种子, 定向])                 返回一个随机图，也称为 Erdős-Rényi 图或二项式图。
# watts_strogatz_graph(n, k, p[, 种子])                返回 Watts-Strogatz 小世界图。
# barabasi_albert_graph(n, m[, 种子, ...])             使用 Barabási–Albert 优先附件返回一个随机图
# random_lobster(n, p1, p2[, 种子])                    返回一个随机龙虾图。


# 一个图中的节点可以合并到另一个图中：
# H = nx.path_graph(10)
# G.add_nodes_from(H)
# G现在包含 的节点H作为 的节点G。相反，您可以将图形H用作 中的节点G。
# G.add_node(H)

# K_5 = nx.complete_graph(5)
# K_3_5 = nx.complete_bipartite_graph(3, 5)
# barbell = nx.barbell_graph(10, 10)
# lollipop = nx.lollipop_graph(10, 20)

# er = nx.erdos_renyi_graph(10, 0.1)        # G_{n,p}
# ws = nx.watts_strogatz_graph(30, 3, 0.1)    # Watts–Strogatz small-world graph.
# ba = nx.barabasi_albert_graph(10, 5)
# red = nx.random_lobster(10, 0.9, 0.9)
