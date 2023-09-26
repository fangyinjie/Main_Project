from z3 import z3
from z3 import *
from z3.z3 import sat
import time
import itertools

"""
# 定义整数变量x和y
x, y = z3.Ints('x y')

# 构造存在量词表达式
exists_expr = z3.Exists([x, y], z3.And(x > 0, y > 0))

s = z3.Solver()
s.add(exists_expr)
s.add(y > 10)
if s.check() == sat:
    print(s.model().eval(y))
    # print(s.model().eval(y).as_long())
    # print(s.model().eval(f(2, 10)))


else:
    print("No solution found")

# 打印存在量词表达式
print(exists_expr)

"""

# for NUM in range(3, 32):
NUM = 0 # 12
total_list = list(range(NUM))
ret = []
stime = time.time()
for n in range(NUM):
    ret = list(itertools.combinations(total_list,n+1))

    print(f'num:{n}__length:{len(ret)}__list{ret}')
etime = time.time()
print(f'{NUM}, time:{etime - stime}')
# print(ret)
# print(ret)

for y in range(10):
    for x in range(10):
        if x == 5:
            break
    print(f'y={y}')