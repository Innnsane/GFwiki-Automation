import UnityPy
import pandas as pd
from pandas import ExcelWriter
from avg import xlsx_to_dict
from avg import find_avg_file
from avg import show_avg_sort

XLSX = "./res/line.xlsx"
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


def get(episode, chapter):
    if episode == [""]:
        episode = []
    if chapter == [""]:
        chapter = []

    avg_dict = find_avg_file(episode, chapter)

    env = UnityPy.load(AVG)

    speaker_json = {}
    for obj in env.objects:
        data = obj.read()
        if obj.type == "TextAsset":

            for avg in avg_dict:
                if data.name == avg["file"]:
                    lines = str(data.script, encoding="utf-8").split("\r\n")

                    for line in lines:
                        if line.find("<Speaker>") == -1 or line.find("</Speaker>") == -1:
                            continue

                        if line.find("<Speaker></Speaker>") != -1:
                            speaker = "旁白"
                        else:
                            speaker = line[line.find("<Speaker>") + len("<Speaker>"):line.find("</Speaker>")]

                        if line.find(":") == -1:
                            line_length = len(line_handle(line.split("：")[-1]))
                        else:
                            line_length = len(line_handle(line.split(":")[-1]))

                        if speaker not in speaker_json.keys():
                            speaker_json[speaker] = [1, line_length]
                        else:
                            speaker_json[speaker][0] += 1
                            speaker_json[speaker][1] += line_length

                    break

    save(speaker_json)

    lines_length = 0
    for key in speaker_json.keys():
        lines_length += int(speaker_json[key][1])
    print(f"-- 执行完成")
    print(f"-- 【{episode}】-【{chapter}】文本量：{lines_length}")


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

    text = text.replace("+", "").replace(" ", "").replace("\n", "")

    return text


def main():
    print("-- 台词、出场率统计")
    mode = input("-- 请选择想要执行的模式：【1：全部执行】，【2：直接输入】，【3：选择输入】")
    if mode == "1":
        get([], [])
    elif mode == "2":
        avg_episode_target = input("-- 请输入想要查询的【episode】，不同的【episode】请用【+】分隔，不输入视为全部：\n").split("+")
        avg_chapter_target = input("-- 请输入想要查询的【chapter】，不同的【chapter】请用【+】分隔，不输入视为全部：\n").split("+")
        get(avg_episode_target, avg_chapter_target)
    elif mode == "3":
        target_dict = show_avg_sort()
        get(target_dict["episode"], target_dict["chapter"])
    else:
        print("-- 模式错误")
        main()


main()

