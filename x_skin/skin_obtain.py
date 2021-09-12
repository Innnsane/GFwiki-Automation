import os
import sys
import ujson

sys.path.append("..")
from wikibot import xlsx_dict
from wikibot import save_xlsx

STC_SOURCE = "../w_stc_data"
TEXT_SOURCE = "../w_text_data"

OBTAIN_XLSX = "./obtain/obtain.xlsx"
OBTAIN = "./obtain/obtain.txt"

GASHA = "./obtain/gasha.txt"
LIST = "./obtain/list.txt"


def skin_creation():
    # with open("./obtain_tem.txt", "r", encoding="utf-8") as f:
    #     obtain_info = ujson.load(f)
    #     f.close()
    obtain_info = xlsx_dict(OBTAIN_XLSX)
    for obtain in obtain_info:
        print(obtain)

    with open(LIST, "r", encoding="utf-8") as f_list:
        list_info = ujson.load(f_list)['list']
        f_list.close()
    with open(GASHA, "r", encoding="utf-8") as f_gasha:
        gasha_info = ujson.load(f_gasha)['reward_list']
        f_gasha.close()

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
    with open(os.path.join(STC_SOURCE, "mall_info.json"), "r", encoding="utf-8") as f_mall:
        mall_info = ujson.load(f_mall)
        f_mall.close()
    with open(os.path.join(TEXT_SOURCE, "mall.txt"), "r", encoding="utf-8") as f_mall_text:
        mall_text = f_mall_text.read()
        f_mall_text.close()

    with open(os.path.join(STC_SOURCE, "item_info.json"), "r", encoding="utf-8") as f_item:
        item_info = ujson.load(f_item)
        f_item.close()
    with open(os.path.join(TEXT_SOURCE, "item.txt"), "r", encoding="utf-8") as f_item_text:
        item_text = f_item_text.read()
        f_item_text.close()

    skin_dict = []
    for skin in skin_info:
        # 去除格林娜和原型皮肤
        if 200 < int(skin["id"]) < 300 or 5000 <= int(skin["id"]) < 5100:
            continue

        the_skin = {'id': skin["id"], 'name': '', 'dollname': '', 'blackcard': '', 'obtain_info': '', 'obtain_num': '',
                    'obtain_des': ''}
        for skin_obtain in obtain_info:
            if str(skin_obtain['id']) == str(skin["id"]):
                the_skin = {'id': str(skin_obtain["id"]), 'name': skin_obtain['name'],
                            'dollname': skin_obtain['dollname'], 'blackcard': str(skin_obtain['blackcard']),
                            'obtain_info': skin_obtain["obtain_info"], 'obtain_num': str(skin_obtain["obtain_num"]),
                            'obtain_des': skin_obtain["obtain_des"]}
                break

        cn_name = ""
        for gun in gun_info:
            if gun["id"] == skin["fit_gun"]:
                cn_name_tem = gun_text[gun_text.find(gun["name"]) + len(gun["name"]) + 1:]
                cn_name = cn_name_tem[:cn_name_tem.find("\n")]
                if cn_name.endswith(" "):
                    cn_name = cn_name[:-1]

        skin_name_tem = skin_text[skin_text.find(skin["name"]) + len(skin["name"]) + 1 + len(cn_name) + 1:]
        skin_name = skin_name_tem[:skin_name_tem.find("\n")]
        the_skin['name'] = skin_name.replace("\\n", "").replace("\"", "\\\"")
        the_skin['dollname'] = cn_name

        # info num des
        # 采购 采购币数量 无/其他描述
        # 钻石 钻石数量 礼包描述
        # RMB 人名币数量 无/其他描述
        # 活动 活动名称 是否有道具或者其他描述

        for mall_pack in mall_info:
            if mall_pack["gift"].split("-")[0] == skin['id']:
                mall_name_tem = mall_text[
                                mall_text.find(mall_pack["giftbag_name"]) + len(mall_pack["giftbag_name"]) + 1:]
                mall_name = mall_name_tem[:mall_name_tem.find("\n")]
                the_skin['obtain_des'] = mall_name + '<br>'

                if int(mall_pack["gemprice"]) != 0:
                    the_skin['obtain_info'] = 'gem'
                    the_skin['obtain_num'] = mall_pack['gemprice']
                    the_skin['obtain_des'] += '礼包内容：' + skin_name.replace("\\n", "").replace("\"", "\\\"")

                    for item_id in mall_pack['item_ids'].split(','):
                        for item in item_info:
                            if item_id.split('-')[0] == item['id']:
                                item_text_tem = item_text[
                                                item_text.find(item["item_name"]) + len(item["item_name"]) + 1:]
                                item_name = item_text_tem[:item_text_tem.find("\n")]
                                the_skin['obtain_des'] += "," + item_name + '×' + item_id.split('-')[1]

                else:
                    the_skin['obtain_info'] = 'event'
                    the_skin['obtain_des'] += '商城兑换：'

                    if len(mall_pack['itemprice'].split("-")):
                        for item in item_info:
                            if mall_pack['itemprice'].split("-")[0] == item['id']:
                                item_text_tem = item_text[
                                                item_text.find(item["item_name"]) + len(item["item_name"]) + 1:]
                                item_name = item_text_tem[:item_text_tem.find("\n")]
                                the_skin['obtain_des'] += item_name + '×' + mall_pack['itemprice'].split('-')[1]

                break

        for item in list_info:
            if item['item_type'] == '2' and item['item_id'] == skin["id"]:
                the_skin['blackcard'] = item['blackcard_exchange_cost']

                if item['is_exchange'] == "1":
                    the_skin['obtain_info'] = 'coin'
                    the_skin['obtain_num'] = item['exchange_cost']
                break

        for item_2 in gasha_info:
            if item_2['item_type'] == '2' and item_2['item_id'] == skin["id"]:
                if item_2['is_exchange'] == "1":
                    the_skin['obtain_info'] = 'coin'
                    the_skin['obtain_num'] = item_2['exchange_cost']
                break

        skin_dict.append(the_skin)

    save_xlsx(skin_dict, OBTAIN_XLSX)

    return


if __name__ == '__main__':
    skin_creation()

