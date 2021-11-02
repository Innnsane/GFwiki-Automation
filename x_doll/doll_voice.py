import os
import sys
import ujson
import UnityPy

sys.path.append("..")
from wikibot import URL
from wikibot import read_wiki
from wikibot import write_wiki
from wikibot import login_innbot

STC_SOURCE = "../w_stc_data"
TEXT_SOURCE = "../w_text_data"
LUA_SOURCE = "../w_lua_data"
DESTINATION = "./voice"
VOICE_CH = "./voice/ch/NewCharacterVoice.json"
VOICE_JP = "./voice/jp/NewCharacterVoice.json"
VOICE_EN = "./voice/en/NewCharacterVoice.json"
VOICE_KR = "./voice/kr/NewCharacterVoice.json"
LANG = ["ch", "jp", "en", "kr"]
lang_cn = {"ch": "中文", "jp": "日文", "en": "英文", "kr": "韩文"}

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

    voice_dict = {}
    for lang in LANG:
        with open(os.path.join("./voice", lang, "NewCharacterVoice.json"), "r", encoding="utf-8") as f:
            voice_dict[lang] = ujson.load(f)
            f.close()

    session = login_innbot()

    for gun in gun_info:
        if int(gun["id"]) > 500:
            break

        cn_name_tem = gun_text[gun_text.find(gun["name"]) + len("gun-10000001,"):]
        cn_name = cn_name_tem[:cn_name_tem.find("\n")]
        if cn_name.endswith(" "):
            cn_name = cn_name[:-1]

        try:
            origin_text = read_wiki(session, URL, cn_name + "/语音")
        except:
            origin_text = ''

        voice_json = {"normal": {}, "mod": {}, "child": {}}
        for lang in LANG:
            voice_json["normal"][lang] = {}
            voice_json["mod"][lang] = {}
            voice_json["child"][lang] = {}

            for voice_gun in voice_dict[lang].keys():
                if voice_gun == gun["code"]:
                    for voice_type in voice_dict[lang][voice_gun].keys():
                        voice_json["normal"][lang][voice_type] = voice_dict[lang][voice_gun][voice_type]
                if voice_gun == f"{gun['code']}Mod":
                    for voice_type in voice_dict[lang][voice_gun].keys():
                        voice_json["mod"][lang][voice_type] = voice_dict[lang][voice_gun][voice_type]
                if voice_gun == f"{gun['code']}_0":
                    for voice_type in voice_dict[lang][voice_gun].keys():
                        voice_json["child"][lang][voice_type] = voice_dict[lang][voice_gun][voice_type]

        page = "<noinclude>__NOTOC__{{#Widget:VoiceTableSwitch}}\n</noinclude>"
        page += section("normal", ["默认语音", "额外语音"], voice_json, origin_text, gun['code'])
        if voice_json["mod"]["ch"].keys():
            page += section("mod", ["心智升级默认语音", "心智升级额外语音"], voice_json, origin_text, name_mod(gun['code']))
        if voice_json["child"]["ch"].keys():
            page += section("child", ["儿童节版默认语音", "儿童节版额外语音"], voice_json, origin_text, gun['code'])

        # purge_wiki(session, URL, cn_name + "/语音")
        write_wiki(session, URL, cn_name + "/语音", page, '更新')
        # print(page)


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

            text_dict = {}
            for lang in LANG:
                if key == "TITLECALL":
                    text_dict[lang] = ""
                elif key.lower() not in voice[mode][lang].keys():
                    text_dict[lang] = ""
                else:
                    text_dict[lang] = "<br>".join(voice[mode][lang][key.lower()])

            origin_dict = {}
            for lang in LANG:
                origin_dict[lang] = search_string(origin_text, key, title_list[0], lang_cn[lang])["text"]

            for lang in LANG:
                if text_dict[lang] != "" and VOICE_LIST_DOLL[key][2]:
                    text_dict[lang] = "{{模糊|" + text_dict[lang] + "|}}"
                if (origin_dict[lang] and not text_dict[lang]) or origin_dict[lang].find("ruby") != -1:
                    text_dict[lang] = origin_dict[lang]

            voice_type = search_string(origin_text, key, title_list[0], "日文")["type"]
            if voice_type != ".mp3":
                voice_type = ".wav"

            voice_addition = ""
            if mode == "mod":
                voice_addition = "Mod"
            elif mode == "child":
                voice_addition = "_0"

            text += f"|标题{count_c}={VOICE_LIST_DOLL[key][0]}\n"
            for lang in LANG:
                text += f"|{lang_cn[lang]}{count_c}={text_dict[lang]}\n"
            text += f"|语音{count_c}={gun_code}{voice_addition}_{key}_JP{voice_type}\n\n"
            count_c += 1

        text += template_part4
        count_a += 1
    return text


def search_string(origin_text, tar, title, language):
    if origin_text.find(title) == -1 or origin_text.find(VOICE_LIST_DOLL[tar][0]) == -1:
        return {"text": "", "type": ""}

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

    # 当前无对应语言的文本记录
    if origin_text_3.find(f"|{language}{i}=") == -1:
        return {"text": "", "type": ""}

    origin_text_4 = origin_text_3[origin_text_3.find(f"|{language}{i}=") + len(f"|{language}{i}="):]
    voice_text = origin_text_4[:origin_text_4.find("\n")]

    origin_text_5 = origin_text_3[origin_text_3.find(f"|语音{i}=") + len(f"|语音{i}="):]
    voice_type_text = origin_text_5[:origin_text_5.find("\n")]
    voice_type = voice_type_text[len(voice_type_text) - 4:]

    return {"text": voice_text, "type": voice_type}


def name_mod(code):
    if code == "xm3":
        return "XM3"
    else:
        return code


def stc_to_text(text, name):
    tem = text[text.find(name) + len(name) + 1:]
    out_text = tem[:tem.find("\n")]
    return out_text


def unpack_voice_text():
    for file_name in os.listdir(DESTINATION):
        if not os.path.exists(os.path.join(DESTINATION, file_name, "asset_textes.ab")):
            continue

        file_path = os.path.join(DESTINATION, file_name, "asset_textes.ab")
        env = UnityPy.load(file_path)

        for obj in env.objects:
            data = obj.read()

            if str(obj.type) != "TextAsset":
                continue
            if str(data.name) != "NewCharacterVoice":
                continue

            data_json = {}
            data_line = data.text.split("\r\n")
            for line in data_line:
                if not line:
                    continue

                line_code = line.split("|")[0]
                line_type = line.split("|")[1]
                line_text = line.split("|")[2]

                if line_code not in data_json.keys():
                    data_json[line_code] = {}
                data_json[line_code][line_type] = line_text.replace("＜＞", "<>").split("<>")

            with open(os.path.join(DESTINATION, file_name, f"NewCharacterVoice.json"), "w", encoding='utf-8') as f:
                ujson.dump(data_json, f, ensure_ascii=False)


if __name__ == '__main__':
    unpack_voice_text()
    # doll_file()
