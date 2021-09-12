import os
import sys
import ujson
import UnityPy
import pandas as pd

sys.path.append("..")
from wikibot import URL
from wikibot import write_wiki
from wikibot import xlsx_dict
from wikibot import login_innbot

STC_SOURCE = "../w_stc_data"
TEXT_SOURCE = "../w_text_data"
AVG_PIC_INFO = "../x_avg/res/pic_info.xlsx"
AVG_NAME = "../x_avg/name.xlsx"
AVG = "../x_avg/res/asset_textavg.ab"


def update_wiki():
    with open(os.path.join(STC_SOURCE, "gun_info.json"), "r", encoding="utf-8") as f_gun:
        gun_info = ujson.load(f_gun)
        f_gun.close()
    with open(os.path.join(TEXT_SOURCE, "gun.txt"), "r", encoding="utf-8") as f_gun_text:
        gun_text = f_gun_text.read()
        f_gun_text.close()

    session = login_innbot()
    code_pic_dict = doll_avg_info()

    for gun in gun_info:
        if int(gun["id"]) > 2000:
            break

        cn_name_tem = gun_text[gun_text.find(gun["name"]) + len("gun-10000001,"):]
        cn_name = cn_name_tem[:cn_name_tem.find("\n")]
        if cn_name.endswith(" "):
            cn_name = cn_name[:-1]

        page = "{{剧情文本整理|出场="
        page += str(code_pic_dict[gun["code"]]["appear"])
        page += "|文本="
        page += str(code_pic_dict[gun["code"]]["text"])
        page += "|内容=\n"

        for scenario in code_pic_dict[gun["code"]]["format"]:
            page += "{{剧情文本整理块|" + scenario + "|"

            for avg in code_pic_dict[gun["code"]]["format"][scenario]:
                page += "{{剧情选项2|分类1="
                page += avg['scenario']
                page += f"|分类2={avg['episode']}|分类3={avg['chapter']}"
                page += f"|目录={avg['path']}|文件={avg['file']}"
                page += f"|名称1={avg['name_a']}|名称2={avg['name']}|名称3={avg['name_b']}"
                page += "}}\n"

            page += "}}\n"

        page += "}}"

        write_wiki(session, URL, cn_name+"/整理", page, '更新')
        # print(page)


def doll_avg_info():
    pic_info_list = xlsx_to_dict(AVG_PIC_INFO)

    with open(os.path.join(STC_SOURCE, "gun_info.json"), "r", encoding="utf-8") as f_gun:
        gun_info = ujson.load(f_gun)
        f_gun.close()

    code_pic_dict = {}
    for gun in gun_info:
        if int(gun["id"]) > 2000:
            continue
        code_pic_dict[gun["code"]] = {"appear": 0, "text": 0, "avg_info": [], "format": {}}

    env = UnityPy.load(AVG)
    avg_dict = xlsx_to_dict(AVG_NAME)

    for avg in avg_dict:
        if avg["story"] != "1":
            continue

        for obj in env.objects:
            data = obj.read()
            if data.name != avg["file"] or avg["path"] not in obj.container:
                continue

            lines = str(data.script, encoding="utf-8").split("\r\n")

            for line in lines:
                if "(" not in line or "||" not in line:
                    continue

                pic_part = line.split("||")[0]
                text_part = line.replace("：", ":").split(":")[-1]

                speaker = "a"
                pic = {"a": pic_part[:pic_part.find(")") + 1], "b": ""}

                if pic_part.find(";") != -1:
                    pic_part_seg = pic_part[pic_part.find(";")+1:]
                    pic["b"] = pic_part_seg[:pic_part_seg.find(")")+1]

                    if pic_part.find(";") < pic_part.find("<Speaker>"):
                        speaker = "b"

                for info in pic_info_list:
                    if info["pic"] == pic[speaker] and info["code"]:
                        code_pic_dict[info["code"]]["appear"] += 1
                        code_pic_dict[info["code"]]["text"] += len(line_handle(text_part))
                        if avg not in code_pic_dict[info["code"]]["avg_info"]:
                            code_pic_dict[info["code"]]["avg_info"].append(avg)

            break

    for code in code_pic_dict:
        print("--- ", code, code_pic_dict[code]["appear"], code_pic_dict[code]["text"])
        for info in code_pic_dict[code]["avg_info"]:
            avg_format = code_pic_dict[code]["format"]

            if info["scenario"] not in code_pic_dict[code]["format"].keys():
                avg_format[info["scenario"]] = [info]
            else:
                avg_format[info["scenario"]].append(info)

            print("* ", info["scenario"], info["episode"], info["chapter"], str(info["name_a"]) + str(info["name"]) + str(info["name_b"]))

    return code_pic_dict


def xlsx_to_dict(file_path):
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


update_wiki()
