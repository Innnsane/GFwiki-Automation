import os
import ujson
import datetime
import subprocess
import pandas as pd
from pandas import ExcelWriter

from datetime import *


DATA_GETTER = "./"
STC_DATA = "../../w_stc_data"
STC_UPDATE = "../stc_update"
EXCEL_DATA = "../stc_excel"


def initial_sub_call():
    print("DataGetter start")
    subprocess.call(os.path.join(DATA_GETTER, "DataGetter.exe"))
    print("DataGetter end")
    return


def data_store():
    diff_text = []
    with open(os.path.join(DATA_GETTER, "allcatchdata.json"), "r", encoding='utf-8') as f_read:
        data_lines = f_read.readlines()

        for line in data_lines:
            data_file_name = line[(line.index('"') + 1):(line.index(':') - 1)]
            data_file_path = os.path.join(STC_DATA, f"{data_file_name}.json")
            data_file_content = line[(line.index('[') + 0):-2]

            is_repeat = 0
            num_count = 0
            while num_count < len(diff_text):
                if diff_text[num_count]["name"] == data_file_name:
                    is_repeat = 1
                    break
                num_count += 1
            if is_repeat:
                continue

            # if former exists, differ the update of stc
            if os.path.exists(data_file_path):
                with open(data_file_path, "r", encoding='utf-8') as f_differ:
                    data_former = ujson.load(f_differ)
                    diff_array = compare_data(data_former, ujson.loads(data_file_content))
                    diff_text += [{"name": data_file_name, "data": diff_array}]
                    f_differ.close()

                if len(diff_array):
                    with open(data_file_path, "w", encoding='utf-8') as f_write:
                        f_write.write(data_file_content)
                        f_write.close()

            # if former doesn't exist, created file
            else:
                with open(data_file_path, "w", encoding='utf-8') as f_write:
                    f_write.write(data_file_content)
                    f_write.close()
                diff_array = ujson.loads(data_file_content)
                diff_text += [{"name": data_file_name, "data": diff_array}]

            dict_to_excel({"name": data_file_name, "data": ujson.loads(data_file_content)})

            print(data_file_name, len(ujson.loads(data_file_content)))
        f_read.close()

        # push, print, save the update data
        diff_json = []
        stc_update_file = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print(f'\n**************** {stc_update_file} update ****************')
        for diff_line in diff_text:
            if len(diff_line["data"]):
                diff_json.append(diff_line)
                print(diff_line["name"], len(diff_line["data"]))

        if diff_json:
            with open(os.path.join(STC_UPDATE, f"stc-up_{stc_update_file}.json"), "w", encoding='utf-8') as f_update:
                f_update.write(ujson.dumps(diff_json))
                f_update.close()

    return


def compare_data(src_data, dst_data):
    count = 0
    noise_data = []
    while count < len(dst_data):
        is_differ = 1

        if not len(noise_data):
            count_2 = count
        else:
            count_2 = count - len(noise_data)

        while count_2 < len(src_data):
            for key in dst_data[count]:
                if src_data[count_2].get(key, "NON0N") == "NON0N":
                    is_differ = 1
                    break
                if src_data[count_2][key] != dst_data[count][key]:
                    is_differ = 1
                    break
                is_differ = 0

            if not is_differ:
                break
            count_2 = count_2 + 1

        if is_differ:
            noise_data += [dst_data[count]]
        count = count + 1

    return noise_data


def dict_to_excel(stc_dict):
    with ExcelWriter(os.path.join(EXCEL_DATA, f"{stc_dict['name']}.xlsx")) as writer:
        data = pd.DataFrame.from_dict(stc_dict["data"])
        data.to_excel(writer, sheet_name=stc_dict["name"], index=None)


initial_sub_call()
data_store()
