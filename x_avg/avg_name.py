import os
import ujson
import UnityPy
import pandas as pd
from pandas import ExcelWriter
from avg_index import INDEX

STC_SOURCE = "../w_stc_data"
TEXT_SOURCE = "../w_text_data"
AVG = "./res/asset_textavg.ab"
NAME = "./name.xlsx"


def update_avg():
    if os.path.exists(NAME):
        avg_dict_old = xlsx_to_dict()
    else:
        avg_dict_old = []

    avg_dict_new = unpack_avg_ab()
    for avg in avg_dict_new:
        exist = None
        for avg_old in avg_dict_old:
            if avg["path"] + avg["file"] == avg_old["path"] + avg_old["file"]:
                exist = True
                break

        if not exist:
            avg_add = {"file": avg["file"], "path": avg["path"],
                       "name_a": "", "name": "", "name_b": "", "sign": "", "scenario": "", "episode": "", "chapter": "", "story": ""}

            print(avg["file"], avg["path"])
            avg_dict_old.append(avg_add)

    save_xlsx(avg_dict_old)


def unpack_avg_ab():
    env = UnityPy.load(AVG)

    avg_dict = []
    for obj in env.objects:
        data = obj.read()

        join_word = "/"
        if obj.type == "TextAsset":
            avg_dict.append({"file": data.name, "path": join_word.join(obj.container.split("/")[3:-1])})

    return avg_dict


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


def initialize_with_pattern(info_all):
    with open(os.path.join(STC_SOURCE, "gun_info.json"), "r", encoding="utf-8") as f_gun:
        gun_info = ujson.load(f_gun)
        f_gun.close()
    with open(os.path.join(TEXT_SOURCE, "gun.txt"), "r", encoding="utf-8") as f_gun_text:
        gun_text = f_gun_text.read()
        f_gun_text.close()
    with open(os.path.join(STC_SOURCE, "fetter_story_info.json"), "r", encoding="utf-8") as f_fetter_story:
        fetter_story_info = ujson.load(f_fetter_story)
        f_fetter_story.close()
    with open(os.path.join(TEXT_SOURCE, "fetter.txt"), "r", encoding="utf-8") as f_fetter_text:
        fetter_text = f_fetter_text.read()
        f_fetter_text.close()
    with open(os.path.join(TEXT_SOURCE, "fetter_story.txt"), "r", encoding="utf-8") as f_fetter_story_text:
        fetter_story_text = f_fetter_story_text.read()
        f_fetter_story_text.close()
    with open(os.path.join(STC_SOURCE, "skin_info.json"), "r", encoding="utf-8") as f_skin:
        skin_info = ujson.load(f_skin)
        f_skin.close()
    with open(os.path.join(TEXT_SOURCE, "skin.txt"), "r", encoding="utf-8") as f_skin_text:
        skin_text = f_skin_text.read()
        f_skin_text.close()
    with open(os.path.join(STC_SOURCE, "skin_class_info.json"), "r", encoding="utf-8") as f_skin_class:
        skin_class_info = ujson.load(f_skin_class)
        f_skin_class.close()
    with open(os.path.join(TEXT_SOURCE, "skin_class.txt"), "r", encoding="utf-8") as f_skin_class_text:
        skin_class_text = f_skin_class_text.read()
        f_skin_class_text.close()
    with open(os.path.join(STC_SOURCE, "npc_info.json"), "r", encoding="utf-8") as f_npc:
        npc_info = ujson.load(f_npc)
        f_npc.close()
    with open(os.path.join(TEXT_SOURCE, "npc.txt"), "r", encoding="utf-8") as f_npc_text:
        npc_text = f_npc_text.read()
        f_npc_text.close()
    with open(os.path.join(STC_SOURCE, "story_util_info.json"), "r", encoding="utf-8") as f_story:
        story_info = ujson.load(f_story)
        f_story.close()
    with open(os.path.join(TEXT_SOURCE, "story_util.txt"), "r", encoding="utf-8") as f_story_text:
        story_text = f_story_text.read()
        f_story_text.close()
    with open(os.path.join(STC_SOURCE, "mission_info.json"), "r", encoding="utf-8") as f_mission:
        mission_info = ujson.load(f_mission)
        f_mission.close()
    with open(os.path.join(TEXT_SOURCE, "mission.txt"), "r", encoding="utf-8") as f_mission_text:
        mission_text = f_mission_text.read()
        f_mission_text.close()

    pattern = {"memoir": "心智升级", "fetter": "格里芬往事", "skin": "笔记薄", "anniversary": "周年庆", "startavg": "初始剧情"}

    # 方针
    # scenario 一级分类 一个类型 例如：心智升级、格里芬往事、笔记薄、周年庆、初始剧情、主线剧情、支线剧情、联动剧情 ……
    # episode  二级分类 一个故事 例如：心智升级的人形、格里芬往事的标题、笔记薄的装扮主题名称、主线剧情活动的名称、支线剧情活动的名称、联动剧情活动的名称 ……
    # chapter  三级分类 一个章节 例如：主线剧情活动的章节、联动剧情活动的名称 ……

    title_dict = xlsx_to_dict()
    for avg in title_dict:
        if avg["name"]:
            continue

        if len(avg["path"].split("/")) > 1:
            if avg["path"].split("/")[1] in pattern.keys():
                avg["scenario"] = pattern[avg["path"].split("/")[1]]

            if avg["path"].split("/")[1] == "memoir":
                avg["name_b"] = f'P{avg["file"].split("_")[1]}'
                gun_id = avg["file"].split("_")[0]

                for gun in gun_info:
                    if gun["id"] == gun_id:
                        gun_name = stc_to_text(gun_text, gun["name"])
                        avg["episode"] = gun_name
                        avg["name"] = stc_to_text(gun_text, gun["name"]) + "Mod"
                        break

            if avg["path"].split("/")[1] == "anniversary":
                avg["name_a"] = f"No.{avg['file']}"

                for gun in gun_info:
                    if gun["id"] == avg["file"]:
                        avg["name"] = stc_to_text(gun_text, gun["name"])
                        break

                for npc in npc_info:
                    if npc["id"] == avg["file"]:
                        avg["name"] = stc_to_text(npc_text, npc["name"])
                        break

            if avg["path"].split("/")[1] == "fetter":
                fetter_id = avg["file"]

                for fetter_story in fetter_story_info:
                    if fetter_story["id"] == fetter_id:
                        avg["episode"] = stc_to_text(fetter_text, f"fetter-1000000{fetter_story['fetter_id']}")
                        avg["name"] = stc_to_text(fetter_story_text, fetter_story['name'])
                        break

            if avg["path"].split("/")[1] == "skin":
                skin_id = avg["file"]

                for skin in skin_info:
                    if skin_id == skin["id"]:
                        avg["name"] = stc_to_text(skin_text, skin['name'])

                        for skin_class in skin_class_info:
                            if skin_class['id'] == skin['class_id']:
                                avg["episode"] = stc_to_text(skin_class_text, skin_class['name'])

        elif avg["path"] == "avgtxt":
            for story in story_info:

                scripts = []
                for key in ["scripts", "start", "round", "point", "first", "mid", "end", "fail", "step_start_story", "step_end_story"]:
                    for story_single in story[key].split(","):
                        scripts.append(story_single.split(":")[-1:][0])

                for script in scripts:
                    if avg["file"] == script:
                        avg["sign"] = story["campaign"]
                        avg["scenario"] = INDEX[avg["sign"]][0]
                        avg["episode"] = INDEX[avg["sign"]][1]

                        # find mission name
                        for mission in mission_info:
                            if story["mission_id"] == mission["id"]:
                                avg["name"] = stc_to_text(mission_text, mission["name"])
                                break
                        break

                if avg["sign"]:
                    break

            if avg["sign"] and not avg["sign"].startswith("-"):
                if avg["file"].endswith("E"):
                    avg["chapter"] = "紧急"
                elif avg["file"].endswith("N"):
                    avg["chapter"] = "夜战"
                else:
                    avg["chapter"] = "普通"

                avg["name_b"] = "P" + avg["file"].split("-")[2][0]

        if avg["name"]:
            print(avg["scenario"], avg["episode"], avg["chapter"], avg["name_a"], avg["name"], avg["name_b"], avg["file"])

    save_xlsx(title_dict)


def save_xlsx(title_dict):
    with ExcelWriter(NAME) as writer:
        data = pd.DataFrame.from_dict(title_dict)
        data.to_excel(writer, sheet_name="avg", index=None)


def stc_to_text(text, name):
    tem = text[text.find(name) + len(name) + 1:]
    out_text = tem[:tem.find("\n")]
    return out_text


def mode_input():
    while True:
        mode = input("-- 请选择想要执行的程序：\n【1：更新剧情列表】【2：初始化全部信息】【3：初始化新增信息】【4：退出】：")
        if mode == "1":
            update_avg()
        elif mode == "2":
            initialize_with_pattern(True)
        elif mode == "3":
            initialize_with_pattern(None)
        elif mode == "4":
            break
        else:
            print("-- 未检测到对应模式，请重新输入")


mode_input()
