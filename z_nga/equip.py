import requests
import ujson
import os
import re


STC_SOURCE = "..\\w_stc_data"
TEXT_SOURCE = "..\\w_text_data"
EQUIP_SOURCE = "..\\x_equip"


def main():
    with open(os.path.join(STC_SOURCE, "equip_info.json"), "r", encoding="utf-8") as f_equip:
        equip_info = ujson.load(f_equip)
        f_equip.close()
    with open(os.path.join(TEXT_SOURCE, "equip.txt"), "r", encoding="utf-8") as f_equip_text:
        equip_text = f_equip_text.read()
        f_equip_text.close()
    with open(os.path.join(STC_SOURCE, "gun_info.json"), "r", encoding="utf-8") as f_gun:
        gun_info = ujson.load(f_gun)
        f_gun.close()
    with open(os.path.join(TEXT_SOURCE, "gun.txt"), "r", encoding="utf-8") as f_gun_text:
        gun_text = f_gun_text.read()
        f_gun_text.close()

    EQUIP_TYPE1 = ["", "配件", "弹匣", "人形装备"]
    EQUIP_TYPE2 = ["", "光学瞄具", "全息瞄具", "红点瞄具", "夜战装备", "穿甲弹", "状态弹", "霰弹", "高速弹", "芯片", "外骨骼", "防弹插板", "特殊", "消音器", "弹链箱", "伪装披风", "特殊", "特殊"]
    EQUIP_ATTR = {"pow": "伤害", "hit": "命中", "dodge": "回避", "speed": "移速", "rate": "射速", "critical_harm_rate": "暴击伤害",
                  "critical_percent": "暴击概率", "armor_piercing": "穿甲", "armor": "护甲", "night_view_percent": "夜视能力", "bullet_number_up": "弹量"}

    out_json = []
    for equip in equip_info:
        if int(equip['id']) < 247:
            continue

        this_equip = {}
        eq_name_tem = equip_text[equip_text.find(equip["name"]) + len("equip-10000001,"):]
        eq_name = eq_name_tem[:eq_name_tem.find("\n")]

        text = "{{装备信息\n"
        eq_intro_tem = equip_text[equip_text.find(equip["equip_introduction"]) + len("equip-30000001,"):]
        eq_intro = eq_intro_tem[:eq_intro_tem.find("\n")]

        # if there is no introduction means not in the game
        if not eq_intro:
            continue

        this_equip['id'] = equip['id']
        this_equip['star'] = equip['rank']
        this_equip['name'] = eq_name
        this_equip['type'] = EQUIP_TYPE1[int(equip['category'])] + "/" + EQUIP_TYPE2[int(equip['type'])]
        this_equip['doll'] = doll_handle(gun_info, gun_text, equip['fit_guns'])
        this_equip['max_level'] = eq_intro

        if int(equip['max_level']) == 0:
            this_equip['max_level'] = '0'
        else:
            this_equip['max_level'] = '10'

        if int(equip['skill']) != 0 or int(equip['passive_skill']) != 0:
            this_equip['skill'] = '○'
        else:
            this_equip['skill'] = '×'

        count = 1
        equip_mul = {}
        if equip['bonus_type']:
            equip_mul = bonus_handle(equip['bonus_type'])
        for key in EQUIP_ATTR.keys():
            if not equip[key]:
                continue
            if key not in equip_mul.keys():
                text += f"|属性{count}倍率=1.0\n"
                equip_mul[key] = '1'
            count += 1

        eq_des_tem = equip_text[equip_text.find(equip["description"]) + len("equip-20000001,"):]
        eq_des = eq_des_tem[:eq_des_tem.find("\n")]
        for key in EQUIP_ATTR.keys():
            if eq_des.find(f"<{key}>") > 0:
                eq_des = eq_des.replace(f"<{key}>", str(int(float(equip[key].split(',')[1]) * float(equip_mul[key]))))

        pattern_1 = re.compile(r'(//n)?\$')
        attr_des = re.sub(pattern_1, '$', eq_des)
        attr_des_a = attr_des[:attr_des.find('$')].replace('//n', ' ')

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

        this_equip['attr'] = attr_des[:attr_des.find('$')].replace('//n', ' ')
        this_equip['powerup_mp'] = int(float(equip['powerup_mp']) * 10000 * int(equip['exclusive_rate']))
        this_equip['powerup_ammo'] = int(float(equip['powerup_ammo']) * 10000 * int(equip['exclusive_rate']))
        this_equip['powerup_mre'] = int(float(equip['powerup_mre']) * 10000 * int(equip['exclusive_rate']))
        this_equip['powerup_part'] = int(float(equip['powerup_part']) * 10000 * int(equip['exclusive_rate']))
        this_equip['des'] = eq_intro

        print(this_equip)
        out_json.append(this_equip)

    with open(".\\equip.json", "w", encoding='utf-8') as f:
        ujson.dump(out_json, f)
        f.close()
    return


def doll_handle(gun_info, gun_text, strings):
    gun_type = ["None", "HG", "SMG", "RF", "AR", "MG", "SG"]

    count = 1
    text_str = ''
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
                text_str += f"{cn_name}[{gun_type[int(gun['type'])]}]"

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


main()
