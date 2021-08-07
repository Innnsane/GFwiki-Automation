import os

TEXT = ".\\w_text_data"
AVG = ".\\w_avg_data"
LUA = ".\\w_lua_data"
DATA = ".\\w_stc_data"
WORD = "月下庆宴"


def search(source):
    for file_name in os.listdir(source):
        path = os.path.join(source, file_name)
        try:
            with open(path, "r", encoding='utf-8') as f:
                tar = f.read()
                f.close()
        except:
            continue

        if tar.find(WORD) != -1:
            print(source, file_name)


search(TEXT)
# search(AVG)
# search(LUA)
# search(DATA)
