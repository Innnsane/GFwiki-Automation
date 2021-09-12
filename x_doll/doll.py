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

from design import DESIGN
from collaboration import COLLABORATION

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
    skin_obtain = {"gem": "钻石", "coin": "采购", "event": "活动", "rmb": "RMB"}

    for gun in gun_info:
        if int(gun["id"]) > 1200:
            break

        # if int(gun["id"]) <= 339:
        #     continue

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

        page = "{{" + f"战术少女信息3\n|人形名称={cn_name}|code={gun['code']}\n" \
                      f"|实装时间={gun['launch_time'].replace(' 00:00:00', '')}\n" \
                      f"|建造时间={develop_time(gun['develop_duration'])}\n" \
                      f"{gain_handle(gun['obtain_ids'], gun_obtain_info, gun_obtain_text)}\n"

        if int(gun['id']) >= 1000:
            page += f"|星级=1"
        else:
            page += f"|星级={gun['rank']}"
        page += f"|编号={gun['id']}|枪种={gun_type[int(gun['type'])]}\n"

        extra_tem = gun_text[gun_text.find(gun["extra"]) + len("gun-40000001,"):]
        extra_text = extra_tem[:extra_tem.find("\n")]
        if extra_text.split('//c')[1] != "":
            page += f"|CV={extra_text.split('//c')[1]}"
        page += f"|画师={extra_text.split('//c')[0]}\n\n"

        if gun['explore_tag']:
            tag_number = 1
            for tag in gun['explore_tag'].split(","):
                page += f"|人形品质{tag_number}={tag}"
                tag_number += 1
            page += "\n"

        page += organization_handle(gun['org_id'], org_text)
        page += f"|基础弹药={gun['baseammo']}|基础口粮={gun['basemre']}|增加弹药={gun['ammo_add_withnumber']}|增加口粮={gun['mre_add_withnumber']}\n"
        page += f"|拆解人力={gun['retiremp']}|拆解弹药={gun['retireammo']}|拆解口粮={gun['retiremre']}|拆解零件={gun['retirepart']}\n\n"

        gun_update = None
        if gun['mindupdate_consume']:
            for gun_up in gun_info:
                if int(gun_up['id']) == int(gun["id"]) + 20000:
                    gun_update = gun_up

            page += f"|MOD星级={gun_update['rank']}\n"
            for live2D in live2d_info:
                if int(live2D["skin"]) == 0 and live2D["fit_gun"] == gun_update["id"]:
                    page += f"|MOD立绘动态={live2D['skinType']}"

            extra_tem = gun_text[gun_text.find(gun_update["extra"]) + len("gun-40000001,"):]
            extra_text = extra_tem[:extra_tem.find("\n")]
            if extra_text.split('//c')[1] != "":
                page += f"|MODCV={extra_text.split('//c')[1]}"
            page += f"|MOD画师={extra_text.split('//c')[0]}\n"
            page += mindupdate_handle(gun['mindupdate_consume']) + "\n\n"

        voice_gain_tem = voice_text[voice_text.find(f"\n{gun['code']}|GAIN|") + len(gun['code']) + len('|GAIN|') + 1:]
        voice_gain = voice_gain_tem[:voice_gain_tem.find("\n")]
        page += f"|获取台词={voice_gain}\n"

        for design in DESIGN:
            if design['id'] == int(gun['id']):
                if design['from'] == 1:
                    from_text = "官方设定集 《THE ART OF GIRLS'FRONTLINE UNTIL THE STARS》"
                elif design['from'] == 2:
                    from_text = "官方设定集 《THE ART OF GIRLS'FRONTLINE VOL.2》"
                elif design['from'] == 3:
                    from_text = f"战术人形百科"
                else:
                    from_text = "暂无来源"
                page += f"|设定来源={from_text}\n|人形设定={design['des']}\n"

        count = 1
        for skin in skin_info:
            if gun["id"] == skin["fit_gun"]:
                skin_name_tem = skin_text[skin_text.find(skin["name"]) + len("skin-10000001,") + len(cn_name) + 1:]
                skin_name = skin_name_tem[:skin_name_tem.find("\n")].replace("//n", "")
                skin_dialog_tem = skin_text[skin_text.find(skin["dialog"]) + len("skin-20000001,"):]
                skin_dialog = skin_dialog_tem[:skin_dialog_tem.find("\n")].replace("//n", "<br>").replace("//c", "，")
                page += f"|装扮{count}名称={skin_name}|装扮{count}编号={skin['id']}"

                extra_tem = skin_text[skin_text.find(skin["illustrator_cv"]) + len("skin-40000001,"):]
                extra_text = extra_tem[:extra_tem.find("\n")]
                if extra_text.find("//c") != -1:
                    if extra_text.split('//c')[1] != "":
                        page += f"|装扮{count}CV={extra_text.split('//c')[1]}"
                    page += f"|装扮{count}画师={extra_text.split('//c')[0]}"

                for live2D in live2d_info:
                    if live2D["skin"] == skin["id"]:
                        page += f"|装扮{count}动态={live2D['skinType']}"
                        break

                for obtain in skin_obtain_info:
                    if obtain['id'] == skin["id"]:
                        page += f"|装扮{count}黑卡={obtain['blackcard']}"
                        page += f"|装扮{count}获取={skin_obtain[obtain['obtain_info']]}|装扮{count}道具={obtain['obtain_num']}"
                        if obtain['obtain_des']:
                            page += f"|装扮{count}获取详情={obtain['obtain_des']}"

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

                        page += f"|装扮{count}主题={skin_class_name}|装扮{count}主题类型={skin_class_type}"
                        break

                page += f"|装扮{count}对话={skin_dialog}\n"

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
                        page += f"|装扮{count}笔记={skin_group_name}|装扮{count}笔记icon={skin_group['title_code']}|装扮{count}笔记描述={skin_group_des}\n"
                        break

                count += 1

        page += f"\n|生命参数={gun['ratio_life']}|护甲参数={gun['ratio_armor']}" \
                f"|命中参数={gun['ratio_hit']}|回避参数={gun['ratio_dodge']}|伤害参数={gun['ratio_pow']}|射速参数={gun['ratio_rate']}" \
                f"|成长参数={gun['eat_ratio']}|范围参数={gun['ratio_range']}" \
                f"|移动参数={gun['ratio_speed']}|穿甲参数={gun['armor_piercing']}|暴击参数={gun['crit']}|弹链参数={gun['special']}\n"

        if gun_update:
            page += f"|MOD生命参数={gun_update['ratio_life']}|MOD护甲参数={gun_update['ratio_armor']}" \
                    f"|MOD命中参数={gun_update['ratio_hit']}|MOD回避参数={gun_update['ratio_dodge']}" \
                    f"|MOD伤害参数={gun_update['ratio_pow']}|MOD射速参数={gun_update['ratio_rate']}" \
                    f"|MOD成长参数={gun_update['eat_ratio']}|MOD范围参数={gun_update['ratio_range']}" \
                    f"|MOD移动参数={gun_update['ratio_speed']}|MOD穿甲参数={gun_update['armor_piercing']}" \
                    f"|MOD暴击参数={gun_update['crit']}|MOD弹链参数={gun_update['special']}\n"

        page += f"|生命100={calculate(100, 'life', gun)}|命中100={calculate(100, 'hit', gun)}|回避100={calculate(100, 'dodge', gun)}" \
                f"|伤害100={calculate(100, 'pow', gun)}|射速100={calculate(100, 'rate', gun)}|暴击100={gun['crit']}"
        if int(gun['ratio_armor']) != 0:
            page += f"|护甲100={calculate(100, 'armor', gun)}"
        if int(gun['special']) != 0:
            page += f"|弹链100={gun['special']}"

        if gun_update:
            page += f"\n|生命120={calculate(120, 'life', gun_update)}|命中120={calculate(120, 'hit', gun_update)}|回避120={calculate(120, 'dodge', gun_update)}" \
                    f"|伤害120={calculate(120, 'pow', gun_update)}|射速120={calculate(120, 'rate', gun_update)}|暴击120={gun_update['crit']}"
            if int(gun_update['ratio_armor']) != 0:
                page += f"|护甲120={calculate(120, 'armor', gun_update)}"
            if int(gun_update['special']) != 0:
                page += f"|弹链120={gun_update['special']}"

        page += "\n\n" + effect_gun("", gun['effect_guntype'], gun['effect_grid_effect'])
        page += effect_grid("", gun['effect_grid_center'], gun['effect_grid_pos'])

        if gun_update:
            page += effect_gun("MOD", gun_update['effect_guntype'], gun_update['effect_grid_effect'])
            page += effect_grid("MOD", gun_update['effect_grid_center'], gun_update['effect_grid_pos'])

        page += "\n" + equip_handle(gun['type_equip1'], 1, equip_category_info, equip_category_text, equip_type_info, equip_type_text) + "\n"
        page += equip_handle(gun['type_equip2'], 2, equip_category_info, equip_category_text, equip_type_info, equip_type_text) + "\n"
        page += equip_handle(gun['type_equip3'], 3, equip_category_info, equip_category_text, equip_type_info, equip_type_text) + "\n\n"

        for fetter in fetter_skill_info:
            if fetter['gun'] == gun['id']:
                fetter_skill_tem = fetter_skill_text[fetter_skill_text.find(fetter["name"]) + len("fetter_skill-10000001,"):]
                fetter_skill_name = fetter_skill_tem[:fetter_skill_tem.find("\n")]
                fetter_skill_des_tem = fetter_skill_text[fetter_skill_text.find(fetter["description"]) + len("fetter_skill-10000001,"):]
                fetter_skill_des = fetter_skill_des_tem[:fetter_skill_des_tem.find("\n")].replace("//n", "<br>").replace("//c", "，")
                if (not fetter_skill_des) or (not fetter_dollname_handle(fetter['gun_group'], gun_info, gun_text)):
                    continue
                page += f"|同心技名称={fetter_skill_name}\n|同心技icon={fetter['code']}\n" \
                        f"|同心技连携人形={fetter_dollname_handle(fetter['gun_group'], gun_info, gun_text)}\n|同心技描述={fetter_skill_des}\n\n"

        page += skill_description("技能", gun["skill1"], skill_info, skill_text)
        if gun_update:
            page += skill_description("MOD技能1", gun_update["skill1"], skill_info, skill_text)
            page += skill_description("MOD技能2", gun_update["skill2"], skill_info, skill_text)

        page += "\n"
        page += search_string(origin_text, '国籍')
        page += search_string_enter(origin_text, '国旗')

        if gun['gun_detail_bg']:
            page += f"|组织={gun['gun_detail_bg']}\n"

        if voice_text.find(f"\n{gun['code']}|Introduce|") > 0:
            voice_intro_tem = voice_text[voice_text.find(f"\n{gun['code']}|Introduce|") + len(gun['code']) + len('|Introduce|') + 1:]
            voice_intro = voice_intro_tem[:voice_intro_tem.find("\n")]
            page += f"|旧版自我介绍={voice_intro}\n"

        introduce_tem = gun_text[gun_text.find(gun["en_introduce"]) + len("gun-40000001,"):]
        introduce_text = introduce_tem[:introduce_tem.find("\n")].replace("//n//n", "<br>").replace("//n", "<br>").replace("//c", ",").replace("|", "{{!}}")
        if gun["introduce"] != "":
            introduce_cn = gun['introduce'].replace("\r\n", "<br>").replace("\n", "<br>").replace("|", "{{!}}")
            page += f"|介绍CN={introduce_cn}\n"
        if introduce_text != "":
            page += f"|介绍EN={introduce_text}\n"

        page += "}}"

        write_wiki(session, URL, cn_name, page, '更新')
        # print(page)


def stc_to_text(text, name):
    tem = text[text.find(name) + len(name) + 1:]
    out_text = tem[:tem.find("\n")]
    return out_text


def text_handle(text):
    text = text.replace("|", "{{!}}").replace(":", "：").replace(",", "，").replace(";", "；")
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


def skill_description(mode, skill_id, skill_info, skill_text):
    skill_str = ""
    skill_des_array = []
    skill_cd = f""
    skill_start = f""

    skill_id = str(skill_id) + "01"
    skill_text_tem = skill_text
    for skill in skill_info:
        if int(skill_id) % 100 == 11:
            break
        if int(skill["id"]) == int(skill_id):
            skill_text_tem = skill_text_tem[skill_text_tem.find(skill["name"]) + len("battle_skill_config-110010101,"):]
            skill_name = skill_text_tem[:skill_text_tem.find("\n")]
            skill_text_tem = skill_text_tem[skill_text_tem.find(skill["description"]) + len("battle_skill_config-210010101,"):]
            skill_des = skill_text_tem[:skill_text_tem.find("\n")].replace("//c", "，").replace("//n", "<br>").replace("\"", "\\\"")
            skill_des = text_handle(skill_des)
            skill_des = re.sub(r"[ ]{1,10}", " ", skill_des).replace(" <br>", "<br>").replace("(", "（").replace(")", "）")
            skill_des_array.append(skill_des)

            skill_cd += skill["cd_time"] + ","
            skill_start += skill["start_cd_time"] + ","
            if not skill_str:
                skill_str = f"|{mode}名称={skill_name}\n|{mode}icon={skill['code']}\n"
            skill_id = int(skill_id) + 1

    skill_str += f"|{mode}冷却={skill_cd[:-1]}\n|{mode}前置={skill_start[:-1]}\n"

    number = 0
    string = r"[0-9.]{1,15}[%秒倍点发范围弹量]{0,3}"
    color_string = r"<color=#[0-9a-f]{6}>"
    num_string = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
                  "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
                  "twenty-one", "twenty-two", "twenty-three", "twenty-four", "twenty-five", "twenty-six", "twenty-seven",
                  "twenty-eight", "twenty-nine", "thirty", "thirty-one", "thirty-two", "thirty-three", "thirty-four", "thirty-five",
                  "thirty-six", "thirty-seven", "thirty-eight", "thirty-nine", "forty", "forty-one", "forty-two", "forty-three", "forty-four", "forty-five",
                  "forty-six", "forty-seven", "forty-eight", "forty-nine", "fifty", "fifty-one", "fifty-two", "fifty-three", "fifty-four", "fifty-five",
                  "fifty-six", "fifty-seven", "fifty-eight", "fifty-nine", "sixty", "sixty-one", "sixty-two", "sixty-three", "sixty-four", "sixty-five",
                  "sixty-six", "sixty-seven", "sixty-eight", "sixty-nine", "seventy", "seventy-one", "seventy-two", "seventy-three", "seventy-four", "seventy-five",
                  "seventy-six", "seventy-seven", "seventy-eight", "seventy-nine", "eighty", "eighty-one", "eighty-two", "eighty-three", "eighty-four", "eighty-five",
                  "eighty-six", "eighty-seven", "eighty-eight", "eighty-nine"]

    # 用于技能描述的对比 分别是 lv.1 lv.10
    ret_sample_origin = re.findall(string, skill_des_array[0])
    ret_sample_2_origin = re.findall(string, skill_des_array[9])
    str_sample_origin = skill_des_array[0]
    str_sample_2_origin = skill_des_array[9]

    while number < len(skill_des_array):
        ret = re.findall(string, skill_des_array[number])
        ret_sample = ret_sample_origin
        ret_sample_2 = ret_sample_2_origin
        str_sample = str_sample_origin
        str_sample_2 = str_sample_2_origin

        count = 0
        while count < len(ret):
            # skill_des_array[number] 为输出字符串，test_str 为当前处理的字符串，其作用仅为减少代码量，并不会改变最终结果
            test_str = skill_des_array[number][:skill_des_array[number].find(ret[count])]

            # str_sample 的下一个关键字的位置 小于 test_str 字符串的位置 即 多出一段字符串
            # - str_sample: <ret_two>但伤害降低50%，持续6秒。
            # - test_str: <ret_two>，持续6秒。
            if str_sample.find(ret_sample[count]) < str_sample.find(test_str[test_str.find(f"<ret_{num_string[count - 1]}>")+len(f"<ret_{num_string[count - 1]}>"):].replace("</skill>", "")):
                # 进行字符串中字符的对比，开始位置为上一个ret，由于这个原因，各 str 在此前必须保持一致
                count_str = test_str.find(f"<ret_{num_string[count - 1]}>")
                while count_str < len(str_sample):
                    if str_sample[count_str] != skill_des_array[number][count_str]:
                        # 一旦出现相不同字符，记录此处的位置，并寻找下一个相同的字符，此处可能出现bug
                        # 因为下一个相同的字符之后可能并不相同，尤其是一些常用字符，如 【此时减少弹量8、弹量增加8】 vs 【此时弹量增加8】，继续观察
                        count_str_2 = count_str
                        while count_str_2 < len(str_sample):
                            if str_sample[count_str_2] == skill_des_array[number][count_str]:
                                # 将 str_sample 中 比 test 多出的字符串删除
                                str_sample = str_sample[:count_str] + str_sample[count_str_2:]
                                break
                            count_str_2 += 1
                        break
                    count_str += 1
                    
                # 为使程序简便，去掉 count_de ，改为 remove 特定的元素
                ret_sample = ret_sample[:count] + ret_sample[count + 1:]

            if str_sample_2.find(ret_sample_2[count]) < str_sample_2.find(test_str[test_str.find(f"<ret_{num_string[count - 1]}>")+len(f"<ret_{num_string[count - 1]}>"):].replace("</skill>", "")):
                count_str = 0
                while count_str < len(str_sample_2):
                    if str_sample_2[count_str] != skill_des_array[number][count_str]:
                        count_str_2 = count_str
                        while count_str_2 < len(str_sample_2):
                            if str_sample_2[count_str_2] == skill_des_array[number][count_str]:
                                str_sample_2 = str_sample_2[:count_str] + str_sample_2[count_str_2:]
                                break
                            count_str_2 += 1
                        break
                    count_str += 1
                str_sample_2 = str_sample_2[:count] + str_sample_2[count + 1:]

            # str_sample_2 find test_str 的特定字符串 - fail 缺少下一段字符串，即缺少部分描述
            # - str_sample_2: <ret_two>，持续6秒。
            # - test_str: <ret_two>但伤害降低50%，持续6秒。
            if str_sample_2.find(test_str[test_str.find(f"<ret_{num_string[count - 1]}>")+len(f"<ret_{num_string[count - 1]}>"):].replace("</skill>", "")) == -1:
                # 进行字符串中字符的对比，开始位置为上一个ret
                count_str = test_str.find(f"<ret_{num_string[count - 1]}>")
                while count_str < len(str_sample_2):
                    if str_sample_2[count_str] != skill_des_array[number][count_str]:
                        # 一旦出现相不同字符，在该字符之前添加<skill>标识，之后再寻找相同的字符，在该字符之前添加</skill>
                        skill_des_array[number] = skill_des_array[number][:count_str] + "<skill>" + skill_des_array[number][count_str:]
                        str_sample = str_sample[:count_str] + "<skill>" + str_sample[count_str:]

                        count_str_2 = count_str
                        while count_str_2 < len(str_sample_2):
                            if str_sample_2[count_str] == skill_des_array[number][count_str_2]:
                                skill_des_array[number] = skill_des_array[number][:count_str_2] + "</skill>" + skill_des_array[number][count_str_2:]
                                break
                            count_str_2 += 1

                        # 因为影响了描述的标识，故也需要对 str_sample 的相关字符串添加 skill 标识 才能保持一致，由于排错是根据字符的位置进行的，所以必须执行，方式与 test 同理
                        count_str_3 = count_str
                        while count_str_3 < len(str_sample):
                            if str_sample_2[count_str] == str_sample[count_str_3]:
                                str_sample = str_sample[:count_str_3] + "</skill>" + str_sample[count_str_3:]
                                break
                            count_str_3 += 1

                        # 以上是对 skill_des_array[number] 的操作，即 lv.N skill
                        # 对 str_sample_2 中缺少的字符进行补全，该操作不影响 str_sample_2_origin ，只作用于该技能等级
                        str_sample_2 = str_sample_2[:count_str] + skill_des_array[number][count_str:count_str_2] + "</skill>" + str_sample_2[count_str:]

                        # 增加一段描述之后，同样需要对 ret_sample_2 进行 字符匹配 的补充，与 ret 相同
                        ret_sample_2 = ret_sample_2[:count] + [ret[count]] + ret_sample_2[count:]
                        break
                    count_str += 1

            if str_sample.find(test_str[test_str.find(f"<ret_{num_string[count - 1]}>")+len(f"<ret_{num_string[count - 1]}>"):].replace("</skill>", "")) == -1:
                count_str = test_str.find(f"<ret_{num_string[count - 1]}>")
                while count_str < len(str_sample):
                    if str_sample[count_str] != skill_des_array[number][count_str]:
                        skill_des_array[number] = skill_des_array[number][:count_str] + "<skill>" + skill_des_array[number][count_str:]
                        str_sample_2 = str_sample_2[:count_str] + "<skill>" + str_sample_2[count_str:]

                        count_str_2 = count_str
                        while count_str_2 < len(str_sample):
                            if str_sample[count_str] == skill_des_array[number][count_str_2]:
                                skill_des_array[number] = skill_des_array[number][:count_str_2] + "</skill>" + skill_des_array[number][count_str_2:]
                                break
                            count_str_2 += 1

                        count_str_3 = count_str
                        while count_str_3 < len(str_sample_2):
                            if str_sample[count_str] == str_sample_2[count_str_3]:
                                str_sample_2 = str_sample_2[:count_str_3] + "</skill>" + str_sample_2[count_str_3:]
                                break
                            count_str_3 += 1

                        str_sample = str_sample[:count_str] + skill_des_array[number][count_str:count_str_2] + "</skill>" + str_sample[count_str:]
                        ret_sample = ret_sample[:count] + [ret[count]] + ret_sample[count:]
                        break
                    count_str += 1

            if ret[count] != ret_sample_2[count] or ret[count] != ret_sample[count]:
                str_sample = str_sample.replace(ret_sample[count], f"<skill><ret_{num_string[count]}></skill>", 1)
                str_sample_2 = str_sample_2.replace(ret_sample_2[count], f"<skill><ret_{num_string[count]}></skill>", 1)
                skill_des_array[number] = skill_des_array[number].replace(ret[count], f"<skill><ret_{num_string[count]}></skill>", 1)
            else:
                str_sample = str_sample.replace(ret_sample[count], f"<ret_{num_string[count]}>", 1)
                str_sample_2 = str_sample_2.replace(ret_sample_2[count], f"<ret_{num_string[count]}>", 1)
                skill_des_array[number] = skill_des_array[number].replace(ret[count], f"<ret_{num_string[count]}>", 1)
            count += 1

        count_2 = 0
        while count_2 < len(ret):
            skill_des_array[number] = skill_des_array[number].replace(f"<ret_{num_string[count_2]}>", ret[count_2])
            count_2 += 1

        number += 1

    number = 0
    while number < len(skill_des_array):
        color_ret = re.findall(color_string, skill_des_array[number])
        for color_num in color_ret:
            skill_des_array[number] = skill_des_array[number].replace(color_num, "<span style=\\\"color:#" + color_num[len("<color=#"):-1] + "\\\">").replace("</color>", "<\\/span>")
        skill_str += f"|{mode}描述{number + 1}={skill_des_array[number]}\n"
        number += 1

    return skill_str


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
        grid_text += f"|{mode}格{count + 1}={grid[count]}"
        count += 1

    return grid_text + "\n"


def effect_gun(mode, effectstr, attrstr):
    gun_effect = ["全体", "手枪", "冲锋枪", "步枪", "突击步枪", "机枪", "霰弹枪"]
    gun_attribute = ["无", "伤害", "射速", "命中", "回避", "暴击", "技能冷却", " ", "护甲"]

    text = f"|{mode}影响对象="
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
        text += f"|{mode}影响名称{count + 1}={gun_attribute[name]}|{mode}影响效果{count + 1}={amount}"
        count += 1

    return text + "\n"


def equip_handle(type_equip, num, equip_category_info, equip_category_text, equip_type_info, equip_type_text):
    text = ""
    for category in equip_category_info:
        if type_equip.split(";")[0] == category["category"]:
            text = f"|装备槽{num}类型={stc_to_text(equip_category_text, category['name'])}"
            break

    count = 0
    slot_equip = type_equip.split(";")[1].split(",")
    while count < len(slot_equip):
        for eq_type in equip_type_info:
            if slot_equip[count] == eq_type["type"]:
                text += f"|装备槽{num}装备{count + 1}={stc_to_text(equip_type_text, eq_type['name'])}"
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
        text += f"|获得方式{count +1}={gain_text[count].replace('//c', '，')}"
        count += 1

    return text


def organization_handle(string, org_text):
    if len(string) < 3:
        org_a = "无"
        org_b = "无"
    elif len(string) < 5:
        org_a = string
        org_b = "负责人"
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
        org_a_des = "无归属部门"

    if len(org_b) == 5:
        org_text_tem = org_text[org_text.find("organization-100" + org_b) + len("organization-10010101,"):]
        org_b_name = org_text_tem[:org_text_tem.find("\n")]
        org_text_tem_2 = org_text[org_text.find("organization-200" + org_b) + len("organization-20000101,"):]
        org_b_des = org_text_tem_2[:org_text_tem_2.find("\n")]
    else:
        org_b_name = org_b
        org_b_des = org_b_name

    return f"|部门1={org_a_name}|部门1描述={org_a_des}\n|部门2={org_b_name}|部门2描述={org_b_des}\n"


def mindupdate_handle(string):
    string = string.replace("10:", "核心×").replace("45:", "心智碎片×").replace("51:", "新型火控原件×").replace(",", ",")
    up_1 = string.split(";")[0]
    up_2 = string.split(";")[1]
    up_3 = string.split(";")[2]

    return f"|心智升级消耗1={up_1}|心智升级消耗2={up_2}|心智升级消耗3={up_3}"


def fetter_dollname_handle(string, gun_info, gun_text):
    text = ""
    for gun_id in string.split(","):
        for gun in gun_info:
            if gun['id'] == gun_id:
                cn_name_tem = gun_text[gun_text.find(gun["name"]) + len("gun-10000001,"):]
                cn_name = cn_name_tem[:cn_name_tem.find("\n")]
                text += cn_name + ","
    return text[:-1]


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
