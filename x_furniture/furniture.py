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
    with open("./res/furniture_template.txt", "r", encoding="utf-8") as f_furniture_template:
        furniture_template = f_furniture_template.read()
        f_furniture_template.close()

    session = login_innbot()
    fur_type = {'101': '地面/地板', '102': '地面/地毯', '103': '地面/地毯',
                '201': '家具/装饰', '202': '家具/沙发', '203': '家具/床', '299': '家具/宠物',
                '301': '墙面/壁纸', '302': '墙面/挂饰', '303': '墙面/海报'}

    for furniture_class in furniture_class_info:
        # special 299-宠物, 300-海报, 301-小黑屋, 400-附属房间设施, 500-人形往事, 600-平凡的站牌
        if int(furniture_class['id']) in [300, 400]:
            continue
        if int(furniture_class['id']) != 19:
            continue

        fur_suit_name_tem = furniture_class_text[furniture_class_text.find(furniture_class["name"]) + len(furniture_class["name"]) + 1:]
        fur_suit_name = fur_suit_name_tem[:fur_suit_name_tem.find("\n")]

        try:
            origin_text = read_wiki(session, URL, f"家具/{fur_suit_name}")
        except:
            origin_text = ''

        page = furniture_template
        page = page.replace(f"|实装时间=\n", search_string(origin_text, '实装时间'))
        page = page.replace(f"|同期主题装扮名称=\n", search_string(origin_text, '同期主题装扮名称'))
        page = page.replace(f"|静态图片=\n", search_string(origin_text, '静态图片'))
        page = page.replace(f"|动态图片=\n", search_string(origin_text, '动态图片'))
        page = page.replace(f"|套装特效名称=\n", search_string(origin_text, '套装特效名称'))
        page = page.replace(f"|套装特效=\n", search_string(origin_text, '套装特效'))

        if origin_text.find("|套装特效2=") != -1:
            page = page.replace(f"|套装特效2=\n", search_string(origin_text, '套装特效2'))
        else:
            page = page.replace(f"|套装特效2=\n", "")

        des_text_tem = furniture_class_text[furniture_class_text.find(furniture_class["description"]) + len(furniture_class["description"]) + 1:]
        des_text = des_text_tem[:des_text_tem.find("\n")].replace("//n", "<br>").replace("//c", "，")

        page = page.replace("|家具套装名称=", f"|家具套装名称={fur_suit_name}")
        page = page.replace(f"|家具套装编号=", f"|家具套装编号={furniture_class['id']}")
        page = page.replace("|家具星级=", f"|家具星级={furniture_class['rank']}")
        page = page.replace("|套装说明=", f"|套装说明={des_text}")

        furniture_single_text = ''
        for furniture in furniture_info:
            if furniture['classes'] == furniture_class['id']:
                furniture_single_text += furniture_single(furniture, furniture_text, fur_type, interact_info)

        page = page.replace("|家具行=", f"|家具行={furniture_single_text}")

        write_wiki(session, URL, f"家具/{fur_suit_name}", page, '更新')
        # print(page)


def furniture_single(furniture, furniture_text, fur_type, interact_info):
    furniture_single_text = ''
    fur_name_tem = furniture_text[furniture_text.find(furniture["name"]) + len(furniture["name"]) + 1:]
    fur_name = fur_name_tem[:fur_name_tem.find("\n")]
    fur_des_tem = furniture_text[furniture_text.find(furniture["description"]) + len(furniture["description"]) + 1:]
    fur_des = fur_des_tem[:fur_des_tem.find("\n")].replace("//n", "<br>").replace("//c", "，")

    icon = furniture['code']
    if len(icon.split(',')) > 1:
        icon = icon.split(',')[0]
    icon = icon + "_icon.png"

    if fur_name.find("-") != -1:
        fur_name_b = fur_name[fur_name.find("-") + 1:]
    else:
        fur_name_b = fur_name

    furniture_single_text += "{{家具行信息2\n"
    furniture_single_text += f"|家具单独标准名称={fur_name}\n"
    furniture_single_text += f"|家具单独展示名称={fur_name_b}\n"
    furniture_single_text += f"|家具图片={icon}\n"
    furniture_single_text += f"|家具类型={fur_type[furniture['type']]}\n"

    if furniture['type'] in ['101', '301']:
        space_text = "N/A"
    else:
        space = furniture['space'].split(',')
        space_text = f"{space[0]}×{space[1]}"

    furniture_single_text += f"|家具占地={space_text}\n"
    furniture_single_text += f"|家具舒适={furniture['deco_rate']}\n"

    if furniture['interact_point'] != '0':
        furniture_single_text += f"|家具交互点个数={len(furniture['interact_point'].split(','))}\n"

        special_point_num = 0
        interact_point_text = ''
        for point in furniture['interact_point'].split(','):
            for interact in interact_info:
                if interact['id'] == point:
                    interact_point_text += interact['gun_action'] + ', '
                    if interact['gun_action'] not in ['sit', 'sleep', 'wait', 'pick', 'bird_sit']:
                        special_point_num += 1
                    break

        furniture_single_text += f"|家具特殊交互点个数={special_point_num}\n"
        furniture_single_text += f"|家具交互信息={interact_point_text[:-2]}\n"

    if furniture['furniture_bgm'] != '0':
        furniture_single_text += f"|家具BGM={furniture['furniture_bgm']}"

    furniture_single_text += f"|家具描述={fur_des}" + "}}\n"
    return furniture_single_text


def search_string(origin_text, tar):
    out_text = ""
    if origin_text.find(f'|{tar}=') > 0:
        obtain_1 = origin_text[origin_text.find(f'{tar}='):]
        if (obtain_1.find('|') < 0) or (obtain_1.find('\n') < obtain_1.find('|')):
            out_text += "|" + obtain_1[:obtain_1.find('\n')] + "\n"
        else:
            out_text += f"|{obtain_1[:obtain_1.find('|')]}\n"

    return out_text


def search_segment(origin_text):
    out_text = None
    if origin_text.find("{{") > 0:
        out_text = origin_text[origin_text.find("}}") + 2:]

    return out_text


furniture_write()