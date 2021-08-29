import os
import ujson
import pandas as pd
from pandas import ExcelWriter

XLSX = "../x_lines/line.xlsx"
AVG = "./asset_textavg.ab"
NAME = "./name.xlsx"


def xlsx_to_dict():
    title_dict_raw = pd.read_excel(NAME, index_col=None).to_dict('split')
    keys = title_dict_raw['columns']

    title_dict = []
    for data in title_dict_raw['data']:
        this_data_dict = {}

        i = 0
        while i < len(keys):
            this_data_dict[keys[i]] = data[i]

            if type(data[i]) == float:
                try:
                    this_data_dict[keys[i]] = str(int(data[i]))
                except:
                    this_data_dict[keys[i]] = ""

            i += 1

        title_dict.append(this_data_dict)

    return title_dict


def find_avg_file(episode, chapter):
    avg_dict_select = []
    avg_dict_raw = xlsx_to_dict()

    if not episode and not chapter:
        avg_dict_select = avg_dict_raw
    elif episode and not chapter:
        for avg in avg_dict_raw:
            if avg["episode"] in episode:
                avg_dict_select.append(avg)
    elif episode is not None and chapter is not None:
        for avg in avg_dict_raw:
            if avg["episode"] in episode and avg["chapter"] in chapter:
                avg_dict_select.append(avg)

    return avg_dict_select


def show_avg_sort():
    avg_dict = xlsx_to_dict()

    episode_list = []
    for avg in avg_dict:
        if avg["episode"] not in episode_list:
            episode_list.append(avg["episode"])
    print(f"-- 共 {len(episode_list)} 种【episode】，详细清单如下 --------")

    i = 0
    while i*5 < len(episode_list):
        max_position = (i+1)*5
        if max_position > len(episode_list):
            max_position = len(episode_list)

        print(episode_list[i*5:max_position])
        i += 1

    avg_episode_target = input("-- 请输入想要查询的【episode】，不同的【episode】请用【+】分隔：\n").split("+")

    chapter_list = []
    avg_dict_sort = []
    for avg in avg_dict:
        if avg["episode"] in avg_episode_target:
            avg_dict_sort.append(avg)
            if avg["chapter"] not in chapter_list:
                chapter_list.append(avg["chapter"])

    print(f"-- 共 {len(chapter_list)} 种【episode】，详细清单如下 --------")

    i = 0
    while i*5 < len(chapter_list):
        max_position = (i+1)*5
        if max_position > len(chapter_list):
            max_position = len(chapter_list)

        print(chapter_list[i*5:max_position])
        i += 1

    avg_chapter_target = input("-- 请输入想要查询的【chapter】，不同的【chapter】请用【+】分隔：\n").split("+")

    for avg in avg_dict_sort:
        if avg["chapter"] in avg_chapter_target:
            print(avg["episode"], avg["chapter"], avg["name_a"], avg["name"], avg["name_b"], avg["file"])

    return {"episode": avg_episode_target, "chapter": avg_chapter_target}


# print(find_avg_file(["1"], []))
# show_avg_sort()
