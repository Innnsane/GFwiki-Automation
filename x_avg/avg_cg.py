import os

STC_SOURCE = "..\\w_stc_data"
TEXT_SOURCE = "..\\w_text_data"
AVG_SOURCE = "..\\w_avg_data"
TEMPLATE = "./res/mw_bg_cg.txt"


def get_cg_info():
    template = ""
    with open(os.path.join(AVG_SOURCE, "profiles.txt"), "r", encoding="utf-8") as f:
        text_list = f.readlines()

        count = 0
        for i in text_list:
            template += "{{#ifeq:{{{1}}}|" + str(count) + "|" + i.replace("\n", "") + "|}}"
            count += 1

    with open(TEMPLATE, "w", encoding="utf-8") as f_w:
        f_w.write(template)


get_cg_info()
