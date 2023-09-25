import seaborn as sns
# import matplotlib.pyplot as mp
import pandas as pd
from itertools import combinations

# importing the necessary libraries
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

# 散点图

root_addr = "./7-23-time.csv"
df = pd.read_csv(root_addr)

plt.style.use('_mpl-gallery')

x = df['number_of_nodes']
y = df['number_of_edges']
z1 = df['type1']
z2 = df['type1']
z3 = df['type3']
zp = df['priotime']
# generating  random dataset
# z1 = np.random.randint(80, size=(55))
# x1 = np.random.randint(60, size=(55))
# y1 = np.random.randint(64, size=(55))

# z2 = np.random.randint(80, size=(55))
# x2 = np.random.randint(60, size=(55))
# y2 = np.random.randint(64, size=(55))

# Creating figures for the plot
#
# """
fig = plt.figure(figsize=(10, 7))
ax = plt.axes(projection="3d")
# Creating a plot using the random datasets
# ax.scatter3D(x, y, z1, color="red")
ax.scatter3D(x, y, z2, color="blue")
ax.scatter3D(x, y, z3, color="green")
ax.scatter3D(x, y, zp, color="black")
# """

fig, ax = plt.subplots()
# ax.scatter(x, z1, s=12, c='red')
# ax.scatter(x, z2, s=36, c='blue')
ax.scatter(x, z3, s=36, c='green')
# ax.scatter(x, zp, s=36, c='black')
# ax.scatter(y, z2, s=24, c='blue')
# ax.scatter(y, z3, s=24, c='green')
# ax.scatter(y, zp, s=24, c='black')
# ax.scatter(x, z1, s=12, c='red', vmin=0, vmax=100)
# ax.scatter(x, z1, s=12, c='red', vmin=0, vmax=100)

# ax.set(xlim=(0, 8), xticks=np.arange(1, 8), ylim=(0, 8), yticks=np.arange(1, 8))

plt.title("3D scatter plot")

# display the  plot
plt.show()

