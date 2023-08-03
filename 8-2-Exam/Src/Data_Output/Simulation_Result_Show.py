#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Randomized DAG Generator
# Fang YJ
# Real-Time Systems Group
# Hunan University HNU
################################################################################

import os
import matplotlib.pyplot as plt
from . import Core as Core
# import Core as Core
# import Core as Core

""" 一个处理器（Processor），拥有特定数量的资源（core，内存，缓存等）。一个客户首先申请服务。在对应服务时间完成后结束并离开工作站 """
DAG_ID_Trans = {"M1_S1_C1": 'DAG1',
                "M1_S2_C1": 'DAG2',
                "M1_S2_C2": 'DAG3',
                "M1_S2_C2": 'DAG4',
                "M2_S1_C1": 'DAG5',
                "M2_S2_C1": 'DAG6'}

color_dict = {0: '#1b9e77', 1: '#d95f02', 2: '#7570b3', 3: '#e7298a'}

DAG_ID_Trans_MC = {"M1_S1_C1": 'DAG1', "M1_S2_C1": 'DAG1',
                   "M1_S1_C2": 'DAG2', "M1_S2_C2": 'DAG2',
                   "M2_S1_C1": 'DAG3', "M2_S2_C1": 'DAG3'}

DAG_color_list = {
    'DAG1': "#1b9e77",
    'DAG2': "#d95f02",
    'DAG3': "#7570b3",
}
# Dag_color_list = {"M1_S1_C1": {0: "#D8D8D8", 1: "#D8D8D8"},
#                   "M1_S2_C1": {0: "#b3e2cd", 1: "#b3e2cd", 2: "#b3e2cd"},
#                   "M1_S2_C2": {0: "#fdcdac", 1: "#fdcdac"},
#                   "M1_S2_C2": {0: "#fdcdac", 1: "#fdcdac", 2: "#fdcdac"},
#                   "M2_S1_C1": {0: "#fdcdac", 1: "#fdcdac"},
#                   "M2_S2_C1": {0: "#cbd5e8", 1: "#cbd5e8", 2: "#cbd5e8"},
#                   "M2_S3_C1": {0: "#f4cae4", 1: "#f4cae4", 2: "#f4cae4", 3: "#f4cae4", 4: "#f4cae4", 5: "#f4cae4"}}


Dag_color_list = {"M1_S1_C1": {0: "#D8D8D8", 1: "#b3e2cd"},
                  "M1_S2_C1": {0: "#D8D8D8", 1: "#fdcdac", 2: "#cbd5e8"},
                  "M1_S2_C2": {0: "#D8D8D8", 1: "#b3e2cd"},
                  "M1_S2_C2": {0: "#D8D8D8", 1: "#fdcdac", 2: "#cbd5e8"},
                  "M2_S1_C1": {0: "#D8D8D8", 1: "#b3e2cd"},
                  "M2_S2_C1": {0: "#D8D8D8", 1: "#fdcdac", 2: "#cbd5e8"}}

Dag_color_CC = {0: "#D8D8D8", 1: "#1b9e77", 2: "#fdcdac", 3: "#cbd5e8"}

#
# 'DAG2': "#d95f02",
# 'DAG3': "#7570b3",


dag_cnode_dict = {
    'DAG1_M': [0, 4, 6, 13, 20, 32, 38, 41, 46, 47],
    'DAG2_M': [0, 2, 6, 14],
    'DAG3_M': [0, 2, 4, 13, 21, 35, 36]
}
# #############
# if y['node'][1]['Flow_Num'] == 1:
#     color_id = '#fdcdac'
#     # ", 1: "", 2: ""
#     pass
# elif y['node'][1]['Flow_Num'] == 2:
#     color_id = '#cbd5e8'
#     pass

def show_makespan(Core_Data_List, ax, font_size, title_data):
    makespan_res = Core.ret_makespan(Core_Data_List)
    # makespan_res_C1 = Core.ret_dag_cri_makespan(Core_Data_List, 1)
    # makespan_res_C2 = Core.ret_dag_cri_makespan(Core_Data_List, 2)
    ax.set_title(title_data + f"makespan:{makespan_res}", fontsize=font_size, color="black", weight="light", ha='left', x=0)    # 子图标题
    core_name_list = []
    core_y_location_list = []
    ax.ticklabel_format(style='plain')
    plt.xticks(fontproperties='Times New Roman', size=font_size)
    plt.xlim(xmin=0, xmax=makespan_res)
    for core_channel, (x_id, x) in enumerate(Core_Data_List.items()):
        core_name_list.append('core {0}'.format(x.Core_ID))
        for y in x.Core_Running_Task:
            barh_width = y['end_time'] - y['start_time']
            barh_left  = y['start_time']
            text_left  = y['start_time'] + (y['end_time'] - y['start_time']) / 2
            # name       = '{0}:{1}'.format(y['node'][1]['JobTypeID'], y['node'][1]['Node_Index'])
            # name = (y['node'][1]['EDIT_ID'] + '/')[4:-1]
            # name       = '{0}\n{1}'.format(y['node'][1]['Node_ID'], y['node'][1]['Node_Index'])
            # name       = '{0}\n{1}--{2}'.format(y['node'][1]['Node_ID'], y['node'][1]['WCET'],  y['node'][1]['DAG'].graph['DAG_ID'])
            # name = ''
            name = f'{y["node"][0]}'
            # Bar_Colore = 'lightgray'
            # Bar_Colore = Dag_color_CC[ y['node'][1]['Flow_Num'] ]
            Bar_Colore = color_dict[ y['node'][1]['Criticality'] ]
            # Bar_Colore = '#fdcdac'
            # if barh_width < 10:
            #     continue
            ax.barh(y=core_channel, width=barh_width, height=1, left=barh_left, color=Bar_Colore, edgecolor='black')
            ax.text(y=core_channel, x=text_left, s='{0}'.format(name, barh_width), fontsize=font_size, family='Times New Roman', ha='center', va='center')
            # plt.xlabel("time-axis_({0})".format(xtikck_type), fontdict={'family': 'Times New Roman', 'size': font_size})
        core_y_location_list.append(core_channel * 1)
    plt.yticks(core_y_location_list, core_name_list, fontproperties='Times New Roman', size=font_size)


def show_single_dag_and_makespan_random(Core_Data_List, makespan_res, ax, xtikck_type, font_size, DAG_T):
    core_channel = 0
    core_name_list = []
    core_y_location_list = []
    temp_denominator = 1
    if xtikck_type == 'MS':
        temp_denominator = 2260000
    elif xtikck_type == 'US':
        temp_denominator = 2260
    elif xtikck_type == 'NS':
        temp_denominator = 2.260

    ax.ticklabel_format(style='plain')

    plt.xticks(fontproperties='Times New Roman', size=font_size)
    plt.xlim(xmin=0, xmax=makespan_res / temp_denominator)

    for x in Core_Data_List:
        core_name_list.append('core {0}'.format(x.Core_ID))
        for y in x.Core_Running_Task:
            barh_width = (y['end_time'] - y['start_time']) / temp_denominator
            if barh_width == 0:
                continue
            barh_left = (y['start_time']) / temp_denominator
            text_left = (y['start_time'] + (y['end_time'] - y['start_time']) / 2) / temp_denominator
            plt.xlabel("time-axis_({0})".format(xtikck_type), fontdict={'family': 'Times New Roman', 'size': font_size})

            name = y['node'][1]['Node_ID']
            if name in dag_cnode_dict[DAG_T]:
                ax.barh(y=core_channel, width=barh_width, height=1, left=barh_left, color='lightsalmon', edgecolor='gray')
            else:
                ax.barh(y=core_channel, width=barh_width, height=1, left=barh_left, color='lightgreen', edgecolor='gray')
            ax.text(y=core_channel, x=text_left, s='{0}'.format(name), fontsize=font_size, family='Times New Roman',
                    ha='center', va='center')
        core_y_location_list.append(core_channel * 1)
        core_channel += 1
    plt.yticks(core_y_location_list, core_name_list, fontproperties='Times New Roman', size=font_size)  # 设置y刻度:用文字来显示刻度


def show_mc_dag_and_makespan(Core_Data_List, makespan_res, ax, xtikck_type, font_size):
    core_channel = 0
    core_name_list = []
    core_y_location_list = []
    temp_denominator = 1
    if xtikck_type == 'MS':
        temp_denominator = 2260000
    elif xtikck_type == 'US':
        temp_denominator = 2260
    elif xtikck_type == 'NS':
        temp_denominator = 2.260

    ax.ticklabel_format(style='plain')

    plt.legend( [plt.scatter(0, 0, marker="s", color=DAG_color_list[dag_id_x]) for dag_id_x in ["DAG1", "DAG2", "DAG3"]],
                ['{0}'.format(dag_id_x) for dag_id_x in ["DAG1", "DAG2", "DAG3"]],
                loc='upper right', title='', prop={'family': 'Times New Roman', 'size': font_size} )

    plt.xticks(fontproperties='Times New Roman', size=font_size)
    plt.xlim(xmin=0, xmax=makespan_res / temp_denominator)

    for x in Core_Data_List:
        core_name_list.append('core {0}'.format(x.Core_ID))
        for y in x.Core_Running_Task:
            # if y['node'][1]['EDIT_ID'] in ['Job_29.1', 'Job_0']:            # 特殊结点跳过；
            #     continue
            barh_width = (y['end_time'] - y['start_time']) / temp_denominator
            barh_left = (y['start_time']) / temp_denominator
            text_left = (y['start_time'] + (y['end_time'] - y['start_time']) / 2) / temp_denominator
            plt.xlabel("time-axis_({0})".format(xtikck_type), fontdict={'family': 'Times New Roman', 'size': font_size})

            # name = (y['node'][1]['EDIT_ID'] + '/')[4:-1]
            # name = y['node'][1]['EDIT_ID']
            name = y['node'][1]['Node_ID']
            temp_dag_id = y['node'][1]['DAG'].graph['DAG_ID']

            # ax.barh(y=core_channel, width=barh_width, height=1, left=barh_left, color=color_dict[y['node'][1]['Criticality']], edgecolor='gray')
            # ax.text(y=core_channel, x=text_left, s='{0}'.format(y['node'][1]['Node_ID']), fontsize=font_size, family='Times New Roman', ha='center', va='center')
            ax.barh(y=core_channel, width=barh_width, height=1, left=barh_left, color=DAG_color_list[DAG_ID_Trans_MC[temp_dag_id]], edgecolor='gray')
            ax.text(y=core_channel, x=text_left, s='{0}'.format(name), fontsize=font_size, family='Times New Roman', ha='center', va='center')

        core_y_location_list.append(core_channel * 1)
        core_channel += 1
    plt.yticks(core_y_location_list, core_name_list, fontproperties='Times New Roman', size=font_size)  # 设置y刻度:用文字来显示刻度


# 'best': 0,  # 'upper right': 1,  # 'upper left': 2,  # 'lower left': 3,  # 'lower right': 4,  # 'right': 5,
# 'center left': 6,     # 'center right': 7,    # 'lower center': 8,    # 'upper center': 9,    # 'center': 10,
def show_dag_and_makespan(Core_Data_List, makespan_res, ax, xtikck_type, font_size):
    core_channel = 0
    core_name_list = []
    core_y_location_list = []
    temp_denominator = 1
    if xtikck_type == 'MS':
        temp_denominator = 2260000
    elif xtikck_type == 'US':
        temp_denominator = 2260
    elif xtikck_type == 'NS':
        temp_denominator = 2.260
    else:
        pass

    ax.ticklabel_format(style='plain')
    # plt.legend( [plt.scatter(0, 0, marker="s", color=color_value) for dag_id_x in DAG_ID_list for color_id, color_value in Dag_color_list[dag_id_x].items()],
    #             ['{0}-flow{1}'.format(DAG_ID_Trans_MC[dag_id_x], color_id) for dag_id_x in DAG_ID_list for color_id, color_value in Dag_color_list[dag_id_x].items()],
    #             loc='upper right', title='', prop={'family': 'Times New Roman', 'size': font_size})

    # plt.legend( [plt.scatter(0, 0, marker="s", color=DAG_color_list[dag_id_x]) for dag_id_x in ["DAG1", "DAG2", "DAG3"]],
    #             ['{0}'.format(dag_id_x) for dag_id_x in ["DAG1", "DAG2", "DAG3"]],
    #             loc='upper right', title='', prop={'family': 'Times New Roman', 'size': font_size} )
    plt.xticks(fontproperties='Times New Roman', size=font_size)
    plt.xlim(xmin=0, xmax=makespan_res / temp_denominator)

    for x in Core_Data_List:
        core_name_list.append('core {0}'.format(x.Core_ID))
        for y in x.Core_Running_Task:
            if y['node'][1]['Node_ID'] in ['Job_29.1', 'Job_0']:            # 特殊结点跳过；
                continue
            barh_width = (y['end_time'] - y['start_time']) / temp_denominator
            barh_left = (y['start_time']) / temp_denominator
            text_left = (y['start_time'] + (y['end_time'] - y['start_time']) / 2) / temp_denominator
            plt.xlabel("time-axis_({0})".format(xtikck_type), fontdict={'family': 'Times New Roman', 'size': font_size})

            # name = (y['node'][1]['Node_ID'] + '/')[4:-1]
            # name = y['node'][1]['Node_ID']
            # name = y['node'][1]['EDIT_ID'] + '\n--' + str(y['node'][1]['Flow_Num'])
            name = (y['node'][1]['EDIT_ID'] + '/')[4:-1]
            # 'name' in y['node'][1]    # 有'name'的key值
            temp_dag_id = y['node'][1]['DAG'].graph['DAG_ID']
            # ax.barh(y=core_channel, width=barh_width, height=1, left=barh_left, color=color_dict[y['node'][1]['Criticality']], edgecolor='gray')
            # ax.text(y=core_channel, x=text_left, s='{0}'.format(y['node'][1]['Node_ID']), fontsize=font_size, family='Times New Roman', ha='center', va='center')
            ax.barh(y=core_channel, width=barh_width, height=1, left=barh_left, color=DAG_color_list[DAG_ID_Trans_MC[temp_dag_id]], edgecolor='gray')
            ax.text(y=core_channel, x=text_left, s='{0}'.format(name), fontsize=font_size, family='Times New Roman', ha='center', va='center')

        core_y_location_list.append(core_channel * 1)
        core_channel += 1
    plt.yticks(core_y_location_list, core_name_list, fontproperties='Times New Roman', size=font_size)  # 设置y刻度:用文字来显示刻度
    print(max([core_data_x.get_finish_time() for core_data_x in Core_Data_List])/2.260)  # makespan
    print(max([core_data_x.get_finish_time() for core_data_x in Core_Data_List]))        # makespan


def show_dag_and_makespan_2(Core_Data_List, ax_obj, font_size):
    makespan_res = max([Core_Data_x.last_finish_time for Core_Data_x in Core_Data_List])
    core_name_list = []
    core_y_location_list = []
    ax_obj.ticklabel_format(style='plain')
    for core_id, x in enumerate(Core_Data_List):
        core_name_list.append(x.Core_ID)
        core_y_location_list.append(core_id * 1)
        for y in x.Core_Running_Task:
            color_lable = color_dict[y['dag_ID']]
            barh_width = y['end_time'] - y['start_time']
            barh_start = y['start_time']
            node_id = y['node'][1]['Node_ID']  # name = (y['node'][1]['Node_ID'] + '/')[4:-1]
            # if y['node'][1]['Node_ID'].endswith('Job_29.1') or y['node'][1]['Node_ID'].endswith('Job_0'):
            if node_id in ['Job_29.1', 'Job_0']:
                continue
            ax_obj.barh(y=core_id * 1, width=barh_width, height=1, left=barh_start, color=color_lable, edgecolor='gray')
            ax_obj.text(x=barh_start + barh_width / 2, y=core_id, s='{0}'.format(node_id), fontsize=font_size,
                        family='Times New Roman', ha='center', va='center')
    plt.yticks(core_y_location_list, core_name_list, fontproperties='Times New Roman', size=font_size)  # 设置y刻度:用文字来显示刻度
    plt.xticks(fontproperties='Times New Roman', size=font_size)
    plt.xlim(xmin=0, xmax=makespan_res * 1)


def show_core_data_list(Cdlist_obj, Show_or_Save, file_name):
    dict_len = len(Cdlist_obj)
    plt.figure(figsize=(25, 10 * dict_len))
    FontSize = 8
    for num_id, (key, value) in enumerate(Cdlist_obj.items()):
        ax = plt.subplot(dict_len, 1, num_id+1)
        show_makespan(value, ax, FontSize, key)
    if Show_or_Save == 'Show':
        plt.show()
    else:
        os.makedirs(Show_or_Save, mode=0o777, exist_ok=True)
        plt.savefig(Show_or_Save + file_name)
        plt.close()


if __name__ == "__main__":
    Dag_ID_List = ['M1_S1_C1']
    core_num = 3
    Core_Data_List = [Core.Core_Obj(f'core_{i + 1}') for i in range(core_num)]

    core0 = Core_Data_List[0]
    core0.Insert_Task_Info(2, dag_NUM=1, node=[1, {'Node_ID': '1'}], start_time=0,    end_time=100)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[2, {'Node_ID': '2'}], start_time=100,  end_time=200)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[3, {'Node_ID': '3'}], start_time=200,  end_time=300)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[4, {'Node_ID': '4'}], start_time=300,  end_time=400)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[5, {'Node_ID': '5'}], start_time=600,  end_time=700)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[6, {'Node_ID': '6'}], start_time=700,  end_time=800)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[7, {'Node_ID': '7'}], start_time=800,  end_time=900)
    core0.Insert_Task_Info(2, dag_NUM=1, node=[8, {'Node_ID': '8'}], start_time=1000, end_time=1200)

    core1 = Core_Data_List[1]
    core1.Insert_Task_Info(0, dag_NUM=1, node=[1, {'Node_ID': '1'}], start_time=0,    end_time=100)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[2, {'Node_ID': '2'}], start_time=100,  end_time=200)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[3, {'Node_ID': '3'}], start_time=200,  end_time=300)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[4, {'Node_ID': '4'}], start_time=300,  end_time=400)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[5, {'Node_ID': '5'}], start_time=600,  end_time=700)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[6, {'Node_ID': '6'}], start_time=700,  end_time=800)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[7, {'Node_ID': '7'}], start_time=800,  end_time=900)
    core1.Insert_Task_Info(0, dag_NUM=1, node=[8, {'Node_ID': '8'}], start_time=1000, end_time=1200)

    core2 = Core_Data_List[2]
    core2.Insert_Task_Info(1, dag_NUM=1, node=[1, {'Node_ID': '1'}], start_time=0,    end_time=100)
    core2.Insert_Task_Info(1, dag_NUM=1, node=[2, {'Node_ID': '2'}], start_time=100,  end_time=200)
    core2.Insert_Task_Info(1, dag_NUM=1, node=[3, {'Node_ID': '3'}], start_time=200,  end_time=300)
    core2.Insert_Task_Info(1, dag_NUM=1, node=[4, {'Node_ID': '4'}], start_time=300,  end_time=400)
    core2.Insert_Task_Info(1, dag_NUM=1, node=[5, {'Node_ID': '5'}], start_time=600,  end_time=700)
    core2.Insert_Task_Info(1, dag_NUM=1, node=[6, {'Node_ID': '6'}], start_time=700,  end_time=800)
    core2.Insert_Task_Info(1, dag_NUM=1, node=[7, {'Node_ID': '7'}], start_time=800,  end_time=900)
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



