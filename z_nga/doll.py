import requests
import ujson
import math
import os
import re


STC_SOURCE = "..\\w_stc_data"
TEXT_SOURCE = "..\\w_text_data"
LUA_SOURCE = "..\\w_lua_data"
OBTAIN_SOURCE = "..\\x_skin\\obtain\\obtain.txt"


def doll_file():
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

    with open(OBTAIN_SOURCE, "r", encoding="utf-8") as f_obtain:
        skin_obtain_info = ujson.load(f_obtain)
        f_obtain.close()

    gun_type = ["None", "HG", "SMG", "RF", "AR", "MG", "SG"]
    skin_obtain = {"gem": "钻石", "coin": "采购", "event": "活动", "rmb": "RMB"}
    AttrSpeed = {"HG": 1.50, "SMG": 1.20, "RF": 0.70, "AR": 1.00, "MG": 0.40, "SG": 0.60};

    out_json = []
    for gun in gun_info:
        if int(gun["id"]) > 1200:
            break
        if int(gun["id"]) <= 1029:
            continue

        this_gun = {}
        cn_name_tem = gun_text[gun_text.find(gun["name"]) + len("gun-10000001,"):]
        cn_name = cn_name_tem[:cn_name_tem.find("\n")]
        if cn_name.endswith(" "):
            cn_name = cn_name[:-1]

        this_gun['id'] = gun['id']
        this_gun['rank'] = gun['rank']
        this_gun['name'] = cn_name
        this_gun['type'] = gun_type[int(gun['type'])]

        this_gun['life'] = calculate(100, 'life', gun)
        this_gun['pow'] = calculate(100, 'pow', gun)
        this_gun['hit'] = calculate(100, 'hit', gun)
        this_gun['dodge'] = calculate(100, 'dodge', gun)
        this_gun['rate'] = calculate(100, 'rate', gun)
        this_gun['armor_piercing'] = gun['armor_piercing']
        this_gun['armor'] = calculate(100, 'armor', gun)
        this_gun['crit'] = gun['crit']
        this_gun['special'] = gun['special']
        this_gun['speed'] = int(int(gun['ratio_speed']) / AttrSpeed[this_gun['type']] * 10 / 100)

        effect_gun_json = effect_gun(gun['effect_guntype'], gun['effect_grid_effect'])
        this_gun['effect_gun_grid'] = effect_grid(gun['effect_grid_center'], gun['effect_grid_pos'])
        this_gun['effect_gun_tar'] = effect_gun_json['target']
        this_gun['effect_gun_des'] = effect_gun_json['des']

        skill_json = skill_description(gun["skill1"], skill_info, skill_text)
        this_gun['skill_name'] = skill_json['name']
        this_gun['skill_start'] = skill_json['start']
        this_gun['skill_cd'] = skill_json['cd']
        this_gun['skill_des'] = skill_json['des']

        out_json.append(this_gun)

    print(out_json)
    with open(".\\doll.json", "w", encoding='utf-8') as f:
        ujson.dump(out_json, f)
        f.close()
    return


def text_handle(text):
    text = text.replace("|", "{{!}}").replace(":", "：").replace(",", "，").replace(";", "；")
    return text


def skill_description(skill_id, skill_info, skill_text):
    skill_json = {}
    skill_id = str(skill_id) + "01"
    skill_text_tem = skill_text
    for skill in skill_info:
        if int(skill_id) % 100 == 10:
            skill_json['cd'] = skill["cd_time"]
            skill_json['start'] = skill["start_cd_time"]
            skill_text_tem = skill_text_tem[skill_text_tem.find(skill["name"]) + len("battle_skill_config-110010101,"):]
            skill_name = skill_text_tem[:skill_text_tem.find("\n")]
            skill_text_tem = skill_text_tem[skill_text_tem.find(skill["description"]) + len("battle_skill_config-210010101,"):]
            skill_des = skill_text_tem[:skill_text_tem.find("\n")].replace("//c", "，").replace("//n", "<br>").replace("\"", "\\\"")
            skill_des = text_handle(skill_des)
            skill_des = re.sub(r"[ ]{1,10}", " ", skill_des).replace(" <br>", "<br>").replace("(", "（").replace(")", "）")
            skill_json['name'] = skill_name
            skill_json['des'] = skill_des
            break
        if int(skill["id"]) == int(skill_id):
            skill_id = int(skill_id) + 1

    return skill_json


def effect_grid(cen, pos):
    color = {'0': '□', '1': '■', '2': '▣'}
    grid = ['0', '0', '0', '0', '0', '0', '0', '0', '0']
    self_n = int(- ((int(cen) - 17 - ((int(cen) - 17) % 5)) / 5) + ((int(cen) - 17) % 5) * 3)
    grid[self_n] = '2'

    grid_a = pos.split(",")
    for grid_b in grid_a:
        n = int(3*(2 - (int(grid_b) - 1) % 5) + int((int(grid_b) - 1) / 5) - 2 + self_n)
        grid[n] = '1'

    count = 0
    grid_text = f""
    while count < len(grid):
        grid_text += f"{color[grid[count]]}"
        count += 1

    return grid_text


def effect_gun(effectstr, attrstr):
    gun_effect = ["全体", "手枪", "冲锋枪", "步枪", "突击步枪", "机枪", "霰弹枪"]
    gun_attribute = ["无", "伤害", "射速", "命中", "回避", "暴击", "技能冷却", " ", "护甲"]

    out_json = {}
    text = f""
    array = effectstr.split(",")
    for element in array:
        text += gun_effect[int(element)] + "/"
    out_json['target'] = text[:-1]

    count = 0
    text_2 = ""
    array_2 = attrstr.split(";")
    while count < len(array_2):
        name = int(array_2[count].split(",")[0])
        amount = int(array_2[count].split(",")[1])
        if int(name) == 7:
            print(array_2[count])
        text_2 += f"{gun_attribute[name]}{amount}%,"
        count += 1
    out_json['des'] = text_2[:-1]

    return out_json


BASIC = [16, 45, 5, 5]
BASIC_LIFE_ARMOR = [
    [[55, 0.555], [2, 0.161]],
    [[96.283, 0.138], [13.979, 0.04]]
]
BASE_ATTR = [
    [0.60, 0.60, 0.80, 1.20, 1.80, 0.00],
    [1.60, 0.60, 1.20, 0.30, 1.60, 0.00],
    [0.80, 2.40, 0.50, 1.60, 0.80, 0.00],
    [1.00, 1.00, 1.00, 1.00, 1.00, 0.00],
    [1.50, 1.80, 1.60, 0.60, 0.60, 0.00],
    [2.00, 0.70, 0.40, 0.30, 0.30, 1.00]
]
GROW = [
    [[0.242, 0], [0.181, 0], [0.303, 0], [0.303, 0]],
    [[0.06, 18.018], [0.022, 15.741], [0.075, 22.572], [0.075, 22.572]]
]
TYPE_ENUM = {"HG": 0, "SMG": 1, "RF": 2, "AR": 3, "MG": 4, "SG": 5}
ATTR_ENUM = {"life": 0, "pow": 1, "rate": 2, "hit": 3, "dodge": 4, "armor": 5}


def calculate(lv, attr_type, gun):
    mod = 1
    if lv == 100:
        mod = 0

    guntype = int(gun['type']) - 1
    attr = ATTR_ENUM[attr_type]
    ratio = int(gun['ratio_' + attr_type])
    growth = int(gun['eat_ratio'])

    if attr == 0 or attr == 5:
        return math.ceil(
            (BASIC_LIFE_ARMOR[mod][attr & 1][0] + (lv-1)*BASIC_LIFE_ARMOR[mod][attr & 1][1]) * BASE_ATTR[guntype][attr] * ratio / 100
        )
    else:
        base = BASIC[attr-1] * BASE_ATTR[guntype][attr] * ratio / 100
        accretion = (GROW[mod][attr-1][1] + (lv-1)*GROW[mod][attr-1][0]) * BASE_ATTR[guntype][attr] * ratio * growth / 100 / 100
        return math.ceil(base) + math.ceil(accretion)


doll_file()
