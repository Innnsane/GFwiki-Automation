import pandas as pd
from pandas import ExcelWriter

AVG = "./asset_textavg.ab"
NAME = "./name.xlsx"


def xlsx_dict(file_path):
    title_dict_raw = pd.read_excel(file_path, index_col=None).to_dict('split')
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


def xlsx_to_dict():
    return xlsx_dict(NAME)


def find_avg_file(scenario, episode, chapter):
    avg_dict_select = []
    avg_dict_raw = xlsx_to_dict()

    if scenario == [""]:
        scenario = []
    if episode == [""]:
        episode = []
    if chapter == [""]:
        chapter = []

    if not scenario:
        for avg in avg_dict_raw:
            if avg["story"] == "1":
                avg_dict_select.append(avg)
    elif scenario and not episode:
        for avg in avg_dict_raw:
            if avg["story"] == "1" and avg["scenario"] in scenario:
                avg_dict_select.append(avg)
    elif scenario and episode and not chapter:
        for avg in avg_dict_raw:
            if not avg["scenario"] or not avg["episode"]:
                continue
            if avg["story"] == "1" and avg["scenario"] in scenario and avg["episode"] in episode:
                avg_dict_select.append(avg)
    elif scenario and episode and chapter:
        for avg in avg_dict_raw:
            if not avg["scenario"] or not avg["episode"] or not avg["chapter"]:
                continue
            if avg["story"] == "1" and avg["scenario"] in scenario and avg["episode"] in episode and avg["chapter"] in chapter:
                avg_dict_select.append(avg)

    return avg_dict_select


def show_avg_sort():
    avg_dict = xlsx_to_dict()

    scenario_list = []
    for avg in avg_dict:
        if avg["story"] == "1" and avg["scenario"] not in scenario_list:
            scenario_list.append(avg["scenario"])
    print(f"-- 共 {len(scenario_list)} 种【scenario】，详细清单如下 --------")
    print_avg_list(scenario_list)

    avg_scenario_target = input("-- 请输入想要查询的【scenario】，不同的【scenario】请用【+】分隔：\n").split("+")
    if avg_scenario_target == [""]:
        print("-- 已跳过，将选择全部剧情")
        return {"scenario": [], "episode": [], "chapter": []}

    episode_list = []
    avg_scenario_sort = []
    for avg in avg_dict:
        if avg["story"] == "1" and avg["scenario"] in avg_scenario_target:
            avg_scenario_sort.append(avg)
            if avg["episode"] not in episode_list:
                episode_list.append(avg["episode"])
    print(f"-- 共 {len(episode_list)} 种【episode】，详细清单如下 --------")
    print_avg_list(episode_list)

    avg_episode_target = input("-- 请输入想要查询的【episode】，不同的【episode】请用【+】分隔：\n").split("+")
    if avg_episode_target == [""]:
        print(f"-- 已跳过，将选择【scenario：{avg_scenario_target}】下的全部剧情")
        return {"scenario": avg_scenario_target, "episode": [], "chapter": []}

    chapter_list = []
    avg_episode_sort = []
    for avg in avg_dict:
        if avg["story"] == "1" and avg["episode"] in avg_episode_target:
            avg_episode_sort.append(avg)
            if avg["chapter"] not in chapter_list:
                chapter_list.append(avg["chapter"])

    print(f"-- 共 {len(chapter_list)} 种【chapter】，详细清单如下 --------")
    print_avg_list(chapter_list)

    avg_chapter_target = input("-- 请输入想要查询的【chapter】，不同的【chapter】请用【+】分隔：\n").split("+")

    for avg in avg_episode_sort:
        if avg["story"] == "1" and avg["chapter"] in avg_chapter_target or avg_chapter_target == [""]:
            print(avg["episode"], avg["chapter"], avg["name_a"], avg["name"], avg["name_b"], avg["file"])

    return {"scenario": avg_scenario_target, "episode": avg_episode_target, "chapter": avg_chapter_target}


def print_avg_list(avg_list):
    i = 0
    while i*5 < len(avg_list):
        max_position = (i+1)*5
        if max_position > len(avg_list):
            max_position = len(avg_list)

        print(avg_list[i*5:max_position])
        i += 1
    return


if __name__ == '__main__':
    print("test")
    # print(find_avg_file(["1"], []))
    # show_avg_sort()

