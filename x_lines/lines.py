import os
import ujson

TEXT = "..\\x_avg\\file"
TEXT_M = "..\\x_lines\\jashin"
JSON = "..\\x_lines\\line.json"


def save(sp_json):
    sp_arr = []
    for key in sp_json.keys():
        sp_arr.append({"speaker": key, "number": sp_json[key]})

    with open(JSON, "w", encoding='utf-8') as f:
        ujson.dump(sp_arr, f)

    display(sp_arr)
    return


def display(sp_arr):
    i = 6000
    while i > 0:
        this_num = ""
        for num in sp_arr:
            if num['number'] == i:
                this_num += num['speaker'] + "，"

        if this_num:
            print(f"[{i}]\n", this_num[:-1])
        i -= 1


def get():
    sp_json = {}

    for file_name in os.listdir(TEXT_M):
        path = os.path.join(TEXT_M, file_name)

        with open(path, "r", encoding='utf-8') as f:
            lines = f.readlines()

            for line in lines:
                if line.find("<Speaker>") == -1:
                    continue

                if line.find("<Speaker></Speaker>") != -1:
                    speaker = "旁白"

                elif line.find("<Speaker>") != -1 and line.find("</Speaker>") != -1:
                    speaker = line[line.find("<Speaker>") + len("<Speaker>"):line.find("</Speaker>")]

                if speaker not in sp_json.keys():
                    sp_json[speaker] = 1
                else:
                    sp_json[speaker] += 1

            f.close()
    save(sp_json)

    num = 0
    for key in sp_json.keys():
        num += int(sp_json[key])
    print(num)


get()

