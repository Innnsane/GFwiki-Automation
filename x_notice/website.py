import os
import time
import ujson
import datetime
import requests

SAVE = "./save.json"
SRC = "./announcement"


def get(url):
    info = requests.get(
            url,
            params={
                "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
            },
            timeout=30,
        )
    info.raise_for_status()
    return info.json()


def save_all_site():
    site_list = get("https://gfcn-webserver.sunborngame.com/website/news_list/3?page=0&limit=1000")['data']['list']
    with open(SAVE, "w", encoding='utf-8') as f:
        ujson.dump(site_list, f)
    return


def save_all_announcement():
    with open(SAVE, "r", encoding='utf-8') as f:
        site_list = ujson.load(f)

    for site in site_list:
        site_content = get(f"https://gfcn-webserver.sunborngame.com/website/news/{str(site['Id'])}")['data']

        file_name = f"{str(site_content['Id'])}_{site_content['Title'].replace(':', '')}.txt"
        with open(os.path.join(SRC, file_name), "w") as f:
            ujson.dump(site_content, f)

        print(site_content['Title'], "accomplished")
        time.sleep(2)


def show():
    for file in os.listdir(SRC):
        with open(os.path.join(SRC, file), "r", encoding='utf-8') as f:
            announcement = ujson.load(f)
        print(announcement)


def check():
    file_date_list = {}
    for file in os.listdir(SRC):
        with open(os.path.join(SRC, file), "r", encoding='utf-8') as f:
            announcement = ujson.load(f)
        if announcement['Date'].split(" ")[0] not in file_date_list.keys():
            file_date_list[announcement['Date'].split(" ")[0]] = 1
        else:
            file_date_list[announcement['Date'].split(" ")[0]] += 1

    for key in file_date_list:
        print(key, file_date_list[key])


if __name__ == "__main__":
    # save_all_site()
    # save_all_announcement()
    # show()
    check()

