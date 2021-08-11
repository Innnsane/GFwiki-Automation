import os
import ujson


STC_SOURCE = "..\\w_stc_data"
SKILL_ICON_SOURCE = "..\\extracted_save\\sprites_ui"


def doll_file():
    with open(os.path.join(STC_SOURCE, "gun_info.json"), "r", encoding="utf-8") as f_gun:
        gun_info = ujson.load(f_gun)
        f_gun.close()

    with open(os.path.join(STC_SOURCE, "battle_skill_config_info.json"), "r", encoding="utf-8") as f_skill:
        skill_info = ujson.load(f_skill)
        f_skill.close()

    array = {}
    for gun in gun_info:
        if int(gun["id"]) > 1200:
            break

        gun_update = None
        if gun['mindupdate_consume']:
            for gun_up in gun_info:
                if int(gun_up['id']) == int(gun["id"]) + 20000:
                    gun_update = gun_up

        icon = skill_icon(gun["skill1"], skill_info)
        array[icon] = ""
        if gun_update:
            icon_1 = skill_icon(gun_update["skill1"], skill_info)
            icon_2 = skill_icon(gun_update["skill2"], skill_info)
            array[icon_1] = ""
            array[icon_2] = ""

    print(array)

    for icon_name in array.keys():
        if icon_name + ".png" not in os.listdir(SKILL_ICON_SOURCE):
            print(icon_name)


def skill_icon(skill_id, skill_info):
    icon = ""
    skill_id = str(skill_id) + "01"
    for skill in skill_info:
        if int(skill["id"]) == int(skill_id):
            icon = skill['code']
            break

    return icon


doll_file()
