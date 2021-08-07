import os
import ujson

TEXT = ".\\file"


def get():
    nga = ""

    for file_name in os.listdir(TEXT):
        path = os.path.join(TEXT, file_name)

        nga += f"[quote][collapse={file_name.replace('.txt', '')}]"
        with open(path, "r", encoding='utf-8') as f:
            lines = f.readlines()

            for line in lines:
                if line.find(":\n") != -1 or line.find(":") == -1:
                    continue

                if line.find("<Speaker>") != -1 and line.find("</Speaker>") != -1:
                    speaker = line[line.find("<Speaker>") + len("<Speaker>"):line.find("</Speaker>")]

                nga += "[quote]"
                if speaker:
                    nga += f"[b]{speaker}:[/b]\n"

                line_text = line.split(':')[1].replace("+", "\n").replace("<color=#00CCFF>", "[color=blue]").replace("<color=#A9A9A9>", "[color=silver]").replace("<color=#AE0000>", "[color=red]")
                line_text = line_text.replace("</color>", "[/color]").replace("<size=25>", "[size=50%]").replace("<size=60>", "[size=130%]").replace("<Size=50>", "[size=110%]")
                line_text = line_text.replace("<size=50>", "[size=110%]").replace("<size=55>", "[size=120%]").replace("</size>", "[/size]")
                nga += f"{line_text}[/quote]"

            f.close()
        nga += "[/collapse][/quote]"
    print(nga)


get()
