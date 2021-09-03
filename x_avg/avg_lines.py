import UnityPy
import pandas as pd
from pandas import ExcelWriter
from avg import xlsx_to_dict
from avg import find_avg_file
from avg import show_avg_sort

XLSX = "./res/line.xlsx"
LINE_LENGTH = "./res/line_length.xlsx"
AVG = "./res/asset_textavg.ab"
NGA = "./res/nga_line.txt"


def save(sp_json):
    sp_arr = []
    for key in sp_json.keys():
        sp_arr.append({"speaker": key, "number": sp_json[key][0], "length": sp_json[key][1]})

    with ExcelWriter(XLSX) as writer:
        data = pd.DataFrame.from_dict(sp_arr)
        data.to_excel(writer, sheet_name="avg", index=None)

    display(sp_arr)
    return


def display(sp_arr):
    max_length = 0
    for sp in sp_arr:
        if sp["number"] > max_length:
            max_length = sp["number"]

    nga = ""
    while max_length > 0:
        this_num = ""
        for num in sp_arr:
            if num['number'] == max_length:
                this_num += num['speaker'] + "，"

        if this_num:
            nga += f"[quote][{max_length}] - {this_num[:-1]}[/quote]"
        max_length -= 1

    with open(NGA, "w", encoding="utf-8") as f:
        f.write(nga)


def get(scenario, episode, chapter):
    avg_dict = find_avg_file(scenario, episode, chapter)

    env = UnityPy.load(AVG)

    speaker_json = {}
    line_length_together = 0
    for obj in env.objects:
        data = obj.read()
        if obj.type == "TextAsset":

            for avg in avg_dict:
                if data.name == avg["file"] and avg["path"] in obj.container:
                    lines = str(data.script, encoding="utf-8").split("\r\n")

                    for line in lines:
                        if line.find(":") == -1 and line.find("：") == -1:
                            continue
                        elif line.find(":") == -1:
                            line_text = line_handle(line.split("：")[-1])
                        else:
                            line_text = line_handle(line.split(":")[-1])

                        line_length_together += len(line_text)
                        line_length = len(line_text)

                        if line.find("<Speaker>") == -1 or line.find("</Speaker>") == -1:
                            continue

                        if line.find("<Speaker></Speaker>") != -1:
                            speaker = "旁白"
                        else:
                            speaker = line[line.find("<Speaker>") + len("<Speaker>"):line.find("</Speaker>")]

                        if speaker not in speaker_json.keys():
                            speaker_json[speaker] = [1, line_length]
                        else:
                            speaker_json[speaker][0] += 1
                            speaker_json[speaker][1] += line_length

                    break

    save(speaker_json)

    print(f"-- 执行完成")
    print(f"-- 【{episode}】-【{chapter}】文本量：{line_length_together}")

    return line_length_together


def line_length_all():
    avg_dict = xlsx_to_dict()

    scenario_list = {}
    for avg in avg_dict:
        if avg["story"] == "1" and avg["scenario"] != "":
            if avg["scenario"] not in scenario_list.keys():
                scenario_list[avg["scenario"]] = []
            if avg["episode"] != "" and avg["episode"] not in scenario_list[avg["scenario"]]:
                scenario_list[avg["scenario"]].append(avg["episode"])

    with ExcelWriter(LINE_LENGTH) as writer:
        for scenario in scenario_list.keys():
            print(scenario, " - ", scenario_list[scenario])

            length_list = []
            if scenario_list[scenario]:
                for episode in scenario_list[scenario]:
                    length_list.append({"名称": episode, "文本量": get(scenario, episode, [])})
            else:
                length_list.append({"名称": scenario, "文本量": get(scenario, [], [])})

            data = pd.DataFrame.from_dict(length_list)
            data.to_excel(writer, sheet_name=scenario, index=None)


def line_handle(text):
    i = 0
    text_a = 0

    while i < len(text):
        if text[i] == "<":
            text_a = i
        if text[i] == ">":
            text = text[:text_a] + text[i+1:]
            i = text_a
            text_a = 0
        i += 1

    text = text.replace("\n", "").replace("+", "")

    return text


def main():
    print("-- 台词、出场率统计")
    mode = input("-- 请选择想要执行的模式：【1：全部执行】，【2：直接输入】，【3：选择输入】，【4：文本量统计】")
    if mode == "1":
        get([], [], [])
    elif mode == "2":
        avg_scenario_target = input("-- 请输入想要查询的【scenario】，不同的【scenario】请用【+】分隔，不输入视为全部：\n").split("+")
        avg_episode_target = input("-- 请输入想要查询的【episode】，不同的【episode】请用【+】分隔，不输入视为全部：\n").split("+")
        avg_chapter_target = input("-- 请输入想要查询的【chapter】，不同的【chapter】请用【+】分隔，不输入视为全部：\n").split("+")
        get(avg_scenario_target, avg_episode_target, avg_chapter_target)
    elif mode == "3":
        target_dict = show_avg_sort()
        get(target_dict["scenario"], target_dict["episode"], target_dict["chapter"])
    elif mode == "4":
        line_length_all()
    else:
        print("-- 模式错误")
        main()


main()

