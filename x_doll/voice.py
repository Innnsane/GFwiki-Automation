import ujson
import os
import re

from wikibot import login_wiki
from wikibot import read_wiki
from wikibot import write_wiki

STC_SOURCE = "..\\w_stc_data"
TEXT_SOURCE = "..\\w_text_data"
LUA_SOURCE = "..\\w_lua_data"
VOICE_JP = ".\\voice\\CharacterVoice_jp.txt"

VOICE_LIST_TITLE = {
    1: "交互语音",
    2: "培养语音",
    3: "战斗语音",
    4: "宿舍语音",
    5: "节日语音",
}

VOICE_LIST_DOLL = {
    "TITLECALL": ["游戏标题", 1, 0],
    "HELLO": ["问候", 1, 0],
    "GAIN": ["获得/自我介绍", 1, 0],
    "DIALOGUE1": ["交流1", 1, 0],
    "DIALOGUE2": ["交流2", 1, 0],
    "DIALOGUE3": ["交流3", 1, 0],
    "DIALOGUEWEDDING": ["交流4", 1, 1],
    "SOULCONTRACT": ["誓约", 1, 1],
    "PHRASE": ["口癖", 1, 0],
    "TIP": ["提示", 1, 0],
    "LOADING": ["载入", 1, 0],

    "BUILDOVER": ["建造完成", 2, 0],
    "FEED": ["强化完成", 2, 0],
    "COMBINE": ["编制扩大", 2, 0],
    "FIX": ["修复", 2, 0],
    "FORMATION": ["部队编入", 2, 0],
    "OPERATIONBEGIN": ["后勤出发", 2, 0],
    "OPERATIONOVER": ["后勤归来", 2, 0],
    "BLACKACTION": ["自律作战", 2, 0],

    "GOATTACK": ["出击", 3, 0],
    "MEET": ["遇敌", 3, 0],
    "BREAK": ["重创", 3, 0],
    "WIN": ["胜利", 3, 0],
    "RETREAT": ["撤退", 3, 0],
    "ATTACK": ["进攻阵型", 3, 0],
    "DEFENSE": ["防御阵型", 3, 0],
    "SKILL1": ["技能1", 3, 0],
    "SKILL2": ["技能2", 3, 0],
    "SKILL3": ["技能3", 3, 0],

    "MOOD1": ["笑", 4, 0],
    "MOOD2": ["惊", 4, 0],
    "LOWMOOD": ["失意", 4, 0],
    "APPRECIATE": ["赞赏", 4, 0],
    "AGREE": ["附和", 4, 0],
    "ACCEPT": ["同意", 4, 0],
    "FEELING": ["共鸣", 4, 0],

    "NEWYEAR": ["新年", 5, 0],
    "VALENTINE": ["情人节", 5, 0],
    "TANABATA": ["七夕", 5, 0],
    "ALLHALLOWS": ["万圣节", 5, 0],
    "CHRISTMAS": ["圣诞节", 5, 0]
}


def doll_file():
    with open(os.path.join(STC_SOURCE, "gun_info.json"), "r", encoding="utf-8") as f_gun:
        gun_info = ujson.load(f_gun)
        f_gun.close()
    with open(os.path.join(TEXT_SOURCE, "gun.txt"), "r", encoding="utf-8") as f_gun_text:
        gun_text = f_gun_text.read()
        f_gun_text.close()

    with open(os.path.join(LUA_SOURCE, "NewCharacterVoice.txt"), "r", encoding="utf-8") as f_voice_text:
        voice = f_voice_text.readlines()
        f_voice_text.close()
    with open(os.path.join(LUA_SOURCE, "NewCharacterVoice.txt"), "r", encoding="utf-8") as f_voice_text_2:
        voice_all = f_voice_text_2.read()
        f_voice_text_2.close()
    with open(VOICE_JP, "r", encoding="utf-8") as f_voice_text_jp:
        voice_jp = f_voice_text_jp.readlines()
        f_voice_text_jp.close()

    for gun in gun_info:
        if int(gun["id"]) > 1200:
            break

        if int(gun["id"]) < 64:
            continue

        cn_name_tem = gun_text[gun_text.find(gun["name"]) + len("gun-10000001,"):]
        cn_name = cn_name_tem[:cn_name_tem.find("\n")]
        if cn_name.endswith(" "):
            cn_name = cn_name[:-1]

        try:
            origin_text = read_wiki(the_session, url, cn_name + "/语音")
        except:
            origin_text = ''

        hasMod = None
        hasChiLd = None
        if voice_all.find("\n" + gun["code"] + "Mod|") != -1:
            hasMod = True
        if voice_all.find("\n" + gun["code"] + "_0|") != -1:
            hasChiLd = True

        voice_json = {"normal": {}, "mod": {}, "child": {}}
        for line in voice:
            line_arr = line.split("|")
            if line_arr[0] == gun["code"]:
                voice_json["normal"][line_arr[1]] = {"cn": "", "jp": ""}
                voice_json["normal"][line_arr[1]]["cn"] = line_arr[2][:-1]
            if hasMod and line_arr[0] == gun["code"] + "Mod":
                voice_json["mod"][line_arr[1]] = {"cn": "", "jp": ""}
                voice_json["mod"][line_arr[1]]["cn"] = line_arr[2][:-1]
            if hasChiLd and line_arr[0] == gun["code"] + "_0":
                voice_json["child"][line_arr[1]] = {"cn": "", "jp": ""}
                voice_json["child"][line_arr[1]]["cn"] = line_arr[2][:-1]

        for line_jp in voice_jp:
            line_jp_arr = line_jp.split("|")
            if line_jp_arr[0] == gun["code"]:
                voice_json["normal"][line_jp_arr[1]]["jp"] = line_jp_arr[2][:-1]
            if hasMod and line_jp_arr[0] == gun["code"] + "Mod":
                voice_json["mod"][line_jp_arr[1]]["jp"] = line_jp_arr[2][:-1]
            if hasChiLd and line_jp_arr[0] == gun["code"] + "_0":
                voice_json["child"][line_jp_arr[1]]["jp"] = line_jp_arr[2][:-1]

        page = section("normal", ["默认语音", "额外语音"], voice_json, origin_text, gun['code'])
        if hasMod:
            page += section("mod", ["心智升级默认语音", "心智升级额外语音"], voice_json, origin_text, gun['code'])
        if hasChiLd:
            page += section("child", ["儿童节版默认语音", "儿童节版额外语音"], voice_json, origin_text, gun['code'])

        # write_wiki(the_session, url, "用户:Innbot/sandbox", page, '更新')
        print(page)
        break


def section(mode, title_list, voice, origin_text, gun_code):
    text = ""
    template_part1 = "<noinclude>\n=="
    template_part2 = "==\n</noinclude>{{#invoke:VoiceTable|table|表格标题="
    template_part3 = "\n<noinclude>|可播放=1</noinclude>\n"
    template_part4 = "}}\n"


    count_a = 0
    count_b = 0
    COUNT = [[1, 2, 3], [4, 5]]
    for title in title_list:
        text += template_part1 + title + template_part2 + title + template_part3

        count_c = 1
        for key in VOICE_LIST_DOLL.keys():
            if VOICE_LIST_DOLL[key][1] not in COUNT[count_a]:
                continue

            if VOICE_LIST_DOLL[key][1] == 5 and mode == "child":
                continue

            if VOICE_LIST_DOLL[key][1] == count_b + 1:
                count_b += 1
                text += f"|分类标题{count_c}={VOICE_LIST_TITLE[count_b]}\n\n"

            if key == "TITLECALL":
                text_cn = "少女前线"
                text_jp = "ショウジョゼンセン"
            elif key not in voice[mode].keys():
                text_cn = ""
                text_jp = ""
            else:
                text_cn = voice[mode][key]['cn']
                text_jp = voice[mode][key]['jp']

            origin_cn = search_string(origin_text, key, title_list[0], "中文")
            origin_jp = search_string(origin_text, key, title_list[0], "日文")

            if origin_jp[:5] == "{{模糊|" and origin_jp[len(origin_jp) - 2:] == "}}":
                origin_jp = origin_jp[:len(origin_jp) - 2] + "|}}"

            if text_cn != "" and VOICE_LIST_DOLL[key][2]:
                text_cn = "{{模糊|" + text_cn + "|}}"
            if text_jp != "" and VOICE_LIST_DOLL[key][2]:
                text_jp = "{{模糊|" + text_jp + "|}}"

            if (origin_cn and not text_cn) or origin_cn.find("ruby") != -1:
                text_cn = origin_cn
            if (origin_jp and not text_jp) or origin_jp.find("ruby") != -1:
                text_jp = origin_jp

            voice_type = ".wav"
            if origin_text.find(".mp3") != -1:
                voice_type = ".mp3"

            voice_addition = ""
            if mode == "mod":
                voice_addition = "Mod"
            elif mode == "child":
                voice_addition = "_0"

            text += f"|标题{count_c}={VOICE_LIST_DOLL[key][0]}\n"
            text += f"|日文{count_c}={text_jp.replace('<>', '<br>')}\n"
            text += f"|中文{count_c}={text_cn.replace('<>', '<br>')}\n"
            text += f"|语音{count_c}={gun_code}{voice_addition}_{key}_JP{voice_type}\n\n"
            count_c += 1

        text += template_part4
        count_a += 1
    return text


def search_string(origin_text, tar, title, language):
    if origin_text.find(title) == -1 or origin_text.find(VOICE_LIST_DOLL[tar][0]) == -1:
        return ""

    origin_text_1 = origin_text[origin_text.find(f"|表格标题={title}") + len(f"|表格标题={title}"):]
    if origin_text_1.find(title) == -1:
        origin_text_2 = origin_text_1
    else:
        origin_text_2 = origin_text_1[:origin_text_1.find(title)]

    i = 1
    while i < 30:
        if origin_text_2.find(f"|标题{i}={VOICE_LIST_DOLL[tar][0]}") != -1:
            break
        i += 1

    origin_text_3 = origin_text_2[origin_text_2.find(f"|标题{i}={VOICE_LIST_DOLL[tar][0]}"):]
    origin_text_4 = origin_text_3[origin_text_3.find(f"|{language}{i}=") + len(f"|{language}{i}="):]
    out_text = origin_text_4[:origin_text_4.find("\n")]

    return out_text


doll_file()
