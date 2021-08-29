import os
import math
import ujson
import UnityPy
import pandas as pd
from pandas import ExcelWriter
from avg_name import xlsx_to_dict

STC_SOURCE = "../w_stc_data"
TEXT_SOURCE = "../w_text_data"
AVG = "./asset_textavg.ab"
NAME = "./name.xlsx"
JSON = "./name.json"


def main(episode, chapter):
    if not os.path.exists(NAME):
        print("no xlsx")
        return

    out_string = ""
    for avg in xlsx_to_dict():
        if avg["episode"] == episode and avg["chapter"] == chapter and avg["name"]:
            out_string += "{{剧情选项|"
            if avg["name_a"]:
                out_string += "{{角标|" + avg["name_a"] + "}}"

            out_string += str(avg["name"])

            if avg["name_b"]:
                out_string += "{{角标|" + avg["name_b"] + "}}"

            out_string += "|AVG" + avg["file"] + ".txt}}"

    print(out_string)


main("-48", "1")

