import os
import re
import sys
import time
import ujson

SAVE = "./save.json"
SRC = "./announcement"
STC_SOURCE = "../w_stc_data"
TEXT_SOURCE = "../w_text_data"
key_name_dict = {}

from doll_name_change import LIST
sys.path.append("..")
from wikibot import URL
from wikibot import read_wiki
from wikibot import write_wiki
from wikibot import login_innbot
sys.path.append("../x_avg")
from avg_index import INDEX


def sort():
    li = re.compile(r'[0-9]{1,2}[、\.]')

    for file in os.listdir(SRC):
        print(file)
        with open(os.path.join(SRC, file), "r", encoding='utf-8') as f:
            announcement = ujson.load(f)
        text = text_manager(announcement['Content'])
        if text.find("1.") == -1:
            continue

        num = 0
        text_list = []
        text_tem = text
        line = re.findall(li, text)
        while num < len(line):
            if num < len(line) - 1:
                this_text = text_tem[text_tem.find(line[num]):text_tem.find(line[num + 1])]
                text_tem = text_tem[text_tem.find(line[num]) + 1:]
            else:
                this_text = text_tem[text_tem.find(line[num]):text_tem.find("\n\n")]
            text_list.append(this_text.replace("\n\n", "\n"))
            print(this_text.replace("\n\n", "\n"))
            num += 1

        time.sleep(2)


def text_manager(text):
    color = re.compile("<span style=\"color:#[a-zA-Z0-9]{6}\">")
    text = re.sub(color, "", text)
    text = text.replace("<br />", "<br/>").replace(r"<div>", "").replace(r"</span>", "").replace(r"</div>", "").replace("<br/>", "\n")
    return text


def text_manager_2(text):
    font = re.compile("font-size:1[2-6]px")
    text = re.sub(font, "font-size:14px", text)
    text = text.replace("\n", "")

    for key in key_name_dict.keys():
        text = text.replace(key, key_name_dict[key])

    return text


def write_announcement():
    session = login_innbot()
    with open(SAVE, "r", encoding='utf-8') as f:
        site_list = ujson.load(f)

    num = 0
    file_date_list = {}
    while num < len(site_list):
        file_name = f"{str(site_list[num]['Id'])}_{site_list[num]['Title'].replace(':', '')}.txt"
        print(file_name)
        with open(os.path.join(SRC, file_name), "r", encoding='utf-8') as f:
            site = ujson.load(f)

        # head
        this_date = date_manager(site_list[num]['Date'])
        page = "{{" + f"更新记录|年={this_date['year']}|月={this_date['month']}|日={this_date['day']}\n"

        if num > 0:
            last_date = date_manager(site_list[num - 1]['Date'])
            page += f"|下次更新日期={last_date['year']}年{int(last_date['month'])}月{int(last_date['day'])}日"
            page += "|下次更新标题={{更新维护链接" + f"|{site_list[num - 1]['Title']}"
            page += f"|{last_date['year']}|{last_date['month']}|{last_date['day']}"
            last_date_text = site_list[num - 1]['Date'].split(" ")[0]
            if file_date_list[last_date_text] == 1:
                page += "}}\n"
            else:
                page += "|" + str(file_date_list[site_list[num - 1]['Date'].split(" ")[0]]) + "}}\n"

        date_text_2 = site_list[num]['Date'].split(" ")[0]
        if date_text_2 not in file_date_list.keys():
            file_date_list[date_text_2] = 1
            date_text = f"{this_date['year']}{this_date['month']}{this_date['day']}"
        else:
            file_date_list[date_text_2] += 1
            date_text = f"{this_date['year']}{this_date['month']}{this_date['day']}_{file_date_list[date_text_2]}"

        if num < len(site_list) - 1:
            next_date = date_manager(site_list[num + 1]['Date'])
            page += f"|上次更新日期={next_date['year']}年{int(next_date['month'])}月{int(next_date['day'])}日"
            page += "|上次更新标题={{更新维护链接" + f"|{site_list[num + 1]['Title']}"
            page += f"|{next_date['year']}|{next_date['month']}|{next_date['day']}"
            if site_list[num + 1]['Date'].split(" ")[0] in file_date_list.keys():
                page += "|" + str(file_date_list[site_list[num + 1]['Date'].split(" ")[0]] + 1) + "}}}}\n"
            else:
                page += "}}}}\n"

        # content
        page += f"<div class=\"announcementDiv\"><div class=\"announcementTitle\">{site['Title']}</div>"
        page += f"<div class=\"announcementContent\">{text_manager_2(site['Content'])}</div>"
        page += f"<div class=\"announcementSource\">信息来源：[https://gf-cn.sunborngame.com/NewsInfo?id={site['Id']} {site['Title']}]" \
                f"<span class=\"announcementDate\">{site['Date']}</span></div></div>"

        num += 1

        # print(date_text, page)
        write_wiki(session, URL, f"更新维护记录/{date_text}", page, '更新')
        # time.sleep(2)


def get_key_name_dict():
    with open(os.path.join(STC_SOURCE, "gun_info.json"), "r", encoding="utf-8") as f_gun:
        gun_info = ujson.load(f_gun)
        f_gun.close()
    with open(os.path.join(TEXT_SOURCE, "gun.txt"), "r", encoding="utf-8") as f_gun_text:
        gun_text = f_gun_text.read()
        f_gun_text.close()

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

    with open(os.path.join(STC_SOURCE, "equip_info.json"), "r", encoding="utf-8") as f_equip:
        equip_info = ujson.load(f_equip)
        f_equip.close()
    with open(os.path.join(TEXT_SOURCE, "equip.txt"), "r", encoding="utf-8") as f_equip_text:
        equip_text = f_equip_text.read()
        f_equip_text.close()

    with open(os.path.join(STC_SOURCE, "fairy_info.json"), "r", encoding="utf-8") as f_fairy:
        fairy_info = ujson.load(f_fairy)
        f_fairy.close()
    with open(os.path.join(TEXT_SOURCE, "fairy.txt"), "r", encoding="utf-8") as f_fairy_text:
        fairy_text = f_fairy_text.read()
        f_fairy_text.close()
    with open(os.path.join(STC_SOURCE, "squad_info.json"), "r", encoding="utf-8") as f_squad:
        squad_info = ujson.load(f_squad)
        f_squad.close()
    with open(os.path.join(TEXT_SOURCE, "squad.txt"), "r", encoding="utf-8") as f_squad_text:
        squad_text = f_squad_text.read()
        f_squad_text.close()
    with open(os.path.join(STC_SOURCE, "sangvis_info.json"), "r", encoding="utf-8") as f_sangvis:
        sangvis_info = ujson.load(f_sangvis)
        f_sangvis.close()
    with open(os.path.join(TEXT_SOURCE, "sangvis.txt"), "r", encoding="utf-8") as f_sangvis_text:
        sangvis_text = f_sangvis_text.read()
        f_sangvis_text.close()
    with open(os.path.join(STC_SOURCE, "enemy_illustration_info.json"), "r", encoding="utf-8") as f_enemy_illustration:
        enemy_illustration_info = ujson.load(f_enemy_illustration)
        f_enemy_illustration.close()
    with open(os.path.join(TEXT_SOURCE, "enemy_illustration.txt"), "r", encoding="utf-8") as f_enemy_illustration_text:
        enemy_illustration_text = f_enemy_illustration_text.read()
        f_enemy_illustration_text.close()

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

    gun_name_dict = {}
    for gun in gun_info:
        gun_name = stc_to_text(gun_text, gun['name']).replace("\xa0", " ")
        key_name_dict[f"&ldquo;{gun_name}&rdquo;"] = f"&ldquo;[[{gun_name}]]&rdquo;"
        key_name_dict[f"“{gun_name}”"] = f"“[[{gun_name}]]”"
        key_name_dict[f"：{gun_name}<"] = f"：[[{gun_name}]]<"
        gun_name_dict[gun["id"]] = gun_name

        # the doll who had changed her name
        for name in LIST.keys():
            key_name_dict[f"&ldquo;{name}&rdquo;"] = f"&ldquo;[[{name}]]&rdquo;"
            key_name_dict[f"“{name}”"] = f"“[[{name}]]”"
            key_name_dict[f"：{name}<"] = f"：[[{name}]]<"

    for skin in skin_info:
        gun_name = ""
        skin_name = stc_to_text(skin_text, skin['name']).replace("\xa0", " ")
        for gun_id in gun_name_dict.keys():
            if gun_id == skin["fit_gun"]:
                gun_name = gun_name_dict[gun_id]
        key_name_dict[f"{skin_name}"] = f"[[{gun_name}#{skin_name.replace(gun_name + '-', '')}|{skin_name}]]"

        # the doll who had changed her name
        for name in LIST.keys():
            if LIST[name] == gun_name:
                old_skin_name = skin_name.replace(LIST[name], name)
                key_name_dict[f"{old_skin_name}"] = f"[[{gun_name}#{skin_name.replace(gun_name + '-', '')}|{old_skin_name}]]"

    for skin_class in skin_class_info:
        skin_class_name = stc_to_text(skin_class_text, skin_class['name'])
        key_name_dict[f"&ldquo;{skin_class_name}&rdquo;"] = f"&ldquo;[[{skin_class_name}]]&rdquo;"
        key_name_dict[f"“{skin_class_name}”"] = f"“[[{skin_class_name}]]”"

    for equip in equip_info:
        equip_name = stc_to_text(equip_text, equip['name'])
        key_name_dict[f"&ldquo;{equip_name}&rdquo;"] = f"&ldquo;[[{equip_name}]]&rdquo;"
        key_name_dict[f"“{equip_name}”"] = f"“[[{equip_name}]]”"

    furniture_class_name_dict = {}
    for furniture_class in furniture_class_info:
        furniture_class_name = stc_to_text(furniture_class_text, furniture_class['name'])
        key_name_dict[f"&ldquo;{furniture_class_name}&rdquo;"] = f"&ldquo;[[家具/{furniture_class_name}|{furniture_class_name}]]&rdquo;"
        key_name_dict[f"“{furniture_class_name}”"] = f"“[[家具/{furniture_class_name}|{furniture_class_name}]]”"
        key_name_dict[f"【{furniture_class_name}】"] = f"【[[家具/{furniture_class_name}|{furniture_class_name}]]】"
        furniture_class_name_dict[furniture_class['id']] = furniture_class_name

    for furniture in furniture_info:
        furniture_class_name = ""
        for furniture_class_id in furniture_class_name_dict.keys():
            if furniture['classes'] == furniture_class_id:
                furniture_class_name = furniture_class_name_dict[furniture_class_id]
        furniture_name = stc_to_text(furniture_text, furniture['name'])
        key_name_dict[f"&ldquo;{furniture_name}&rdquo;"] = f"&ldquo;[[家具/{furniture_class_name}#{furniture_name}|{furniture_name}]]&rdquo;"

    for fairy in fairy_info:
        fairy_name = stc_to_text(fairy_text, fairy['name'])
        key_name_dict[f"{fairy_name}"] = f"[[{fairy_name}]]"

    for squad in squad_info:
        squad_name = stc_to_text(squad_text, squad['name'])
        key_name_dict[f"&ldquo;{squad_name}&rdquo;"] = f"&ldquo;[[{squad_name}]]&rdquo;"
        key_name_dict[f"“{squad_name}”"] = f"“[[{squad_name}]]”"

    for sangvis in sangvis_info:
        sangvis_name = stc_to_text(sangvis_text, sangvis['name'])
        key_name_dict[f"&ldquo;{sangvis_name}&rdquo;"] = f"&ldquo;[[{sangvis_name}]]&rdquo;"
        key_name_dict[f"“{sangvis_name}”"] = f"“[[{sangvis_name}]]”"

    for enemy_illustration in enemy_illustration_info:
        enemy_name = stc_to_text(enemy_illustration_text, enemy_illustration['name'])
        key_name_dict[f"&ldquo;{enemy_name}&rdquo;"] = f"&ldquo;[[{enemy_name}]]&rdquo;"
        key_name_dict[f"“{enemy_name}”"] = f"“[[{enemy_name}]]”"

    for key in INDEX.keys():
        key_name_dict[f"&ldquo;{INDEX[key][1].split(' ')[-1]}&rdquo;"] = f"&ldquo;[[{INDEX[key][1].split(' ')[-1]}]]&rdquo;"
        key_name_dict[f"“{INDEX[key][1].split(' ')[-1]}”"] = f"“[[{INDEX[key][1].split(' ')[-1]}]]”"

    key_name_dict["情报中心"] = "[[情报中心]]"
    key_name_dict["格纳库"] = "[[格纳库]]"
    key_name_dict["战区攻略"] = "[[战区攻略系统|战区攻略]]"
    key_name_dict["前进营地"] = "[[前进营地]]"
    key_name_dict["拉弗伯雷兵棋"] = "[[拉弗伯雷兵棋]]"
    key_name_dict["咖啡厅"] = "[[咖啡厅]]"
    key_name_dict["靶机专训"] = "[[靶机专训]]"
    key_name_dict["格里芬往事"] = "[[格里芬往事]]"
    # print(key_name_dict)


def date_manager(date):
    date_date = date.split(" ")[0].split("-")
    date_time = date.split(" ")[1].split(":")
    out = {'year': date_date[0], 'month': date_date[1], 'day': date_date[2],
           'hour': date_time[0], 'minute': date_time[1], 'second': date_time[2]}
    return out


def stc_to_text(text, name):
    tem = text[text.find(name) + len(name) + 1:]
    out_text = tem[:tem.find("\n")]
    return out_text


if __name__ == "__main__":
    get_key_name_dict()
    write_announcement()

