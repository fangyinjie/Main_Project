import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import math

matplotlib.rcParams['font.family']='YouYuan'
# matplotlib.rcParams['font.size']=20
x = np.arange(-1000, 1000, 1)

y0 = [1 for _ in range(len(x))]            # O(1) — 常数复杂度
y_lgx = np.log10(x)                        # O(log n) — 对数复杂度
y_ln = 1 + np.log(x)                            # O(log n) — 对数复杂度
y1 = x                                      # O(n) — 线性复杂度

# y_xlogx = x * math.log(x)                   # O(n log n) — 对数线性复杂度
y2 = x ** 2                                 # O(nᵏ) — 多项式复杂度
# yk = pow(2, x)                                # O(kⁿ) — 指数复杂度

# O(n!) — 阶乘复杂度

# y3 = ln(1+x)
plt.plot(x, y0,     'c--')  #
plt.plot(x, y_lgx,  'r--')  #
plt.plot(x, y_ln,    'g--')  #
plt.plot(x, y1,      'b--')  #

# plt.plot(x, y_xlogx, 'd--')  #
plt.plot(x, y2,      'y--')  #
# plt.plot(x, yk,      'h--')  #

ax = plt.gca()
ax.spines['bottom'].set_position(('data', 0))
ax.spines['top'].set_color('none')
ax.spines['left'].set_position(('data', 0))
ax.spines['right'].set_color('none')


plt.grid()
plt.xlabel('横轴：x', color='green')
plt.ylabel('纵轴：y=x^2', color='red')
plt.axis([0, 10, 0, 10])
plt.show()
