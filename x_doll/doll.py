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
from wikibot import xlsx_dict
from wikibot import login_innbot

sys.path.append("../x_equip")
from equip_name import EQUIP_NAME

from cloud import CLOUD
from design import DESIGN
from doll_attr import calculate
from doll_effect import doll_effect
from collaboration import COLLABORATION
from doll_skill import skill_description

STC_SOURCE = "../w_stc_data"
TEXT_SOURCE = "../w_text_data"
LUA_SOURCE = "../w_lua_data"
OBTAIN_SOURCE = "../x_skin/obtain/obtain.xlsx"


def doll_file():
    with open(os.path.join(STC_SOURCE, "gun_info.json"), "r", encoding="utf-8") as f_gun:
        gun_info = ujson.load(f_gun)
        f_gun.close()
    with open(os.path.join(TEXT_SOURCE, "gun.txt"), "r", encoding="utf-8") as f_gun_text:
        gun_text = f_gun_text.read()
        f_gun_text.close()

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
    with open(os.path.join(STC_SOURCE, "skin_group_info.json"), "r", encoding="utf-8") as f_skin_group:
        skin_group_info = ujson.load(f_skin_group)
        f_skin_group.close()
    with open(os.path.join(TEXT_SOURCE, "skin_group.txt"), "r", encoding="utf-8") as f_skin_group_text:
        skin_group_text = f_skin_group_text.read()
        f_skin_group_text.close()
    with open(os.path.join(STC_SOURCE, "live2d_info.json"), "r", encoding="utf-8") as f_live2d:
        live2d_info = ujson.load(f_live2d)
        f_live2d.close()

    with open(os.path.join(STC_SOURCE, "battle_skill_config_info.json"), "r", encoding="utf-8") as f_skill:
        skill_info = ujson.load(f_skill)
        f_skill.close()
    with open(os.path.join(TEXT_SOURCE, "battle_skill_config.txt"), "r", encoding="utf-8") as f_skin_text:
        skill_text = f_skin_text.read()
        f_skin_text.close()
    with open(os.path.join(STC_SOURCE, "fetter_skill_info.json"), "r", encoding="utf-8") as f_fetter_skill:
        fetter_skill_info = ujson.load(f_fetter_skill)
        f_fetter_skill.close()
    with open(os.path.join(TEXT_SOURCE, "fetter_skill.txt"), "r", encoding="utf-8") as f_fetter_skill_text:
        fetter_skill_text = f_fetter_skill_text.read()
        f_fetter_skill_text.close()
    with open(os.path.join(TEXT_SOURCE, "organization.txt"), "r", encoding="utf-8") as f_org_text:
        org_text = f_org_text.read()
        f_org_text.close()

    with open(os.path.join(STC_SOURCE, "gun_obtain_info.json"), "r", encoding="utf-8") as f_gun_obtain:
        gun_obtain_info = ujson.load(f_gun_obtain)
        f_gun_obtain.close()
    with open(os.path.join(TEXT_SOURCE, "gun_obtain.txt"), "r", encoding="utf-8") as f_gun_obtain_text:
        gun_obtain_text = f_gun_obtain_text.read()
        f_gun_obtain_text.close()

    with open(os.path.join(LUA_SOURCE, "NewCharacterVoice.txt"), "r", encoding="utf-8") as f_voice_text:
        voice_text = f_voice_text.read()
        f_voice_text.close()

    session = login_innbot()
    skin_obtain_info = xlsx_dict(OBTAIN_SOURCE)

    gun_type = ["None", "HG", "SMG", "RF", "AR", "MG", "SG"]
    skin_obtain = {"gem": "??????", "coin": "??????", "event": "??????", "rmb": "RMB"}

    for gun in gun_info:
        if int(gun["id"]) > 1200:
            break

        if int(gun["id"]) <= 0:
            continue

        # if int(gun["id"]) not in [1032]:
        #     continue

        cn_name_tem = gun_text[gun_text.find(gun["name"]) + len("gun-10000001,"):]
        cn_name = cn_name_tem[:cn_name_tem.find("\n")]
        if cn_name.endswith(" "):
            cn_name = cn_name[:-1]

        try:
            origin_text = read_wiki(session, URL, cn_name)
        except:
            origin_text = ''

        page = "{{" + f"??????????????????3\n|????????????={cn_name}|code={gun['code']}\n" \
                      f"|????????????={gun['launch_time'].replace(' 00:00:00', '')}\n" \
                      f"|????????????={develop_time(gun['develop_duration'])}\n" \
                      f"{gain_handle(gun['obtain_ids'], gun_obtain_info, gun_obtain_text)}\n"

        if 1000 <= int(gun['id']) < 1500:
            page += f"|??????=1"
        else:
            page += f"|??????={gun['rank']}"
        page += f"|??????={gun['id']}|??????={gun_type[int(gun['type'])]}\n"

        extra_tem = gun_text[gun_text.find(gun["extra"]) + len("gun-40000001,"):]
        extra_text = extra_tem[:extra_tem.find("\n")]
        if extra_text.split('//c')[1] != "":
            page += f"|CV={extra_text.split('//c')[1]}"
        page += f"|??????={extra_text.split('//c')[0]}\n\n"

        if gun['explore_tag']:
            tag_number = 1
            for tag in gun['explore_tag'].split(","):
                page += f"|????????????{tag_number}={tag}"
                tag_number += 1
            page += "\n"

        page += organization_handle(gun['org_id'], org_text)
        page += f"|????????????={gun['baseammo']}|????????????={gun['basemre']}|????????????={gun['ammo_add_withnumber']}|????????????={gun['mre_add_withnumber']}\n"
        page += f"|????????????={gun['retiremp']}|????????????={gun['retireammo']}|????????????={gun['retiremre']}|????????????={gun['retirepart']}\n\n"

        gun_update = None
        if gun['mindupdate_consume']:
            for gun_up in gun_info:
                if int(gun_up['id']) == int(gun["id"]) + 20000:
                    gun_update = gun_up

            page += f"|MOD??????={gun_update['rank']}\n"
            for live2D in live2d_info:
                if int(live2D["skin"]) == 0 and live2D["fit_gun"] == gun_update["id"]:
                    page += f"|MOD????????????={live2D['skinType']}"

            extra_tem = gun_text[gun_text.find(gun_update["extra"]) + len("gun-40000001,"):]
            extra_text = extra_tem[:extra_tem.find("\n")]
            if extra_text.split('//c')[1] != "":
                page += f"|MODCV={extra_text.split('//c')[1]}"
            page += f"|MOD??????={extra_text.split('//c')[0]}\n"
            page += mindupdate_handle(gun['mindupdate_consume']) + "\n\n"

        voice_gain_tem = voice_text[voice_text.find(f"\n{gun['code']}|GAIN|") + len(gun['code']) + len('|GAIN|') + 1:]
        voice_gain = voice_gain_tem[:voice_gain_tem.find("\n")]
        page += f"|????????????={voice_gain}\n"

        for design in DESIGN:
            if design['id'] == int(gun['id']):
                if design['from'] == 1:
                    from_text = "??????????????? ???THE ART OF GIRLS'FRONTLINE UNTIL THE STARS???"
                elif design['from'] == 2:
                    from_text = "??????????????? ???THE ART OF GIRLS'FRONTLINE VOL.2???"
                elif design['from'] == 3:
                    from_text = f"??????????????????"
                else:
                    from_text = "????????????"
                page += f"|????????????={from_text}\n|????????????={design['des']}\n"

        for cloud_doll in CLOUD:
            if cloud_doll == cn_name:
                page += f"|??????????????????={CLOUD[cloud_doll]}\n"

        count = 1
        for skin in skin_info:
            if gun["id"] == skin["fit_gun"]:
                skin_name_tem = skin_text[skin_text.find(skin["name"]) + len("skin-10000001,") + len(cn_name) + 1:]
                skin_name = skin_name_tem[:skin_name_tem.find("\n")].replace("//n", "")
                skin_dialog_tem = skin_text[skin_text.find(skin["dialog"]) + len("skin-20000001,"):]
                skin_dialog = skin_dialog_tem[:skin_dialog_tem.find("\n")].replace("//n", "<br>").replace("//c", "???")
                page += f"|??????{count}??????={skin_name}|??????{count}??????={skin['id']}"

                extra_tem = skin_text[skin_text.find(skin["illustrator_cv"]) + len("skin-40000001,"):]
                extra_text = extra_tem[:extra_tem.find("\n")]
                if extra_text.find("//c") != -1:
                    if extra_text.split('//c')[1] != "":
                        page += f"|??????{count}CV={extra_text.split('//c')[1]}"
                    page += f"|??????{count}??????={extra_text.split('//c')[0]}"

                for live2D in live2d_info:
                    if live2D["skin"] == skin["id"]:
                        page += f"|??????{count}??????={live2D['skinType']}"
                        break

                for obtain in skin_obtain_info:
                    if obtain['id'] == skin["id"]:
                        page += f"|??????{count}??????={obtain['blackcard']}"
                        page += f"|??????{count}??????={skin_obtain[obtain['obtain_info']]}|??????{count}??????={obtain['obtain_num']}"
                        if obtain['obtain_des']:
                            page += f"|??????{count}????????????={obtain['obtain_des']}"

                for skin_class in skin_class_info:
                    if skin_class['id'] == skin['class_id']:
                        skin_class_name_tem = skin_class_text[
                                              skin_class_text.find(skin_class["name"]) + len("skin_class-10000001,"):]
                        skin_class_name = skin_class_name_tem[:skin_class_name_tem.find("\n")]
                        skin_class_type = skin_class['theme_type']

                        for coll in COLLABORATION:
                            if int(skin["id"]) in coll['skins']:
                                skin_class_name = coll['name']
                                break

                        page += f"|??????{count}??????={skin_class_name}|??????{count}????????????={skin_class_type}"
                        break

                page += f"|??????{count}??????={skin_dialog}\n"

                for skin_group in skin_group_info:
                    is_this_group = None
                    for skin_id in skin_group['skin'].split(","):
                        if skin_id == skin['id']:
                            is_this_group = True

                    if is_this_group:
                        skin_group_tem = skin_group_text[skin_group_text.find(skin_group["theme"]) + len("skin_group-10000011,"):]
                        skin_group_name = skin_group_tem[:skin_group_tem.find("\n")]
                        skin_group_des_tem = skin_group_text[skin_group_text.find(skin_group["description"]) + len("skin_group-20000011,"):]
                        skin_group_des = skin_group_des_tem[:skin_group_des_tem.find("\n")]
                        page += f"|??????{count}??????={skin_group_name}|??????{count}??????icon={skin_group['title_code']}|??????{count}????????????={skin_group_des}\n"
                        break

                count += 1

        page += f"\n|????????????={gun['ratio_life']}|????????????={gun['ratio_armor']}" \
                f"|????????????={gun['ratio_hit']}|????????????={gun['ratio_dodge']}|????????????={gun['ratio_pow']}|????????????={gun['ratio_rate']}" \
                f"|????????????={gun['eat_ratio']}|????????????={gun['ratio_range']}" \
                f"|????????????={gun['ratio_speed']}|????????????={gun['armor_piercing']}|????????????={gun['crit']}|????????????={gun['special']}\n"

        if gun_update:
            page += f"|MOD????????????={gun_update['ratio_life']}|MOD????????????={gun_update['ratio_armor']}" \
                    f"|MOD????????????={gun_update['ratio_hit']}|MOD????????????={gun_update['ratio_dodge']}" \
                    f"|MOD????????????={gun_update['ratio_pow']}|MOD????????????={gun_update['ratio_rate']}" \
                    f"|MOD????????????={gun_update['eat_ratio']}|MOD????????????={gun_update['ratio_range']}" \
                    f"|MOD????????????={gun_update['ratio_speed']}|MOD????????????={gun_update['armor_piercing']}" \
                    f"|MOD????????????={gun_update['crit']}|MOD????????????={gun_update['special']}\n"

        page += f"|??????100={calculate(100, 'life', gun)}|??????100={calculate(100, 'hit', gun)}|??????100={calculate(100, 'dodge', gun)}" \
                f"|??????100={calculate(100, 'pow', gun)}|??????100={calculate(100, 'rate', gun)}|??????100={gun['crit']}"
        if int(gun['ratio_armor']) != 0:
            page += f"|??????100={calculate(100, 'armor', gun)}"
        if int(gun['special']) != 0:
            page += f"|??????100={gun['special']}"

        if gun_update:
            page += f"\n|??????120={calculate(120, 'life', gun_update)}|??????120={calculate(120, 'hit', gun_update)}|??????120={calculate(120, 'dodge', gun_update)}" \
                    f"|??????120={calculate(120, 'pow', gun_update)}|??????120={calculate(120, 'rate', gun_update)}|??????120={gun_update['crit']}"
            if int(gun_update['ratio_armor']) != 0:
                page += f"|??????120={calculate(120, 'armor', gun_update)}"
            if int(gun_update['special']) != 0:
                page += f"|??????120={gun_update['special']}"

        page += "\n\n" + effect_gun("", gun['effect_guntype'], gun['effect_grid_effect'])
        page += effect_grid("", gun['effect_grid_center'], gun['effect_grid_pos'])

        if gun_update:
            page += effect_gun("MOD", gun_update['effect_guntype'], gun_update['effect_grid_effect'])
            page += effect_grid("MOD", gun_update['effect_grid_center'], gun_update['effect_grid_pos'])

        page += "\n" + equip_handle(gun['type_equip1'], 1, equip_category_info, equip_category_text, equip_type_info, equip_type_text) + "\n"
        page += equip_handle(gun['type_equip2'], 2, equip_category_info, equip_category_text, equip_type_info, equip_type_text) + "\n"
        page += equip_handle(gun['type_equip3'], 3, equip_category_info, equip_category_text, equip_type_info, equip_type_text) + "\n\n"

        page += equip_effect_handle(doll_effect(gun), "") + "\n"
        if gun_update:
            page += equip_effect_handle(doll_effect(gun_update), "Mod") + "\n"

        for fetter in fetter_skill_info:
            if fetter['gun'] == gun['id']:
                fetter_skill_tem = fetter_skill_text[fetter_skill_text.find(fetter["name"]) + len("fetter_skill-10000001,"):]
                fetter_skill_name = fetter_skill_tem[:fetter_skill_tem.find("\n")]
                fetter_skill_des_tem = fetter_skill_text[fetter_skill_text.find(fetter["description"]) + len("fetter_skill-10000001,"):]
                fetter_skill_des = fetter_skill_des_tem[:fetter_skill_des_tem.find("\n")].replace("//n", "<br>").replace("//c", "???")
                if (not fetter_skill_des) or (not fetter_dollname_handle(fetter['gun_group'], gun_info, gun_text)):
                    continue
                page += f"|???????????????={fetter_skill_name}\n|?????????icon={fetter['code']}\n" \
                        f"|?????????????????????={fetter_dollname_handle(fetter['gun_group'], gun_info, gun_text)}\n|???????????????={fetter_skill_des}\n\n"

        page += skill_description("??????", gun["skill1"], skill_info, skill_text)
        if gun_update:
            page += skill_description("MOD??????1", gun_update["skill1"], skill_info, skill_text)
            page += skill_description("MOD??????2", gun_update["skill2"], skill_info, skill_text)

        page += "\n"
        page += search_string(origin_text, '??????')
        page += search_string_enter(origin_text, '??????')

        if gun['gun_detail_bg']:
            page += f"|??????={gun['gun_detail_bg']}\n"

        if voice_text.find(f"\n{gun['code']}|Introduce|") > 0:
            voice_intro_tem = voice_text[voice_text.find(f"\n{gun['code']}|Introduce|") + len(gun['code']) + len('|Introduce|') + 1:]
            voice_intro = voice_intro_tem[:voice_intro_tem.find("\n")]
            page += f"|??????????????????={voice_intro}\n"

        introduce_tem = gun_text[gun_text.find(gun["en_introduce"]) + len("gun-40000001,"):]
        introduce_text = introduce_tem[:introduce_tem.find("\n")].replace("//n//n", "<br>").replace("//n", "<br>").replace("//c", ",").replace("|", "{{!}}")
        if gun["introduce"] != "":
            introduce_cn = gun['introduce'].replace("\r\n", "<br>").replace("\n", "<br>").replace("|", "{{!}}")
            page += f"|??????CN={introduce_cn}\n"
        if introduce_text != "":
            page += f"|??????EN={introduce_text}\n"

        page += "}}"

        print(page)
        return
        if page == origin_text:
            continue
        # write_wiki(session, URL, cn_name, page, '??????')


def stc_to_text(text, name):
    tem = text[text.find(name) + len(name) + 1:]
    out_text = tem[:tem.find("\n")]
    return out_text


def text_handle(text):
    text = text.replace("//c", "???").replace("//n", "<br>").replace(" <br>", "<br>").replace("(", "???").replace(")", "???")
    text = text.replace("\"", "\\\"").replace("|", "{{!}}").replace(":", "???").replace(",", "???").replace(";", "???")
    return text


def search_string(origin_text, tar):
    out_text = ""
    if origin_text.find(f'|{tar}=') > 0:
        obtain_1 = origin_text[origin_text.find(f'{tar}='):]
        if (obtain_1.find('|') < 0) or (obtain_1.find('\n') < obtain_1.find('|')):
            out_text += "|" + obtain_1[:obtain_1.find('\n')] + "\n"
        else:
            out_text += f"|{obtain_1[:obtain_1.find('|')]}\n"

    return out_text


# some flag like [[file:xxx.svg.png|25px]] has "|" between two name
def search_string_enter(origin_text, tar):
    out_text = ""
    if origin_text.find(f'|{tar}=') > 0:
        obtain_1 = origin_text[origin_text.find(f'{tar}='):]
        out_text += "|" + obtain_1[:obtain_1.find('\n')] + "\n"

    return out_text


def effect_grid(mode, cen, pos):
    grid = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    self_n = int(- ((int(cen) - 17 - ((int(cen) - 17) % 5)) / 5) + ((int(cen) - 17) % 5) * 3)
    grid[self_n] = 2

    grid_a = pos.split(",")
    for grid_b in grid_a:
        n = int(3*(2 - (int(grid_b) - 1) % 5) + int((int(grid_b) - 1) / 5) - 2 + self_n)
        grid[n] = 1

    count = 0
    grid_text = f""
    while count < len(grid):
        grid_text += f"|{mode}???{count + 1}={grid[count]}"
        count += 1

    return grid_text + "\n"


def effect_gun(mode, effectstr, attrstr):
    gun_effect = ["??????", "??????", "?????????", "??????", "????????????", "??????", "?????????"]
    gun_attribute = ["???", "??????", "??????", "??????", "??????", "??????", "????????????", " ", "??????"]

    text = f"|{mode}????????????="
    array = effectstr.split(",")
    for element in array:
        text += gun_effect[int(element)] + "/"
    text = text[:-1]

    count = 0
    array_2 = attrstr.split(";")
    while count < len(array_2):
        name = int(array_2[count].split(",")[0])
        amount = int(array_2[count].split(",")[1])
        if int(name) == 7:
            print(array_2[count])
        text += f"|{mode}????????????{count + 1}={gun_attribute[name]}|{mode}????????????{count + 1}={amount}"
        count += 1

    return text + "\n"


def equip_handle(type_equip, num, equip_category_info, equip_category_text, equip_type_info, equip_type_text):
    text = ""
    for category in equip_category_info:
        if type_equip.split(";")[0] == category["category"]:
            text = f"|?????????{num}??????={stc_to_text(equip_category_text, category['name'])}"
            break

    count = 0
    slot_equip = type_equip.split(";")[1].split(",")
    while count < len(slot_equip):
        for eq_type in equip_type_info:
            if slot_equip[count] == eq_type["type"]:
                text += f"|?????????{num}??????{count + 1}={stc_to_text(equip_type_text, eq_type['name'])}"
                break
        count += 1

    return text


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


def gain_handle(string, gun_obtain_info, gun_obtain_text):
    gain_arr = string.split(",")

    count = 0
    gain_text = []
    while count < len(gain_arr):
        for obtain in gun_obtain_info:
            if obtain['obtain_id'] == gain_arr[count]:
                obtain_tem = gun_obtain_text[gun_obtain_text.find(obtain["description"]) + len("gun_obtain-10000000,"):]
                obtain_text = obtain_tem[:obtain_tem.find("\n")]
                if len(re.findall(r"[ ]{3,8}-", obtain_text)) == 0:
                    gain_text[len(gain_text) - 1] += re.sub(r"[ ]{3,8}", "", obtain_text)
                else:
                    obtain_text_new = re.sub(r"[ ]{3,8}-", "", obtain_text)
                    gain_text.append(obtain_text_new)
        count += 1

    text = ""
    count = 0
    while count < len(gain_text):
        text += f"|????????????{count +1}={gain_text[count].replace('//c', '???')}"
        count += 1

    return text


def organization_handle(string, org_text):
    if len(string) < 3:
        org_a = "???"
        org_b = "???"
    elif len(string) < 5:
        org_a = string
        org_b = "?????????"
    else:
        org_a = string[:3]
        org_b = string

    if len(org_a) == 3:
        org_text_tem = org_text[org_text.find("organization-10000" + org_a) + len("organization-10000101,"):]
        org_a_name = org_text_tem[:org_text_tem.find("\n")]
        org_text_tem_2 = org_text[org_text.find("organization-20000" + org_a) + len("organization-20000101,"):]
        org_a_des = org_text_tem_2[:org_text_tem_2.find("\n")]
    else:
        org_a_name = org_a
        org_a_des = "???????????????"

    if len(org_b) == 5:
        org_text_tem = org_text[org_text.find("organization-100" + org_b) + len("organization-10010101,"):]
        org_b_name = org_text_tem[:org_text_tem.find("\n")]
        org_text_tem_2 = org_text[org_text.find("organization-200" + org_b) + len("organization-20000101,"):]
        org_b_des = org_text_tem_2[:org_text_tem_2.find("\n")]
    else:
        org_b_name = org_b
        org_b_des = org_b_name

    return f"|??????1={org_a_name}|??????1??????={org_a_des}\n|??????2={org_b_name}|??????2??????={org_b_des}\n"


def mindupdate_handle(string):
    string = string.replace("10:", "????????").replace("45:", "??????????????").replace("51:", "????????????????????").replace(",", ",")
    up_1 = string.split(";")[0]
    up_2 = string.split(";")[1]
    up_3 = string.split(";")[2]

    return f"|??????????????????1={up_1}|??????????????????2={up_2}|??????????????????3={up_3}"


def fetter_dollname_handle(string, gun_info, gun_text):
    text = ""
    for gun_id in string.split(","):
        for gun in gun_info:
            if gun['id'] == gun_id:
                cn_name_tem = gun_text[gun_text.find(gun["name"]) + len("gun-10000001,"):]
                cn_name = cn_name_tem[:cn_name_tem.find("\n")]
                text += cn_name + ","
    return text[:-1]


def equip_effect_handle(doll_effect_dict, mod):
    text = ""

    cn_ring = {"": "???", "_noring": "???"}
    cn_environment = {"day": "??????", "night": "??????"}

    for environment in cn_environment.keys():
        text += f"|{mod}{cn_environment[environment]}????????????={doll_effect_dict['none'][f'effect_{environment}']}" \
                f"|{mod}{cn_environment[environment]}????????????={doll_effect_dict[environment][f'effect_{environment}']}" \
                f"|{mod}{cn_environment[environment]}????????????={doll_effect_dict[f'{environment}_noring'][f'effect_{environment}_noring']}\n"

    for ring in ["", "_noring"]:
        for environment in ["day", "night"]:
            for num in ["1", "2", "3"]:
                this_equip_id = doll_effect_dict[environment + ring][f'equip{num}_id']
                if this_equip_id in EQUIP_NAME.keys():
                    this_equip_name = EQUIP_NAME[this_equip_id]
                    text += f"|{mod}{cn_environment[environment]}{cn_ring[ring]}???????????????{num}MW={this_equip_name}"

                text += f"|{mod}{cn_environment[environment]}{cn_ring[ring]}???????????????{num}={doll_effect_dict[environment + ring][f'equip{num}']}"

            text += "\n"

    return text


doll_file()
