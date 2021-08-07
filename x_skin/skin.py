import os
import ujson
import requests

from wikibot import login_wiki
from wikibot import read_wiki
from wikibot import write_wiki
from collaboration import COLLABORATION

STC_SOURCE = "..\\w_stc_data"
TEXT_SOURCE = "..\\w_text_data"
TEMPLATE_SOURCE = ".\\skin_template.txt"
OBTAIN = ".\\obtain\\obtain.txt"


def text_creation(class_id, time, coll_list, origin_text, theme_type):
    with open(TEMPLATE_SOURCE, "r", encoding="utf-8") as f_tem:
        template = f_tem.read().replace("|主题类型=", "|主题类型=" + theme_type)
        f_tem.close()

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
    with open(os.path.join(STC_SOURCE, "live2d_info.json"), "r", encoding="utf-8") as f_live2d:
        live2d_info = ujson.load(f_live2d)
        f_live2d.close()

    with open(OBTAIN, "r", encoding="utf-8") as f_obtain:
        skin_obtain_info = ujson.load(f_obtain)
        f_obtain.close()

    skin_obtain = {"gem": "钻石", "coin": "采购", "event": "活动", "rmb": "RMB"}

    template = template.replace("|编号=", "|编号=" + class_id)

    if time:
        template = template.replace("|实装时间=", "|实装时间=" + time)
    else:
        template = template.replace("|实装时间=", search_string(origin_text, '实装时间'))


    order = 1
    for skin in skin_info:
        if len(coll_list) and int(skin['id']) not in coll_list:
            continue
        elif skin["class_id"] != class_id:
            continue

        template = template.replace(f"|编号{order}=", f"|编号{order}={skin['id']}")
        template = template.replace(f"|人形编号{order}=", f"|人形编号{order}={skin['fit_gun']}")

        cn_name = ""
        for gun in gun_info:
            if gun["id"] == skin["fit_gun"]:
                cn_name_tem = gun_text[gun_text.find(gun["name"]) + len("gun-10000001,"):]
                cn_name = cn_name_tem[:cn_name_tem.find("\n")]
                if cn_name.endswith(" "):
                    cn_name = cn_name[:-1]
                template = template.replace(f"|人形{order}=", f"|人形{order}={cn_name}")
                template = template.replace(f"|英文{order}=", f"|英文{order}={gun['code']}")

        skin_name_tem = skin_text[skin_text.find(skin["name"]) + len("skin-10000001,") + len(cn_name) + 1:]
        skin_name = skin_name_tem[:skin_name_tem.find("\n")]
        template = template.replace(f"|名称{order}=", f"|名称{order}={skin_name}")

        skin_line_tem = skin_text[skin_text.find(skin["dialog"]) + len("skin-30000001,"):]
        skin_line = skin_line_tem[:skin_line_tem.find("\n")]
        template = template.replace(f"|台词{order}=", f"|台词{order}={skin_line}")

        live2d_sign = None
        for live2D in live2d_info:
            if live2D["skin"] == skin["id"]:
                live2d_sign = True
                if live2D["skinType"] == "1":
                    template = template.replace(f"|动态{order}=", f"|动态{order}=Live2D")
                    break
                elif live2D["skinType"] == "2":
                    template = template.replace(f"|动态{order}=", f"|动态{order}=Animated")
                    break
        if not live2d_sign:
            template = template.replace(f"|动态{order}=\n", "")

        for obtain in skin_obtain_info:
            if obtain['id'] == skin["id"]:
                template = template.replace(f"|黑卡{order}=", f"|黑卡{order}={obtain['blackcard']}")
                template = template.replace(f"|获取{order}=", f"|获取{order}={skin_obtain[obtain['obtain_info']]}")
                template = template.replace(f"|道具{order}=", f"|道具{order}={obtain['obtain_num']}")

        if template.find(f"|获取{order}=|") != -1:
            template = template.replace(f"|获取{order}=", search_string(origin_text, f"获取{order}"))
            template = template.replace(f"|道具{order}=", search_string(origin_text, f"道具{order}"))

        order += 1

    if order <= 12:
        template = template[:template.find(f"\n|编号{order}=")] + "}}"

    template = template.replace("//n", "<br>").replace("//c", ",").replace("\"", "”")
    return template


def update():
    with open(os.path.join(STC_SOURCE, "skin_class_info.json"), "r", encoding="utf-8") as f_class:
        class_info = ujson.load(f_class)
        f_class.close()
    with open(os.path.join(TEXT_SOURCE, "skin_class.txt"), "r", encoding="utf-8") as f_class_text:
        class_text = f_class_text.read()
        f_class_text.close()
    with open(os.path.join(STC_SOURCE, "skin_info.json"), "r", encoding="utf-8") as f_skin:
        skin_info = ujson.load(f_skin)
        f_skin.close()

    # 特典
    try:
        origin_text = read_wiki(the_session, url, '特典装扮')
    except:
        origin_text = ""

    special = []
    inClass = None
    for skin in skin_info:
        for skin_class in class_info:
            if skin["class_id"] == skin_class['id']:
                inClass = True
                break
        if not inClass and not 5000 <= int(skin["id"]) < 5100:
            special.append(int(skin["id"]))
        inClass = None

    content = text_creation('0', '20160520', special, origin_text, '0')
    # write_wiki(the_session, url, '特典装扮', content, '更新')
    # print(content)

    for classes in class_info:
        if classes['id'] == '52':
            continue
        if classes['id'] != '63':
            continue

        class_name_tem = class_text[class_text.find(classes["name"]) + len(f"{classes['name']}") + 1:]
        class_name = class_name_tem[:class_name_tem.find("\n")]

        if int(classes['id']) == 53:
            for coll in COLLABORATION:
                try:
                    origin_text = read_wiki(the_session, url, coll['name'])
                except:
                    origin_text = ""

                content = text_creation('53', coll['time'], coll['skins'], origin_text, classes['theme_type'])
                # write_wiki(the_session, url, coll['name'], content, '更新')
                # print(content)
        else:
            try:
                origin_text = read_wiki(the_session, url, class_name)
            except:
                origin_text = ""

            content = text_creation(classes['id'], None, [], origin_text, classes['theme_type'])
            # write_wiki(the_session, url, class_name, content, '更新')
            print(content)


def search_string(origin_text, tar):
    out_text = f'|{tar}='
    if origin_text.find(f'|{tar}=') > 0:
        obtain_1 = origin_text[origin_text.find(f'{tar}='):]
        if (obtain_1.find('|') < 0) or (obtain_1.find('\n') < obtain_1.find('|')):
            out_text = "|" + obtain_1[:obtain_1.find('\n')]
        else:
            out_text = f"|{obtain_1[:obtain_1.find('|')]}"

    return out_text


update()
