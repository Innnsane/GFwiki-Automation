import os
import ujson
from avg import xlsx_dict
from avg_lines import pic_info_save
from avg_lines import pic_info_get

STC_SOURCE = "../w_stc_data"
AVG_PIC_INFO = "./res/pic_info.xlsx"


def check():
    gun_code = []
    with open(os.path.join(STC_SOURCE, "gun_info.json"), "r", encoding="utf-8") as f_gun:
        gun_info = ujson.load(f_gun)
        f_gun.close()

    for gun in gun_info:
        gun_code.append(gun["code"])

    pic_info_get()
    pic_info_list = xlsx_dict(AVG_PIC_INFO)

    for pic_info in pic_info_list:
        if not pic_info["code"] and pic_info["pic"][:pic_info["pic"].find("(")].replace("Mod", "") in gun_code:
            pic_info["code"] = pic_info["pic"][:pic_info["pic"].find("(")].replace("Mod", "")

    pic_info_save(pic_info_list)
    return


if __name__ == '__main__':
    check()

