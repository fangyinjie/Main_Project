import matplotlib.pyplot as plt # plt 用于显示图片
import matplotlib.image as mpimg # mpimg 用于读取图片
import graphviz # 创建树对象
mygraph = graphviz.Digraph(node_attr={'shape': 'box'}, edge_attr={'labeldistance': "10.5"}, format="png")
# 构建节点
mygraph.node("0", "Has feathers?")
mygraph.node("1", "Can fly?")
mygraph.node("2", "Has fins?")
mygraph.node("3", "Hawk")
mygraph.node("4", "Penguin")
mygraph.node("5", "Dolphin")
mygraph.node("6", "Bear")
# 构建边
mygraph.edge("0", "1", label="True")
mygraph.edge("0", "2", label="False")
mygraph.edge("1", "3", label="True")
mygraph.edge("1", "4", label="False")
mygraph.edge("2", "5", label="True")
mygraph.edge("2", "6", label="False")
# 渲染
mygraph.render("decisionTree")  # 图形显示
ax = plt.gca()      # 获取图形坐标轴
ax.set_axis_off()   # 去掉坐标
decisionTree = mpimg.imread('decisionTree.png') # 读取和代码处于同一目录下的 lena.png
ax.imshow(decisionTree)   # 读取生成的图片

plt.show()