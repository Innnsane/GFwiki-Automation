import UnityPy
from avg import xlsx_to_dict
from avg import find_avg_file
from avg import show_avg_sort

AVG = "./res/asset_textavg.ab"
NGA = "./res/nga_text.txt"


def unpack_avg_ab(scenario, episode, chapter):
    avg_dict = find_avg_file(scenario, episode, chapter)

    env = UnityPy.load(AVG)

    nga = ""
    for avg in avg_dict:
        for obj in env.objects:

            data = obj.read()
            if obj.type == "TextAsset":

                if data.name == avg["file"] and avg["path"] in obj.container:
                    nga += convert_to_nga(avg["name_a"] + str(avg["name"]) + avg["name_b"], str(data.script, encoding="utf-8"))
                    break

    with open(NGA, "w", encoding='utf-8') as f:
        f.write(nga)
    print("-- 执行完成")
    return


def convert_to_nga(name, text):
    lines = text.split("\r\n")

    nga = f"[quote][collapse={name}]"
    for line in lines:
        if line.find(":\n") != -1 or line.find(":") == -1:
            continue

        speaker = None
        if line.find("<Speaker>") != -1 and line.find("</Speaker>") != -1:
            speaker = line[line.find("<Speaker>") + len("<Speaker>"):line.find("</Speaker>")]

        nga += "[quote]"
        if speaker:
            nga += f"[b]{speaker}:[/b]\n"

        line_text = line.split(':')[1].replace("+", "\n").replace("<color=#00CCFF>", "[color=blue]").replace("<color=#A9A9A9>", "[color=silver]")
        line_text = line_text.replace("<color=#AE0000>", "[color=red]").replace("<color=#EE9A49>", "[color=orange]").replace("<color=#FF34B3>", "[color=pink]").replace("</color>", "[/color]")
        line_text = line_text.replace("<size=25>", "[size=50%]").replace("<Size=35>", "[size=70%]").replace("<size=40>", "[size=75%]").replace("<Size=50>", "[size=110%]").replace("<size=50>", "[size=110%]").replace("<size=55>", "[size=120%]").replace("<Size=55>", "[size=120%]")
        line_text = line_text.replace("<size=52>", "[size=110%]").replace("<size=60>", "[size=130%]").replace("<Size=60>", "[size=130%]").replace("<size=65>", "[size=140%]").replace("<size=75>", "[size=160%]").replace("</size>", "[/size]").replace("</Size>", "[/size]")

        i = 1
        while line_text.find("<c>") != -1:
            line_text = line_text.replace("<c>", f" 选项{i}:", 1)
            i += 1

        if line_text:
            nga += f"{line_text}[/quote]"
        else:
            nga += f"[size=0%]占位[/size][/quote]"

    nga += "[/collapse][/quote]"

    return nga


def main():
    print("-- NGA剧情转换工具")
    mode = input("-- 请选择想要执行的模式：【1：全部执行】，【2：直接输入】，【3：选择输入】")
    if mode == "1":
        unpack_avg_ab([], [], [])
    elif mode == "2":
        avg_scenario_target = input("-- 请输入想要查询的【scenario】，不同的【scenario】请用【+】分隔，不输入视为全部：\n").split("+")
        avg_episode_target = input("-- 请输入想要查询的【episode】，不同的【episode】请用【+】分隔，不输入视为全部：\n").split("+")
        avg_chapter_target = input("-- 请输入想要查询的【chapter】，不同的【chapter】请用【+】分隔，不输入视为全部：\n").split("+")
        unpack_avg_ab(avg_scenario_target, avg_episode_target, avg_chapter_target)
    elif mode == "3":
        target_dict = show_avg_sort()
        unpack_avg_ab(target_dict["scenario"], target_dict["episode"], target_dict["chapter"])
    else:
        print("-- 模式错误")
        main()


main()
