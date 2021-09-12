import os
import re
import sys
import math
import ujson
import requests

sys.path.append("..")
from wikibot import URL
from wikibot import read_wiki
from wikibot import write_wiki
from wikibot import login_innbot

STC_SOURCE = "..\\w_stc_data"
TEXT_SOURCE = "..\\w_text_data"
LUA_SOURCE = "..\\w_lua_data"


def interact_write():
    with open(os.path.join(STC_SOURCE, "furniture_info.json"), "r", encoding="utf-8") as f_furniture:
        furniture_info = ujson.load(f_furniture)
        f_furniture.close()
    with open(os.path.join(TEXT_SOURCE, "furniture.txt"), "r", encoding="utf-8") as f_furniture_text:
        furniture_text = f_furniture_text.read()
        f_furniture_text.close()

    with open(os.path.join(STC_SOURCE, "furniture_classes_info.json"), "r", encoding="utf-8") as f_furniture_class:
        furniture_class_info = ujson.load(f_furniture_class)
        f_furniture_class.close()
    with open(os.path.join(TEXT_SOURCE, "furniture_classes.txt"), "r", encoding="utf-8") as f_furniture_class_text:
        furniture_class_text = f_furniture_class_text.read()
        f_furniture_class_text.close()

    with open(os.path.join(STC_SOURCE, "furniture_interact_point_info.json"), "r", encoding="utf-8") as f_interact:
        interact_info = ujson.load(f_interact)
        f_interact.close()

    session = login_innbot()
    fur_type = {'101': '地面/地板', '102': '地面/地毯', '103': '地面/地毯',
                '201': '家具/装饰', '202': '家具/沙发', '203': '家具/床', '299': '家具/宠物',
                '301': '墙面/壁纸', '302': '墙面/挂饰', '303': '墙面/海报'}

    furniture_array = {}
    for furniture in furniture_info:
        fur_name_tem = furniture_text[furniture_text.find(furniture["name"]) + len(furniture["name"]) + 1:]
        fur_name = fur_name_tem[:fur_name_tem.find("\n")]

        interact_point_array = []
        interact_point_text = ''
        if furniture['interact_point'] != '0':
            for point in furniture['interact_point'].split(','):
                interact_point_array.append(point)

                for interact in interact_info:
                    if interact['id'] == point:
                        interact_point_text += interact['gun_action'] + ', '
                        break

            interact_point_text = interact_point_text[:-2]

        fur_suit_name = ''
        for furniture_class in furniture_class_info:
            if furniture['classes'] == furniture_class['id']:
                fur_suit_name_tem = furniture_class_text[furniture_class_text.find(furniture_class["name"]) + len(furniture_class["name"]) + 1:]
                fur_suit_name = fur_suit_name_tem[:fur_suit_name_tem.find("\n")]

        furniture_dict = {"id": furniture["id"], "name": fur_name, "class": fur_suit_name,
                          "type": fur_type[furniture['type']], "interact": interact_point_array, "interact_text": interact_point_text}
        furniture_array[furniture["id"]] = furniture_dict

    interact_json = {}
    for interact in interact_info:
        if interact['gun_action'] in ['sit', 'sleep', 'sleep,sit', 'wait', 'pick', 'bird_sit']:
            continue

        if interact['gun_action'] in interact_json.keys():
            interact_json[interact['gun_action']].append(interact['id'])
        else:
            interact_json[interact['gun_action']] = [interact['id']]

    page = ''
    for interact_name in interact_json:

        this_interact = "<h2 style='font-family: LinBiolinum;'>" + f"{interact_name}</h2>\n"
        this_interact += f"<table class='dollTable'>\n"

        for fid in furniture_array.keys():
            for interact_single in interact_json[interact_name]:
                if interact_single in furniture_array[fid]['interact']:
                    this_interact += "<tr><td width='200px'>"
                    this_interact += f"[[家具/{furniture_array[fid]['class']}#{furniture_array[fid]['name']}|{furniture_array[fid]['name']}]]"
                    this_interact += f"</td><td width='100px'>{furniture_array[fid]['type']}</td><td>{furniture_array[fid]['interact_text']}</td></tr>\n"
                    break

        this_interact += f"</table>\n"

        page += this_interact
    write_wiki(session, URL, f"家具特殊交互", page, '更新')
    # print(page)


interact_write()
