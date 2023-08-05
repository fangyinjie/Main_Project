import numpy as np


def DAG_Generator(Source_Matrix, Node_Num):
    ret = []
    # 如果没有可分配结点了，就把所有没有前驱的连接到头结点，没有后继的连接到尾结点
    return ret


if __name__ == "__main__":
    # assert  n <= 2
    for Node_Num in range(1, 7):
        Source_Matrix = np.array([[0]])
        All_DAG_list = DAG_Generator(Source_Matrix, Node_Num)