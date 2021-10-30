import os
import sys
import ujson
import requests

sys.path.append("..")
from wikibot import URL
from wikibot import read_wiki
from wikibot import write_wiki
from wikibot import login_innbot

STC_SOURCE = "../w_stc_data"
TEXT_SOURCE = "../w_text_data"
LUA_SOURCE = "../w_lua_data"


def furniture_write():
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

    dom_text_all = ""
    for furniture_class in furniture_class_info:
        # special 299-宠物, 300-海报, 301-小黑屋, 400-附属房间设施, 500-人形往事, 600-平凡的站牌
        if int(furniture_class['id']) in [301, 400]:
            continue
        fur_name = stc_to_text(furniture_class_text, furniture_class['name'])
        dom_text_all += f"<div class='furnitureClassData' data-class-name='{fur_name}' data-class-id='{furniture_class['id']}'></div>"

    for furniture in furniture_info:
        dom_text = ""

        fur_name = stc_to_text(furniture_text, furniture['name'])
        fur_des = stc_to_text(furniture_text, furniture['description'])

        icon = furniture['code']
        if len(icon.split(',')) > 1:
            icon = icon.split(',')[0]
        fur_icon = icon + "_icon.png"

        dom_text += f"<div class='furnitureData' data-name='{fur_name}' data-des='{fur_des}' data-icon='{fur_icon}' "
        dom_text += f"data-type='{fur_type[furniture['type']]}' data-favor='{furniture['deco_rate']}' "
        dom_text += f"data-width='{furniture['space'].split(',')[0]}' data-height='{furniture['space'].split(',')[1]}' "

        if furniture['interact_point'] != '0':
            dom_text += f"data-interact='{len(furniture['interact_point'].split(','))}' "

            special_point_num = 0
            for point in furniture['interact_point'].split(','):
                for interact in interact_info:
                    if interact['id'] == point:
                        if interact['gun_action'] not in ['sit', 'sleep', 'wait', 'pick', 'bird_sit', 'sleep,sit']:
                            special_point_num += 1
                        break

            dom_text += f"data-interact-special='{special_point_num}' "
        else:
            dom_text += f"data-interact='0' data-interact-special='0' "


        if furniture['furniture_bgm'] not in ['', '0']:
            dom_text += f"data-bgm='{furniture['furniture_bgm']}' "

        for furniture_class in furniture_class_info:
            if furniture['classes'] == furniture_class['id']:
                dom_text += f"data-class='{stc_to_text(furniture_class_text, furniture_class['name'])}' data-class-id='{furniture_class['id']}'"
                break

        dom_text += "></div>"
        dom_text_all += dom_text

    print(dom_text_all)
    write_wiki(session, URL, f"模板:FurnitureQueryData", dom_text_all, '更新')


def stc_to_text(text, name):
    tem = text[text.find(name) + len(name) + 1:]
    out_text = tem[:tem.find("\n")]
    return out_text


furniture_write()
