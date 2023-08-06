import math
# 1973 R.W. ROBINSON 计算的labeld vertices DAG 的节点 n 的穷举数量

def dag_count(n):
    ret = 0
    if n == 1 or n == 0:
        return 1
    else:
        for k in range(1, n+1):
            ret += pow(-1, (k - 1)) * math.comb(n, k) * pow(2, k * (n - k)) * dag_count(n - k)
        return ret


if __name__ == "__main__":
    for n in range(1, 12 + 1):
        print(n, ":", dag_count(n))