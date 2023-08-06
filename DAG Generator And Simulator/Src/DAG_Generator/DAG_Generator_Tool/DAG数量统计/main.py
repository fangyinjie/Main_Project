# This is a sample Python script.
# 一种随机生成图的方法
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import networkx as nx
import matplotlib.pyplot as plt
import math

ER = nx.random_graphs.erdos_renyi_graph(100,0.03)
pos = nx.spring_layout(ER)
nx.draw(ER, pos, with_labels=False, node_size=30)
plt.show()

"""
ER = nx.random_graphs.erdos_renyi_graph(100000, 0.00015)
degree = nx.degree_histogram(ER)
print(degree)
x = range(len(degree))
y = [z / float(sum(degree)) for z in degree]
k = range(30)
pk = [(15**i)*(math.exp(-15))/math.factorial(i) for i in k]  # ** 代表乘方
plt.plot(k, pk, color="red", linewidth=0.6)
plt.scatter(x, y, color="blue", alpha=0.4, s=25)
plt.xlabel('k')
plt.ylabel('p(k)')
plt.xlim(0, 35)
plt.ylim(0, 0.12)
plt.show()
"""

