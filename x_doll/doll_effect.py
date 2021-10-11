import os
import math
import ujson

from doll_attr import calculate

STC_SOURCE = "../w_stc_data"
TEXT_SOURCE = "../w_text_data"


def doll_effect(gun):
    with open(os.path.join(STC_SOURCE, "equip_info.json"), "r", encoding="utf-8") as f_equip:
        equip_info = ujson.load(f_equip)
        f_equip.close()
    with open(os.path.join(TEXT_SOURCE, "equip.txt"), "r", encoding="utf-8") as f_equip_text:
        equip_text = f_equip_text.read()
        f_equip_text.close()

    equip_group_all = []
    for type_equip_group in [gun["type_equip1"], gun["type_equip2"], gun["type_equip3"]]:
        equip_group_type = []
        for type_equip_single in type_equip_group.split(";")[1].split(","):
            equip_group_type += find_equip(gun["id"], type_equip_group.split(";")[0], type_equip_single, equip_info, equip_text)
        equip_group_all.append(equip_group_type)

    equip_none_effect = doll_attr_calculate(gun, ["", "", ""], "max")
    equip_none_effect_noring = doll_attr_calculate(gun, ["", "", ""], 1.05)
    equip_dict = [{"equip1": "", "equip2": "", "equip3": "",
                   "effect_day": equip_none_effect["day"], "effect_night": equip_none_effect["night"],
                   "effect_day_noring": equip_none_effect_noring["day"], "effect_night_noring": equip_none_effect_noring["night"]}]

    for i in equip_group_all[0]:
        for j in equip_group_all[1]:
            for k in equip_group_all[2]:
                if i["id"] == j["id"] or i["id"] == k["id"] or j["id"] == k["id"]:
                    continue

                equip_effect = doll_attr_calculate(gun, [i, j, k], "max")
                equip_effect_noring = doll_attr_calculate(gun, [i, j, k], 1.05)
                this_equip = {
                    "equip1_id": i["id"],
                    "equip2_id": j["id"],
                    "equip3_id": k["id"],
                    "equip1": stc_to_text(equip_text, i["name"]),
                    "equip2": stc_to_text(equip_text, j["name"]),
                    "equip3": stc_to_text(equip_text, k["name"]),
                    "effect_day": equip_effect["day"],
                    "effect_night": equip_effect["night"],
                    "effect_day_noring": equip_effect_noring["day"],
                    "effect_night_noring": equip_effect_noring["night"]
                }

                if (this_equip["equip1"]+this_equip["equip2"]+this_equip["equip3"]).replace("16lab", "16Lab").find("16Lab") == -1:
                    equip_dict.append(this_equip)

    equip_output = {"day": {}, "night": {}, "day_noring": {}, "night_noring": {}, "none": equip_dict[0]}
    for key_2 in ["day", "night", "day_noring", "night_noring"]:
        max_effect = 0

        for equip in equip_dict:
            if equip[f"effect_{key_2}"] > max_effect:
                max_effect = equip[f"effect_{key_2}"]
                equip_output[key_2] = equip

    return equip_output


def find_equip(gun_id, category, type_equip, equip_info, equip_text):
    equip_dict = []
    for equip in equip_info:
        if equip["rank"] not in ["5"] or category != equip["category"] or not stc_to_text(equip_text, equip["equip_introduction"]):
            continue
        if ((not equip["fit_guns"]) or (equip["fit_guns"] and gun_id in equip["fit_guns"].split(","))) and equip["type"] == type_equip:
            equip_dict.append(equip)

    return equip_dict


def doll_attr_calculate(gun, equip_group, loveness):
    lv = 100
    if int(gun["id"]) > 20000:
        lv = 120

    if loveness == "max" and int(gun["id"]) > 20000:
        loveness = 1.15
    elif loveness == "max":
        loveness = 1.1

    attr_change = {"life": 0, "pow": 0, "rate": 0, "hit": 0, "dodge": 0, "armor": 0}
    attr_fixed = {"critical_harm_rate": 150, "critical_percent": gun['crit'],
                  "armor_piercing": gun['armor_piercing'], "night_view_percent": 0, "bullet_number_up": gun['special']}
    attr_other = {"id": gun["id"], "star": gun["rank"], "upgrade": lv, "type": gun["type"], "skill_effect_per": 0, "skill_effect": 0}

    for key in ["pow", "hit", "dodge"]:
        attr_change[key] = gf_ceil(calculate(lv, key, gun) * loveness)
    for key in ["life", "rate", "armor"]:
        attr_change[key] = gf_ceil(calculate(lv, key, gun))

    for equip in equip_group:
        if not equip:
            continue

        attr_other["skill_effect_per"] += int(equip["skill_effect_per"])
        attr_other["skill_effect"] += int(equip["skill_effect"])

        equip_mul = {}
        if equip['bonus_type']:
            equip_mul = bonus_handle(equip['bonus_type'])

        for key in attr_change.keys():
            if key in equip.keys() and equip[key] and (key not in equip_mul.keys()):
                equip_mul[key] = "1"
        for key in attr_fixed.keys():
            if key in equip.keys() and equip[key] and (key not in equip_mul.keys()):
                equip_mul[key] = "1"

        # print(equip_mul)
        for key in equip_mul.keys():
            attr = math.floor(float(equip[key].split(",")[-1]) * float(equip_mul[key]))

            if key in attr_change.keys():
                attr_change[key] = int(attr_change[key]) + int(attr)
            elif key in attr_fixed.keys():
                attr_fixed[key] = int(attr_fixed[key]) + int(attr)

    day = doll_effect_calculate({"attr_change": attr_change, "attr_fixed": attr_fixed, "attr_other": attr_other}, "day")
    night = doll_effect_calculate({"attr_change": attr_change, "attr_fixed": attr_fixed, "attr_other": attr_other}, "night")

    return {"day": day, "night": night}


def doll_effect_calculate(gun_attr, fight_type):

    skill_level_default = int(10)
    star = int(gun_attr["attr_other"]["star"])
    skill_effect = int(gun_attr["attr_other"]["skill_effect"])
    skill_effect_per = int(gun_attr["attr_other"]["skill_effect_per"])

    # 1技能效能 = ceiling（5*(0.8+星级/10)*[35+5*(技能等级-1)]*(100+skill_effect_per)/100,1) + skill_effect
    # 2技能效能 = ceiling（5*(0.8+星级/10)*[15+2*(技能等级-1)]*(100+skill_effect_per)/100,1) + skill_effect
    doll_skill_effect = gf_ceil(5*(0.8+star/10)*(35+5*(skill_level_default-1))*(100+skill_effect_per)/100) + skill_effect
    if gun_attr["attr_other"]["upgrade"] > 100:
        doll_skill_effect += gf_ceil(5*(0.8+star/10)*(15+2*(skill_level_default-1))*(100+skill_effect_per)/100)

    life = int(gun_attr["attr_change"]["life"])
    dodge = int(gun_attr["attr_change"]["dodge"])
    armor = int(gun_attr["attr_change"]["armor"])
    # 防御效能 = CEILING(生命*(35+闪避)/35*(4.2*100/MAX(1,100-护甲)-3.2),1)
    defend_effect = gf_ceil(life*5*(35+dodge)/35*(4.2*100/max(1, 100-armor)-3.2))

    hit = int(gun_attr["attr_change"]["hit"])
    night_view_percent = int(gun_attr["attr_fixed"]["night_view_percent"])
    if fight_type == "night":
        # 夜战命中 = CEILING(命中*(1+(-0.9*(1-夜视仪数值/100))),1)
        hit = gf_ceil(hit*(1+(-0.9*(1-night_view_percent/100))))

    attack = int(gun_attr["attr_change"]["pow"])
    rate = int(gun_attr["attr_change"]["rate"])
    critical = int(gun_attr["attr_fixed"]["critical_percent"])
    critical_damage = int(gun_attr["attr_fixed"]["critical_harm_rate"])
    armor_piercing = int(gun_attr["attr_fixed"]["armor_piercing"])
    bullet = int(gun_attr["attr_fixed"]["bullet_number_up"])
    if gun_attr["attr_other"]["type"] == "6":
        # SG攻击 = 6*5*(3*弹量*(伤害+穿甲/3)*(1+暴击率*(暴击伤害-100)/10000)/(1.5+弹量*50/射速+0.5*弹量)*命中/(命中+23)+8)
        attack_effect = gf_ceil(6*5*(3*bullet*(attack+armor_piercing/3)*(1+critical*(critical_damage-100)/10000)/(1.5+bullet*50/rate+0.5*bullet)*hit/(hit+23)+8))
    elif gun_attr["attr_other"]["type"] == "5":
        # MG攻击 = 7*5*(弹量*(伤害+穿甲/3)*(1+暴击率*(暴击伤害-100)/10000)/(弹量/3+4+200/射速)*命中/(命中+23)+8)
        attack_effect = gf_ceil(7*5*(bullet*(attack+armor_piercing/3)*(1+critical*(critical_damage-100)/10000)/(bullet/3+4+200/rate)*hit/(hit+23)+8))
    else:
        # 其他攻击 = 5*5*(伤害+穿甲/3)*(1+暴击率*(暴击伤害-100)/10000)*射速/50*命中/(命中+23)+8)
        attack_effect = gf_ceil(5*5*((attack+armor_piercing/3)*(1+critical*(critical_damage-100)/10000)*rate/50*hit/(hit+23)+8))

    effect_total = doll_skill_effect + defend_effect + attack_effect
    return effect_total


def stc_to_text(text, name):
    tem = text[text.find(name) + len(name) + 1:]
    out_text = tem[:tem.find("\n")]
    return out_text


def bonus_handle(string):
    dict1 = {}
    attr1 = string.split(',')
    for key in attr1:
        type1 = key.split(':')[0]
        numb1 = key.split(':')[1]
        dict1[type1] = str(1 + int(numb1) / 1000)
    return dict1


def gf_ceil(number):
    if number % 1 < 0.0001:
        number = number - (number % 1)
    else:
        number = number - (number % 1) + 1
    return int(number)
