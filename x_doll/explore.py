import ujson
import os
import re

STC_SOURCE = "..\\w_stc_data"
TEXT_SOURCE = "..\\w_text_data"
LUA_SOURCE = "..\\w_lua_data"
OBTAIN_SOURCE = "..\\x_skin\\obtain\\obtain.txt"


def get_affair_info():
    with open(os.path.join(STC_SOURCE, "explore_affair_client_info.json"), "r", encoding="utf-8") as f_explore:
        explore_info = ujson.load(f_explore)
        f_explore.close()
    with open(os.path.join(TEXT_SOURCE, "explore_affair_client.txt"), "r", encoding="utf-8") as f_explore_text:
        explore_text = f_explore_text.read()
        f_explore_text.close()

    affair_all = {}
    for explore in explore_info:

        text_tem = explore_text[explore_text.find(explore["content"]) + len(explore["content"]) + 1:]
        text = text_tem[:text_tem.find("\n")].replace("//c", ",").replace("//n", "<br>")

        affair = {'id': explore['id'], 'area_id': area_handle(explore['area_id']), 'text': text, 'gun': []}

        for count in ['1', '2', '3', '4', '5']:
            if text.find(f'[gun{count}:') != -1:
                style_tem = text[text.find(f'[gun{count}:') + len(f'[gun{count}:'):]
                style_text = style_tem[:style_tem.find("]")]

                style_arr = []
                for style in style_text.split(','):
                    style_arr.append(style)

                affair['gun'].append(style_arr)
                affair['text'] = affair['text'].replace(f'[gun{count}:{style_text}]', f'<span>人形{count}</span>').replace(f'[gun{count}]', f'<span>人形{count}</span>')

            elif text.find(f'[gun{count}]') != -1:
                affair['gun'].append([])
                affair['text'] = affair['text'].replace(f'[gun{count}]', f'<span>人形{count}</span>')

        affair_all[affair['id']] = affair
    return affair_all


def area_handle(string):
    area = {'1': '城市', '2': '雪地', '3': '森林', '4': '荒野'}

    out = ''
    arr = string.split(",")
    if len(arr) >= 4:
        return '所有区域'

    for i in arr:
        out += area[i] + ','

    return out[:-1]


def get_style_affair():
    affair_info = get_affair_info()

    style_all = {}
    for affair in affair_info:

        count = 1
        for number in affair_info[affair]['gun']:
            area_text = affair_info[affair]['area_id']
            final_text = affair_info[affair]['text'].replace(f'<span>人形{count}</span>', '<span>{{PAGENAME}}</span>')

            for aid in number:
                if aid not in style_all.keys():
                    style_all[aid] = [{'area': area_text, 'text': final_text}]
                else:
                    style_all[aid].append({'area': area_text, 'text': final_text})
            count += 1

    return style_all


def create_template():
    style_all = get_style_affair()

    template = ''
    for aid in style_all:
        template += "</nowiki>{{#ifeq:{{{1|}}}|" + aid + "|{{探索事件"

        count = 1
        for i in style_all[aid]:
            template += f"|区域{count}={i['area']}|事件{count}={i['text']}"
            count += 1
        template += "}}|}}<nowiki>\n"

    with open(".\\explore\\template.txt", "w", encoding="utf-8") as f:
        f.write(template.replace("<span>", '<span class="affairName">').replace("[pet1]", '<span class="affairName">宠物1</span>'))
        f.close()


create_template()
