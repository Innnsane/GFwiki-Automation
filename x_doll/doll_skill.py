import os
import re
import ujson

STC_SOURCE = "../w_stc_data"
TEXT_SOURCE = "../w_text_data"


def test():
    with open(os.path.join(STC_SOURCE, "battle_skill_config_info.json"), "r", encoding="utf-8") as f_skill:
        skill_info = ujson.load(f_skill)
        f_skill.close()
    with open(os.path.join(TEXT_SOURCE, "battle_skill_config.txt"), "r", encoding="utf-8") as f_skin_text:
        skill_text = f_skin_text.read()
        f_skin_text.close()

    skill_string = skill_description("技能", "801108", skill_info, skill_text)
    print(skill_string)


def skill_description(mode, skill_id, skill_info, skill_text):
    skill_mw = ""
    skill_des_array = []
    skill_cd = f""
    skill_start = f""

    skill_id = str(skill_id) + "01"
    skill_text_tem = skill_text
    for skill in skill_info:
        if int(skill_id) % 100 == 11:
            break
        if int(skill["id"]) == int(skill_id):
            skill_text_tem = skill_text_tem[skill_text_tem.find(skill["name"]) + len("battle_skill_config-110010101,"):]
            skill_name = skill_text_tem[:skill_text_tem.find("\n")]

            skill_text_tem = skill_text_tem[skill_text_tem.find(skill["description"]) + len("battle_skill_config-210010101,"):]
            skill_des = skill_text_tem[:skill_text_tem.find("\n")]
            skill_des_array.append(re.sub(r"[ ]{1,10}", " ", text_handle(skill_des)))

            skill_cd += skill["cd_time"] + ","
            skill_start += skill["start_cd_time"] + ","
            if not skill_mw:
                skill_mw = f"|{mode}名称={skill_name}\n|{mode}icon={skill['code']}\n"
            skill_id = int(skill_id) + 1

    skill_mw += f"|{mode}冷却={skill_cd[:-1]}\n|{mode}前置={skill_start[:-1]}\n"

    number_sample = re.compile("[0-9.]{1,15}[%秒倍点发范围弹量]{0,3}")
    color_sample = re.compile("<color=#[0-9a-fA-F]{6}>")
    num_string = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

    i = 0
    # 存储技能数字的数组 负责替换数字内容 是因为部分数字是提升的数字 如 zero+zero
    num_string_2 = []
    while i < 100:
        num_first = int((i - i % 10) / 10)
        num_second = int(i % 10)
        num_string_2.append(num_string[num_first] + num_string[num_second])
        i += 1

    skill_list = []
    # 用于技能描述的对比 存储技能描述相关信息的数组
    for des in skill_des_array:
        # ret 存储正则获取的字符串数组 ret_sign 表示是否有skill标识 ret_reference 表示在reference中是否有对应的ret
        this_skill = {"ret": [], "ret_sign": [], "ret_reference": [], "des": des, "des_initial": des, "none_ret_num": 0}

        # 对颜色代码进行预处理 使得不受数字识别的程序影响
        this_skill["color"] = re.findall(color_sample, this_skill["des"])
        this_skill["des"] = re.sub(color_sample, "<color-code>", this_skill["des"])

        this_skill["ret"] = re.findall(number_sample, this_skill["des"])
        this_skill["none_ret_num"] = len(this_skill["des"])
        for num in this_skill["ret"]:
            this_skill["none_ret_num"] -= len(num)

        for i in this_skill["ret"]:
            # sign-None 没有skill标记
            this_skill["ret_sign"].append(None)
            this_skill["ret_reference"].append(True)

        skill_list.append(this_skill)

    # 第一遍循环 将所有的 ret数字 转为 <ret-num>
    number = 0
    while number < len(skill_list):
        number_2 = 0
        while number_2 < len(skill_list[number]["ret"]):
            skill_list[number]["des"] = skill_list[number]["des"].replace(skill_list[number]["ret"][number_2], f"<ret_{num_string_2[number_2]}>", 1)
            number_2 += 1
        number += 1

    # 找出字符串长度最小的作为参照物 reference
    skill_reference = {"ret": skill_list[0]["ret"], "ret_sign": [], "des": skill_list[0]["des"], "des_initial": skill_list[0]["des_initial"],
                       "none_ret_num": skill_list[0]["none_ret_num"]}
    for skill in skill_list:
        if skill["none_ret_num"] < skill_reference["none_ret_num"]:
            skill_reference = {"ret": skill["ret"], "ret_sign": [], "des": skill["des"], "des_initial": skill["des_initial"],
                               "none_ret_num": skill["none_ret_num"]}

    # skill_reference["ret_sign"] 的初始化
    for i in skill_reference["ret"]:
        skill_reference["ret_sign"].append(None)

    # 第二遍循环 加第一次skill 同时对描述的增减进行处理
    number = 0
    while number < len(skill_list):
        # 方便处理 将这部分内容 copy
        skill_recognize = skill_list[number]["des"]
        skill_reference_des = skill_reference["des"]

        skill_reference_ret = []
        for ret in skill_reference["ret"]:
            skill_reference_ret.append(ret)

        count = 0
        count_inc_dec = 0
        while skill_list[number]["des"] != skill_reference_des or count < len(skill_list[number]["ret"]):
            # skill_list[number]["des"] 为输出字符串，skill_str 为当前处理的字符串，其作用仅为减少代码量，并不会改变最终结果
            skill_str = skill_list[number]["des"][:skill_list[number]["des"].find(f"<ret_{num_string_2[count]}>")]

            # skill_reference_des find skill_str 的特定字符串 - fail 缺少下一段字符串，即 skill_str 多出部分描述
            skill_str_part = skill_str[skill_str.find(f"<ret_{num_string_2[count - 1]}>") + len(f"<ret_{num_string_2[count - 1]}>"):]
            if skill_reference_des.find(skill_str_part) == -1 or len(skill_str) > len(skill_reference_des):
                # 进行字符串中字符的对比和处理，开始位置为上一个ret
                count_str = skill_str.find(f"<ret_{num_string_2[count - 1]}>")
                while count_str < len(skill_list[number]["des"]):

                    if count_str >= len(skill_reference_des) or skill_reference_des[count_str] != skill_list[number]["des"][count_str]:
                        count_str_2 = count_str
                        while count_str_2 < len(skill_list[number]["des"]):
                            if count_str >= len(skill_reference_des):
                                a = 1
                            elif skill_reference_des[count_str] == skill_list[number]["des"][count_str_2]:
                                if skill_reference_des[count_str + 1] == skill_list[number]["des"][count_str_2 + 1]:
                                    break
                            count_str_2 += 1

                        different_string = skill_list[number]["des"][count_str:count_str_2]

                        # 一旦出现相不同字符，在该多出的字符串之前添加<skill>标识，在之后添加<\\/skill>
                        # 对 skill_reference_des 中缺少的字符进行补全，该操作不影响 skill_reference["des"] ，只作用于该技能等级的循环内
                        if different_string in ["<color-code>", "</color>"]:
                            skill_reference_des = skill_reference_des[:count_str] + different_string + skill_reference_des[count_str:]
                        else:
                            skill_list[number]["des"] = skill_list[number]["des"][:count_str] + "<skill>" + skill_list[number]["des"][count_str:]
                            skill_list[number]["des"] = skill_list[number]["des"][:count_str_2 + len("<skill>")] + "<\\/skill>" + skill_list[number]["des"][count_str_2 + len("<skill>"):]
                            skill_reference_des = skill_reference_des[:count_str] + "<skill>" + different_string + "<\\/skill>" + skill_reference_des[count_str:]

                        # 当不匹配的字符串中有ret代码时，对其进行处理 即将之后的ret数字都加一定的数量从而保持连贯
                        count_num = 0
                        count_final = 0
                        count_difference = 0
                        while count_num < 99:
                            if different_string.find(f"<ret_{num_string_2[count_num]}>") != -1:
                                count_difference += 1
                                count_final = count_num
                            count_num += 1

                        count_num_2 = 99
                        while count_num_2 >= count_final:
                            skill_reference_des_tem = skill_reference_des[count_str_2 + len("<skill>"):]
                            if count_num_2 + count_difference <= 99 and skill_reference_des_tem.find(f"<ret_{num_string_2[count_num_2]}>") != -1:
                                skill_reference_des_tem = skill_reference_des_tem.replace(f"<ret_{num_string_2[count_num_2]}>", f"<ret_{num_string_2[count_num_2 + count_difference]}>", 1)
                                skill_reference_des = skill_reference_des[:count_str_2 + len("<skill>")] + skill_reference_des_tem
                            count_num_2 -= 1

                        # 当多余字符串中无额外的 ret 时，无需对ret数组操作，跳出
                        if count_difference <= 0:
                            break

                        # 为 skill_reference_ret 中缺少的部分添加 的操作
                        count_inc_dec -= count_difference
                        skill_list[number]["ret_reference"][count] = None
                        skill_reference_ret_part1 = skill_reference_ret[:count]
                        skill_reference_ret_part3 = skill_reference_ret[count:]
                        if type(skill_list[number]["ret"][count]) == list:
                            skill_reference_ret_part2 = skill_list[number]["ret"][count]
                        else:
                            skill_reference_ret_part2 = [skill_list[number]["ret"][count]]
                        skill_reference_ret = skill_reference_ret_part1 + skill_reference_ret_part2 + skill_reference_ret_part3

                        break
                    count_str += 1

                # 如果字符超过则代表 有部分描述是完全多出的，直接复制
                if len(skill_str) > len(skill_reference_des):
                    different_string = skill_list[number]["des"].replace(skill_reference_des, "")
                    skill_list[number]["des"] = skill_reference_des + "<skill>" + different_string + "<\\/skill>"
                    skill_reference_des = skill_list[number]["des"]

                    # 处于最后的位置，只需考虑ret数组的增加即可
                    count_num = 0
                    while count_num < 99:
                        if different_string.find(f"<ret_{num_string_2[count_num]}>") != -1:
                            count_inc_dec -= 1
                        count_num += 1

                    count_num_2 = len(skill_reference_ret)
                    while count_num_2 < len(skill_list[number]["ret"]):
                        skill_reference_ret.append(skill_list[number]["ret"][count_num_2])
                        count_num_2 += 1

            # if.如果 reference 等于该个体那么应当放到最后处理，及在其他等级已确定效果有提升 同时如果因为最后字符串的处理导致溢出那么将跳过
            # elif.如果效果有提升 else.效果没有提升
            # print(number, count, skill_list[number]["ret"][count], skill_reference_ret[count])
            if skill_reference["des_initial"] == skill_recognize or count >= len(skill_list[number]["ret"]):
                count += 1
                continue

            elif skill_list[number]["ret"][count] != skill_reference_ret[count]:
                skill_list[number]["ret_sign"][count] = True
                skill_reference["ret_sign"][count + count_inc_dec] = True
                skill_reference_des = skill_reference_des.replace(f"<ret_{num_string_2[count]}>", f"<skill><ret_{num_string_2[count]}><\\/skill>", 1)
                skill_list[number]["des"] = skill_list[number]["des"].replace(f"<ret_{num_string_2[count]}>", f"<skill><ret_{num_string_2[count]}><\\/skill>", 1)

            else:
                skill_list[number]["ret_sign"][count] = None
            count += 1
        number += 1

    # 第三遍循环 加第二次skill 保证所有的<ret-num>拥有同等的待遇即有skill都有，没有都没有 此时skill增加完毕
    number = 0
    while number < len(skill_list):
        count_2 = 0
        count_inc_dec = 0
        while count_2 < len(skill_list[number]["ret"]):
            # 如果 该 数字 与 reference 不同， 同时 有其他等级的描述 与 reference 不同， 此时也需要进行处理
            if (not skill_list[number]["ret_reference"][count_2]) or count_2 + count_inc_dec >= len(skill_reference["ret_sign"]):
                count_inc_dec -= 1
            elif not skill_list[number]["ret_sign"][count_2] and skill_reference["ret_sign"][count_2 + count_inc_dec]:
                skill_list[number]["des"] = skill_list[number]["des"].replace(f"<ret_{num_string_2[count_2]}>", f"<skill><ret_{num_string_2[count_2]}><\\/skill>")
            count_2 += 1

        number += 1

    # 第四遍循环 将所有的 <ret-num> 逆向回 ret数字
    number = 0
    while number < len(skill_list):
        count_3 = 0
        while count_3 < len(skill_list[number]["ret"]):
            skill_list[number]["des"] = skill_list[number]["des"].replace(f"<ret_{num_string_2[count_3]}>", skill_list[number]["ret"][count_3])
            count_3 += 1

        number += 1

    # 第五遍循环 处理 color-code 并生成 mw 代码
    number = 0
    while number < len(skill_list):
        color_ret = skill_list[number]["color"]
        for color_num in color_ret:
            skill_list[number]["des"] = skill_list[number]["des"].replace("<color-code>", "<span style=\\\"color:#" + color_num[len("<color=#"):-1] + "\\\">", 1)
        skill_list[number]["des"] = skill_list[number]["des"].replace('</color>', '<\\/span>')
        skill_mw += f"|{mode}描述{number + 1}={skill_list[number]['des']}\n"
        number += 1

    return skill_mw


def text_handle(text):
    text = text.replace("//c", "，").replace("//n", "<br>").replace(" <br>", "<br>").replace("(", "（").replace(")", "）")
    text = text.replace("\"", "\\\"").replace("|", "{{!}}").replace(":", "：").replace(",", "，").replace(";", "；")
    return text


if __name__ == '__main__':
    test()
