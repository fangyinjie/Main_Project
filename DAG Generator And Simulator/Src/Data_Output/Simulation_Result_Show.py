#!/usr/bin/python3
# -*- coding: utf-8 -*-
import copy
################################################################################
# Randomized DAG Generator
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################

import os
import numpy as np
# import matplotlib.pylab as plt  # 绘制图形
import matplotlib.pyplot as plt
from ..DAG_Scheduler import Core as Core

color_list = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c',
              '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928']
flow_color_dict = {0: '#1b9e77', 1: '#d95f02', 2: '#7570b3', 3: '#e7298a', 4: "#D8D8D8", 5: "#fdcdac", 6: "#cbd5e8"}
DAG_color_dict = {'DAG1': "#1b9e77", 'DAG2': "#d95f02", 'DAG3': "#7570b3"}
DAG_ID_Trans1 = {"M1_S1_C1": 'DAG1', "M1_S2_C1": 'DAG1', "M1_S1_C2": 'DAG2', "M1_S2_C2": 'DAG2', "M2_S1_C1": 'DAG3',
                 "M2_S2_C1": 'DAG3'}
DAG_ID_Trans2 = {"M1_S1_C1": 'DAG1', "M1_S2_C1": 'DAG2', "M1_S1_C2": 'DAG3', "M1_S2_C2": 'DAG4', "M2_S1_C1": 'DAG5',
                 "M2_S2_C1": 'DAG6'}


# Dag_color_list = {"M1_S1_C1": {0: "#D8D8D8", 1: "#D8D8D8"},   "M1_S2_C1": {0: "#b3e2cd", 1: "#b3e2cd", 2: "#b3e2cd"},
#                   "M1_S2_C2": {0: "#fdcdac", 1: "#fdcdac"},   "M1_S2_C2": {0: "#fdcdac", 1: "#fdcdac", 2: "#fdcdac"},
#                   "M2_S1_C1": {0: "#fdcdac", 1: "#fdcdac"},   "M2_S2_C1": {0: "#cbd5e8", 1: "#cbd5e8", 2: "#cbd5e8"},
#                   "M2_S3_C1": {0: "#f4cae4", 1: "#f4cae4", 2: "#f4cae4", 3: "#f4cae4", 4: "#f4cae4", 5: "#f4cae4"}}
# color_list_t = ['palevioletred', 'cornflowerblue', 'darkorange', 'indianred', 'green', 'royalblue', 'tomato',
#                 'greenyellow', 'dodgerblue', 'fuchsia', 'blueviolet', 'lawngreen', 'pink', 'olive', 'silver',
#                 'lightcoral', 'lightseagreen', 'plum']

def show_core_data_list(Cdlist_obj, Show_or_Save, file_name, DAG_list, Period, cycle):
    dict_len = len(Cdlist_obj)
    plt.figure(figsize=(25, 600 * dict_len))
    for num_id, (key, value) in enumerate(Cdlist_obj.items()):
        ax1 = plt.subplot(2 * dict_len, 1, 2 * num_id + 1)
        __show_makespan(value, ax1, DAG_list, font_size=8, title=key, Period=Period, cycle=cycle)
        ax2 = plt.subplot(2 * dict_len, 1, 2 * num_id + 2)
        __show_flow_rate_list(value, ax2)

    if Show_or_Save == 'Show':
        plt.show()
    else:
        os.makedirs(Show_or_Save, mode=0o777, exist_ok=True)
        plt.savefig(Show_or_Save + file_name + '.pdf')
        plt.close()

def __show_flow_rate_list(core_data_dict, ax, step_size=0.1, windows_size=0):
    max_last_finish_time = max([cx.last_finish_time for cid,cx in core_data_dict.items()])
    core_et_dict = {core_id:[] for core_id ,core_data in core_data_dict.items()}
    ax.set(xlim=[-1, max_last_finish_time], ylim=[0, 1 + len(core_data_dict)])
    ax.set_yticks(list(range(1 + len(core_data_dict))),rotation=0, fontproperties='Times New Roman',size=8)

    y_value = 0
    ret_plot = []
    for core_id ,core_data in core_data_dict.items():
        core_data.Core_Running_Task.sort(key=lambda x: x['start_time'], reverse=False)
        last_time_dict = {'start_time':0, 'end_time':0}
        for rn in core_data.Core_Running_Task:
            if rn['start_time'] == last_time_dict['end_time']:
                last_time_dict['end_time'] = rn['end_time']
            elif rn['start_time'] > last_time_dict['end_time']:
                core_et_dict[core_id].append(copy.deepcopy(last_time_dict))
                last_time_dict = {'start_time':rn['start_time'], 'end_time':rn['end_time']}
            else:
                os.error('show_error!!!')
        core_et_dict[core_id].append(copy.deepcopy(last_time_dict))
 # [x, y]
        for time_dict_x in core_et_dict[core_id]:
            ret_plot.append(('start_time', time_dict_x['start_time']))
            ret_plot.append(('end_time', time_dict_x['end_time']))

    ret_plot.sort(key=lambda x: x[1], reverse=False)
    c_plot = []
    for ret_type, ret_value in ret_plot:
        c_plot.append((ret_value, y_value))
        if ret_type == 'start_time':
            y_value += 1
        elif ret_type == 'end_time':
            y_value -= 1
        else:
            os.error('__show_flow_rate_list')
        c_plot.append((ret_value, y_value))
    # c_plot = list(set(c_plot))
    # c_plot.sort(key=lambda x: x[0], reverse=False)
    x, y = zip(*c_plot)
    ax.plot(x, y)
    ax.fill_between(x, y, 0, alpha=0.1)



# 'best': 0,  # 'upper right': 1,  # 'upper left': 2,  # 'lower left': 3,  # 'lower right': 4,  # 'right': 5,
# 'center left': 6,     # 'center right': 7,    # 'lower center': 8,    # 'upper center': 9,    # 'center': 10,
def __show_makespan(Core_Data_List, ax, DAG_list, font_size, title, Period, cycle, xtikck_type='tick'):
    if xtikck_type == 'MS':
        temp_denominator = 2260000
    elif xtikck_type == 'US':
        temp_denominator = 2260
    elif xtikck_type == 'NS':
        temp_denominator = 2.260
    elif xtikck_type == 'tick':
        temp_denominator = 1
    else:
        print('xtikck_type error!!!')
    # (1) draw pic
    for core_channel, (x_id, x) in enumerate(Core_Data_List.items()):
        for y in x.Core_Running_Task:
            barh_width = y['end_time'] - y['start_time']
            barh_left  = y['start_time']
            text_left  = y['start_time'] + (y['end_time'] - y['start_time']) / 2
            if barh_width == 0:
                continue
            # if 'preempt_test' in y['node'][1]:
            #     ax.barh(y=core_channel, width=barh_width, height=0.8, left=barh_left,
            #             color='red', edgecolor='gray')
            #     ax.text(# s='{0}\n{1}'.format(f'{y["node"][0]}', f'{y["node"][1]["DAG"].graph["DAG_NUM"]}'),
            #             s='{0}\n'.format(f'{y["node"][0]}', f'{y["node"][1]["WCET"]}', f'{y["node"][1]["DAG"].graph["DAG_NUM"]}'),
            #             y=core_channel, x=text_left, fontsize=font_size, family='Times New Roman', ha='center', va='center')
            # else:
            # if y['node'][1]['critic']:
            #     color_c = 'red'
            # else:
            #     color_c = color_list[y['node'][1]['DAG'].graph['DAGTypeID']]
            # color_c = color_list[y['node'][1]['DAG'].graph['DAGTypeID']]
            color_c = color_list[y['node'][1]['DAG'].graph['Criticality']]
            ax.barh(y=core_channel, width=barh_width, height=0.8, left=barh_left,
                    color=color_c, edgecolor='gray')
            ax.text(# s='{0}\n{1}'.format(f'{y["node"][0]}', f'{y["node"][1]["DAG"].graph["DAG_NUM"]}'),
                    s='{0}\n'.format(f'{y["node"][0]}', f'{y["node"][1]["WCET"]}', f'{y["node"][1]["DAG"].graph["DAG_NUM"]}'),
                    y=core_channel, x=text_left, fontsize=font_size, family='Times New Roman', ha='center', va='center')
    # (2) set title
    # plt.legend():函数可以为图形添加图例，图例的内容是由可迭代的artist或者文本提供的，比如，可以把曲线的标签放在图例中。其完整用法为：
    # plt.legend(handles, labels, loc, title, prop)，# 其中：
    #     handles：    图例中绘制的那些artist；
    #     labels：     图例中每个artist的标签；
    #     loc：        图例的位置；
    #     title：      图例的标题；
    #     prop：       图例中文本的属性设置；
    # makespan_res = cycle * Period
    makespan_res = Core.ret_makespan(Core_Data_List)
    ax.ticklabel_format(style='plain')
    ax.set_title(title + f"makespan:{makespan_res}", fontsize=font_size, color="black", weight="light", ha='left', x=0)
    ax.legend([ax.scatter(0, 0, marker="s", color=color_list[dag_x.graph['Criticality']]) for dag_x in DAG_list],
              [f'dag_{dag_x.graph["Criticality"]}' for dag_x in DAG_list],
              loc='upper right', title='', prop={'family': 'Times New Roman', 'size': font_size})
    # plt.legend( [plt.scatter(0, 0, marker="s", color=color_value) for dag_id_x in DAG_ID_list for color_id, color_value in Dag_color_list[dag_id_x].items()],
    #             ['{0}-flow{1}'.format(DAG_ID_Trans_MC[dag_id_x], color_id) for dag_id_x in DAG_ID_list for color_id, color_value in Dag_color_list[dag_id_x].items()],
    #             loc='upper right', title='', prop={'family': 'Times New Roman', 'size': font_size})

    # plt.legend( [plt.scatter(0, 0, marker="s", color=DAG_color_list[dag_id_x]) for dag_id_x in ["DAG1", "DAG2", "DAG3"]],
    #             ['{0}'.format(dag_id_x) for dag_id_x in ["DAG1", "DAG2", "DAG3"]],
    #             loc='upper right', title='', prop={'family': 'Times New Roman', 'size': font_size} )

    ax.set(xlim=[0, makespan_res], ylim=[-0.5, len(Core_Data_List) - 0.5])
    ax.set_xticks([Period * (Period_x + 1) for Period_x in range(cycle)], rotation=0, size=font_size)
    ax.set_yticks([core_channel for core_channel in range(len(Core_Data_List))],
                  ['core {0}'.format(x.Core_ID) for x_id, x in Core_Data_List.items()],
                  rotation=0, fontproperties='Times New Roman', size=font_size)

    ax.set_ylabel('core-axis', fontsize=font_size)  # 设置y轴标签字体大小
    ax.set_xlabel('time-axis', fontsize=font_size)  # 设置x轴标签字体大小

    for Period_x in range(cycle):
        ax.axvline(x=Period * (Period_x + 1), ls="-", c="red")  # 添加垂直直线
        # ax.text(y=len(Core_Data_List) - 0.5, x=Period * (Period_x + 1), s='{0}'.format(Period * (Period_x + 1)), fontsize=font_size,
        #         family='Times New Roman', ha='left', va='bottom')

    # print(max([core_data_x.get_finish_time() for core_data_x in Core_Data_List]) / 2.260)  # makespan
    # print(max([core_data_x.get_finish_time() for core_data_x in Core_Data_List]))  # makespan
    # makespan_res = max([Core_Data_x.last_finish_time for Core_Data_x in Core_Data_List])



if __name__ == "__main__":
    Dag_ID_List = ['M1_S1_C1']
    # Dag_ID_List = ['DAG_1', 'DAG_2', 'DAG_3']
    core_num = 3
    Core_Data_List = [Core.Core_Obj(f'core_{i + 1}') for i in range(core_num)]

    core0 = Core_Data_List[0]
    core0.Insert_Task_Info(2, dag_NUM=1, node=[1, {'Node_ID': '1'}], start_time=0, end_time=100)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[2, {'Node_ID': '2'}], start_time=100, end_time=200)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[3, {'Node_ID': '3'}], start_time=200, end_time=300)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[4, {'Node_ID': '4'}], start_time=300, end_time=400)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[5, {'Node_ID': '5'}], start_time=600, end_time=700)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[6, {'Node_ID': '6'}], start_time=700, end_time=800)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[7, {'Node_ID': '7'}], start_time=800, end_time=900)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[8, {'Node_ID': '8'}], start_time=1000, end_time=1200)

    core1 = Core_Data_List[1]
    core1.Insert_Task_Info(0, dag_NUM=1, node=[1, {'Node_ID': '1'}], start_time=0, end_time=100)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[2, {'Node_ID': '2'}], start_time=100, end_time=200)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[3, {'Node_ID': '3'}], start_time=200, end_time=300)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[4, {'Node_ID': '4'}], start_time=300, end_time=400)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[5, {'Node_ID': '5'}], start_time=600, end_time=700)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[6, {'Node_ID': '6'}], start_time=700, end_time=800)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[7, {'Node_ID': '7'}], start_time=800, end_time=900)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[8, {'Node_ID': '8'}], start_time=1000, end_time=1200)

    core2 = Core_Data_List[2]
    core2.Insert_Task_Info(1, dag_NUM=1, node=[1, {'Node_ID': '1'}], start_time=0, end_time=100)
    core2.Insert_Task_Info(1, dag_NUM=1, node=[2, {'Node_ID': '2'}], start_time=100, end_time=200)
    core2.Insert_Task_Info(1, dag_NUM=1, node=[3, {'Node_ID': '3'}], start_time=200, end_time=300)
    core2.Insert_Task_Info(1, dag_NUM=1, node=[4, {'Node_ID': '4'}], start_time=300, end_time=400)
    core2.Insert_Task_Info(1, dag_NUM=1, node=[5, {'Node_ID': '5'}], start_time=600, end_time=700)
    core2.Insert_Task_Info(1, dag_NUM=1, node=[6, {'Node_ID': '6'}], start_time=700, end_time=800)
    core2.Insert_Task_Info(1, dag_NUM=1, node=[7, {'Node_ID': '7'}], start_time=800, end_time=900)
    core2.Insert_Task_Info(1, dag_NUM=1, node=[8, {'Node_ID': '8'}], start_time=1000, end_time=1200)

    makespan = max([Core_Data_x.last_finish_time for Core_Data_x in Core_Data_List])
    FontSize = 14
    plt.xlabel("time-axis", fontdict={'family': 'Times New Roman', 'size': 16})
    plt.ylabel("core-list", fontdict={'family': 'Times New Roman', 'size': 16})

    for exam_id in range(1, 3):  # range(1,3) = [1,2,3) = [1,2]
        ax = plt.subplot(2, 1, exam_id)
        show_dag_and_makespan(Core_Data_List=Core_Data_List, ax_obj=ax, font_size=FontSize)
        ax.set_title("Makespan:{0}={1}ms\n Workload:{2}".format(makespan, makespan / 2260000, 0), fontsize=FontSize,
                     fontproperties='Times New Roman', color="black", weight="light", ha='left', x=0)

    plt.show()

    # show_dag_and_makespan(Dag_ID_List, [core1, core2, core3], makespan_res=2000)
    # show_dag_and_makespan(Dag_ID_List, [core1, core2, core3], None, 2000, {}, 14)