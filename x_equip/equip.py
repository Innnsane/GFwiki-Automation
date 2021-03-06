import os
import re
import sys
import ujson
import requests

sys.path.append("..")
from wikibot import URL
from wikibot import read_wiki
from wikibot import write_wiki
from wikibot import login_innbot

from equip_name import EQUIP_NAME

STC_SOURCE = "../w_stc_data"
TEXT_SOURCE = "../w_text_data"
EQUIP_SOURCE = "../x_equip"


def main():
    with open(os.path.join(STC_SOURCE, "equip_info.json"), "r", encoding="utf-8") as f_equip:
        equip_info = ujson.load(f_equip)
        f_equip.close()
    with open(os.path.join(TEXT_SOURCE, "equip.txt"), "r", encoding="utf-8") as f_equip_text:
        equip_text = f_equip_text.read()
        f_equip_text.close()

    with open(os.path.join(STC_SOURCE, "equip_category_info.json"), "r", encoding="utf-8") as f_equip_category:
        equip_category_info = ujson.load(f_equip_category)
        f_equip_category.close()
    with open(os.path.join(TEXT_SOURCE, "equip_category.txt"), "r", encoding="utf-8") as f_equip_category_text:
        equip_category_text = f_equip_category_text.read()
        f_equip_category_text.close()

    with open(os.path.join(STC_SOURCE, "equip_type_info.json"), "r", encoding="utf-8") as f_equip_type:
        equip_type_info = ujson.load(f_equip_type)
        f_equip_type.close()
    with open(os.path.join(TEXT_SOURCE, "equip_type.txt"), "r", encoding="utf-8") as f_equip_type_text:
        equip_type_text = f_equip_type_text.read()
        f_equip_type_text.close()

    with open(os.path.join(STC_SOURCE, "equip_group_info.json"), "r", encoding="utf-8") as f_equip_group:
        equip_group_info = ujson.load(f_equip_group)
        f_equip_group.close()
    with open(os.path.join(TEXT_SOURCE, "equip_group.txt"), "r", encoding="utf-8") as f_equip_group_text:
        equip_group_text = f_equip_group_text.read()
        f_equip_group_text.close()

    with open(os.path.join(STC_SOURCE, "recommended_formula_info.json"), "r", encoding="utf-8") as f_formula:
        formula_info = ujson.load(f_formula)
        f_formula.close()
    with open(os.path.join(TEXT_SOURCE, "recommended_formula.txt"), "r", encoding="utf-8") as f_formula_text:
        formula_text = f_formula_text.read()
        f_formula_text.close()
    with open(os.path.join(STC_SOURCE, "gun_info.json"), "r", encoding="utf-8") as f_gun:
        gun_info = ujson.load(f_gun)
        f_gun.close()
    with open(os.path.join(TEXT_SOURCE, "gun.txt"), "r", encoding="utf-8") as f_gun_text:
        gun_text = f_gun_text.read()
        f_gun_text.close()
    with open(os.path.join(STC_SOURCE, "battle_skill_config_info.json"), "r", encoding="utf-8") as f_skill:
        skill_info = ujson.load(f_skill)
        f_skill.close()
    with open(os.path.join(TEXT_SOURCE, "battle_skill_config.txt"), "r", encoding="utf-8") as f_skin_text:
        skill_text = f_skin_text.read()
        f_skin_text.close()

    session = login_innbot()

    EQUIP_ATTR = {"pow": "??????", "hit": "??????", "dodge": "??????", "speed": "??????", "rate": "??????", "critical_harm_rate": "????????????",
                  "critical_percent": "????????????", "armor_piercing": "??????", "armor": "??????", "night_view_percent": "????????????", "bullet_number_up": "??????"}

    for equip in equip_info:
        # if not equip['fit_guns']:
        #    continue

        if int(equip['id']) <= 252:
            continue

        if int(equip['id']) > 500:
            continue

        eq_name_tem = equip_text[equip_text.find(equip["name"]) + len("equip-10000001,"):]
        eq_name = eq_name_tem[:eq_name_tem.find("\n")]

        # some equip has different name with page
        page_name = eq_name
        if equip['id'] in EQUIP_NAME.keys():
            page_name = EQUIP_NAME[equip['id']]

        text = "{{????????????\n"
        eq_intro_tem = equip_text[equip_text.find(equip["equip_introduction"]) + len("equip-30000001,"):]
        eq_intro = eq_intro_tem[:eq_intro_tem.find("\n")]

        # if there is no introduction means not in the game
        if not eq_intro:
            continue

        try:
            origin_text = read_wiki(session, URL, page_name)
        except:
            origin_text = ""

        eid = int(equip['id'])
        if eid < 100:
            eid = "00" + str(eid)
        elif eid < 1000:
            eid = "0" + str(eid)

        text += f"|??????={eid}\n|??????={equip['rank']}\n|??????={eq_name}\n|??????={equip['code']}.png\n"

        for category in equip_category_info:
            if equip['category'] == category["category"]:
                text += f"|??????1={stc_to_text(equip_category_text, category['name'])}"
                text += f"|??????1??????={stc_to_text(equip_category_text, category['en_name'])}"
                text += f"|??????1??????={category['code']}\n"

        for eq_type in equip_type_info:
            if equip['type'] == eq_type["type"]:
                text += f"|??????2={stc_to_text(equip_type_text, eq_type['name'])}"
                text += f"|??????2??????={eq_type['code']}"

                eq_type_des = stc_to_text(equip_type_text, eq_type['des']).replace("</color>", "}}")
                eq_type_des = eq_type_des.replace("<color=", "{{Color|").replace(">", "|")
                text += f"|??????2??????={eq_type_des}\n\n"

        if equip['fit_guns']:
            text += doll_handle(gun_info, gun_text, equip['fit_guns'])
        text += f"|??????={eq_intro}\n\n"

        if int(equip['max_level']) == 0:
            text += "|????????????=0\n"
        else:
            text += "|????????????=1\n"

        if int(equip['skill']) != 0 or int(equip['passive_skill']) != 0:
            text += "|????????????=1\n"

        count = 1
        equip_mul = {}
        if equip['bonus_type']:
            equip_mul = bonus_handle(equip['bonus_type'])
        for key in EQUIP_ATTR.keys():
            if not equip[key]:
                continue
            text += f"|??????{count}??????={EQUIP_ATTR[key]}"
            text += f"|??????{count}min={equip[key].split(',')[0]}"
            text += f"|??????{count}max={equip[key].split(',')[1]}"
            if key in equip_mul.keys():
                text += f"|??????{count}??????={equip_mul[key]}\n"
            else:
                text += f"|??????{count}??????=1.0\n"
                equip_mul[key] = '1'
            count += 1

        # final attribute calculate for smw
        for key in EQUIP_ATTR.keys():
            if equip[key]:
                text += f"|{EQUIP_ATTR[key]}={int(float(equip[key].split(',')[1]) * float(equip_mul[key]))}\n"
        text += "\n"

        # four resources related
        text += f"|??????={int(float(equip['powerup_mp']) * 10000 * int(equip['exclusive_rate']))}"
        text += f"|??????={int(float(equip['powerup_ammo']) * 10000 * int(equip['exclusive_rate']))}"
        text += f"|??????={int(float(equip['powerup_mre']) * 10000 * int(equip['exclusive_rate']))}"
        text += f"|??????={int(float(equip['powerup_part']) * 10000 * int(equip['exclusive_rate']))}\n"
        text += f"|????????????={equip['retire_mp']}|????????????={equip['retire_ammo']}"
        text += f"|????????????={equip['retire_mre']}|????????????={equip['retire_part']}\n\n"

        if int(equip['equip_group_id']) != 0:
            for group in equip_group_info:
                if group['id'] == equip['equip_group_id']:
                    eqg_name_tem = equip_group_text[equip_group_text.find(group["name"]) + len("equip_group-10000001,"):]
                    eqg_name = eqg_name_tem[:eqg_name_tem.find("\n")]
                    eqg_des_tem = equip_group_text[equip_group_text.find(group["des"]) + len("equip_group-20000001,"):]
                    eqg_des = eqg_des_tem[:eqg_des_tem.find("\n")].replace("//c", "???")
                    text += f"|????????????={eqg_name}\n|??????????????????={group['code']}\n|??????????????????={eqg_des}\n"
                    text += group_equip_handle(equip_text, equip_info, group['equip_unit']) + "\n"
                    text += group_skill_handle(skill_text, skill_info, group['group_skill']) + "\n"
                    break

        # recommend formula
        if not equip['fit_guns']:
            for formula in formula_info:
                if int(formula['develop_type']) == 3 and formula['type'] == equip['type']:
                    formula_name_tem = formula_text[formula_text.find(formula["name"]) + len("recommended_formula-10000040,"):]
                    formula_name = formula_name_tem[:formula_name_tem.find("\n")]
                    text += f"|????????????????????????={formula_name}" \
                            f"|????????????????????????=??????<span>{formula['mp']}</span>?????????<span>{formula['ammo']}</span>?????????<span>{formula['mre']}</span>?????????<span>{formula['part']}</span>\n"
                elif int(formula['develop_type']) == 4 and formula['type'] == equip['type']:
                    formula_name_tem = formula_text[formula_text.find(formula["name"]) + len("recommended_formula-10000040,"):]
                    formula_name = formula_name_tem[:formula_name_tem.find("\n")]
                    text += f"|????????????????????????={formula_name}" \
                            f"|????????????????????????=??????<span>{formula['mp']}</span>?????????<span>{formula['ammo']}</span>?????????<span>{formula['mre']}</span>?????????<span>{formula['part']}</span>\n"

        text += f"|????????????={develop_time(equip['develop_duration'])}\n"
        if origin_text.find('|????????????=') > 0:
            obtain_1 = origin_text[origin_text.find('????????????='):]
            if (obtain_1.find('|') < 0) or (obtain_1.find('\n') < obtain_1.find('|')):
                text += "|" + obtain_1[:obtain_1.find('\n')] + "\n"
            else:
                text += f"|{obtain_1[:obtain_1.find('|')]}\n"

        if origin_text.find('|??????=') > 0:
            obtain_1 = origin_text[origin_text.find('??????='):]
            if (obtain_1.find('|') < 0) or (obtain_1.find('\n') < obtain_1.find('|')):
                text += "|" + obtain_1[:obtain_1.find('\n')] + "\n"
            else:
                text += f"|{obtain_1[:obtain_1.find('|')]}\n"

        eq_des_tem = equip_text[equip_text.find(equip["description"]) + len("equip-20000001,"):]
        eq_des = eq_des_tem[:eq_des_tem.find("\n")]
        for key in EQUIP_ATTR.keys():
            if eq_des.find(f"<{key}>") > 0:
                eq_des = eq_des.replace(f"<{key}>", str(int(float(equip[key].split(',')[1]) * float(equip_mul[key]))))

        pattern_1 = re.compile(r'(//n)?\$')
        attr_des = re.sub(pattern_1, '$', eq_des)
        attr_des_a = attr_des[:attr_des.find('$')].replace('//n', ' ')
        attr_des_b = attr_des[attr_des.find('$'):].replace('//c', '???')

        count_ret = 0
        pattern_2 = re.compile(r'[-+0-9]{1,5}%?')
        ret_des = re.findall(pattern_2, attr_des_a)
        num_string = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
        for num in ret_des:
            attr_des_a = attr_des_a.replace(num, f"<span><ret_{num_string[count_ret]}></span>", 1)
            count_ret += 1
        count_ret_2 = 0
        while count_ret_2 < len(ret_des):
            attr_des_a = attr_des_a.replace(f"<ret_{num_string[count_ret_2]}>", ret_des[count_ret_2])
            count_ret_2 += 1
        text += f"\n|????????????1={attr_des_a} {attr_des_b[1:]}"

        eq_attr_des_2 = attr_des[:attr_des.find('$')].replace(' ', '<br>').replace('//n', '<br>')
        if eq_attr_des_2.find("??????") != -1 and eq_attr_des_2.find("<br>??????") == -1:
            eq_attr_des_2 = eq_attr_des_2.replace("??????", "<br>??????")
        text += f"\n|????????????2={eq_attr_des_2}\n"

        if page_name != eq_name:
            text += f"|????????????=1\n"

        # end
        text += "}}\n"

        if equip['fit_guns']:
            text += "{{??????????????????}}"

        # print(text)
        write_wiki(session, URL, page_name, text, "update")


def stc_to_text(text, name):
    tem = text[text.find(name) + len(name) + 1:]
    out_text = tem[:tem.find("\n")]
    return out_text


def doll_handle(gun_info, gun_text, strings):
    gun_type = ["None", "HG", "SMG", "RF", "AR", "MG", "SG"]

    count = 1
    text_str = ""
    gun_arr = strings.split(',')
    for gun_id in gun_arr:
        if int(gun_id) > 20000:
            continue

        for gun in gun_info:
            if gun['id'] == gun_id:
                cn_name_tem = gun_text[gun_text.find(gun["name"]) + len("gun-10000001,"):]
                cn_name = cn_name_tem[:cn_name_tem.find("\n")]
                if cn_name.endswith(" "):
                    cn_name = cn_name[:-1]
                text_str += f"|????????????{count}={cn_name}|????????????{count}??????={gun_type[int(gun['type'])]}"

                if int(gun['id']) >= 1000:
                    text_str += f"|????????????{count}??????={1}"
                else:
                    text_str += f"|????????????{count}??????={gun['rank']}\n"

                break
        count += 1

    return text_str


def bonus_handle(string):
    dict1 = {}
    attr1 = string.split(',')
    for key in attr1:
        type1 = key.split(':')[0]
        numb1 = key.split(':')[1]
        dict1[type1] = str(1 + int(numb1) / 1000)
    return dict1


def group_equip_handle(text, info, strings):
    out = ""
    count = 1
    arr = strings.split(',')
    for equip_id in arr:
        for equip in info:
            if equip['id'] == equip_id:
                eq_name_tem = text[text.find(equip["name"]) + len("equip-10000001,"):]
                eq_name = eq_name_tem[:eq_name_tem.find("\n")]
                out += f"|??????????????????{count}??????={eq_name}|??????????????????{count}??????={equip['rank']}\n"
                break

        count += 1
    return out


def group_skill_handle(text, info, strings):
    out = ""
    count = 1
    arr = strings.split(',')
    for skill_bundle in arr:
        skill_id = str(skill_bundle.split(':')[1]) + "01"
        for skill in info:
            if skill['id'] == skill_id:
                skill_tem = text[text.find(skill["description"]) + len("battle_skill_config-199205001,"):]
                skill_text = skill_tem[:skill_tem.find("\n")].replace("//c", "???").replace(";", "???").replace(",", "???")
                out += f"|??????????????????{skill_bundle.split(':')[0]}={skill_text}\n"

        count += 1
    return out


def develop_time(number):
    number = int(number)
    hour = int(number / 3600)
    minute = int((number - hour*3600) / 60)
    second = number - hour*3600 - minute*60

    text = f""
    if hour < 10:
        text += f"0{hour}:"
    else:
        text += f"{hour}:"

    if minute < 10:
        text += f"0{minute}:"
    else:
        text += f"{minute}:"

    if second < 10:
        text += f"0{second}"
    else:
        text += f"{second}"

    return text


main()
