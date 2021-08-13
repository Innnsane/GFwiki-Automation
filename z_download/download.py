import os
import ujson
import UnityPy
import requests
import datetime


from PIL import Image
SOURCE = "..\\assets_web"
DESTINATION = "..\\extracted"


def get_data():
    url = ''
    headers = {
        'X-Unity-Version': '2017.4.40c1',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; MuMu Build/V417IR)',
        'Host': 'gf-cn.oss-cn-beijing.aliyuncs.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }
    r = requests.get(url + str(datetime.datetime.now().timestamp()).split('.')[0], headers=headers)
    r.raise_for_status()

    with open('.\\resData.ab', "wb") as code:
        code.write(r.content)
    return


def unpack_data():
    env = UnityPy.load('.\\resData.ab')
    for obj in env.objects:
        if obj.type == "MonoBehaviour" and obj.serialized_type.nodes:
            tree = obj.read_typetree()
            fp = '.\\resData.json'
            with open(fp, "wt", encoding="utf8") as f:
                ujson.dump(tree, f, ensure_ascii=False, indent=4)
                f.close()
    return


def download():
    with open('.\\resData.json', "r", encoding="utf8") as f:
        data = ujson.load(f)
        f.close()

    resUrl = data["resUrl"]
    headers = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; MuMu Build/V417IR)',
        'Host': 'gf-cn.cdn.sunborngame.com',
        'Connection': 'Keep-Alive',
    }

    # for title in ["passivityAssetBundles", "BaseAssetBundles", "AddAssetBundles"]:
    for title in ["passivityAssetBundles"]:
        for res in data[title]:
            print(f"Downloading {res['assetBundleName']}")
            r = requests.get(resUrl + res['resname'] + '.ab', headers=headers)
            with open(os.path.join(SOURCE, res['assetBundleName'] + '.ab'), "wb") as code:
                code.write(r.content)
                code.close()

    return


def unpack():

    for root, dirs, files in os.walk(SOURCE):
        for file_name in files:
            file_destination_folder = os.path.join(DESTINATION, file_name[:-3])
            if not os.path.exists(file_destination_folder):
                os.mkdir(file_destination_folder)

            file_path = os.path.join(root, file_name)
            env = UnityPy.load(file_path)
            print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--{file_name}')

            Texture2D_array = []

            # MonoBehaviour has pic and alpha information
            MonoBehaviour_arr = []
            for obj in env.objects:
                data = obj.read()
                if obj.type == "MonoBehaviour":
                    data_dict = data.to_dict()
                    if "arrPic" in data_dict.keys():
                        MonoBehaviour_arr.append(data_dict)

            # GameObject and recognize which is he xie
            Pic_arr = {"pic": [], "alpha": []}
            for obj in env.objects:
                if obj.type == "GameObject" and obj.container.find("he_hd") == -1:
                    for item in MonoBehaviour_arr:
                        if item["m_GameObject"]["m_PathID"] == obj.path_id:
                            Pic_arr["pic"].append(item["arrPic"][0]["m_PathID"])
                            Pic_arr["pic"].append(item["arrPic"][1]["m_PathID"])
                            Pic_arr["alpha"].append(item["arrAlphaPic"][0]["m_PathID"])
                            Pic_arr["alpha"].append(item["arrAlphaPic"][1]["m_PathID"])
                            Texture2D_array.append(Pic_arr["alpha"][0])
                            Texture2D_array.append(Pic_arr["alpha"][1])

            # Sprite can link to the relative 2D
            sprite2tex_path_array = []
            for obj in env.objects:
                data = obj.read()

                if obj.type == "Sprite" and obj.path_id in Pic_arr["pic"]:
                    sprite_path_id = obj.path_id
                    texture2d_path_id = data.m_RD.texture.path_id
                    Texture2D_array.append(texture2d_path_id)
                    sprite2tex_path_array.append({"sprite": sprite_path_id,
                                                  "texture2d": texture2d_path_id})

            # Texture2D (after Sprite)
            path_array = []
            for obj in env.objects:
                if obj.type == "Texture2D" and obj.path_id in Texture2D_array:
                    pic = obj.read()

                    link_path_id = 0
                    for link in sprite2tex_path_array:
                        if obj.path_id == link["texture2d"]:
                            link_path_id = link["sprite"]
                            break

                    path_array.append({"img": pic.image,
                                       "name": pic.name,
                                       "TextureFormat": str(pic.m_TextureFormat),
                                       "path_id": obj.path_id,
                                       "link": link_path_id})

            alpha_handle(path_array, file_destination_folder)


def alpha_handle(path_array, file_name):
    for img in path_array:
        if str(img["TextureFormat"]).endswith('Alpha8'):
            continue

        alpha_path_id = 0

        if not alpha_path_id:
            for alpha in path_array:
                if f'{img["name"]}_Alpha' == alpha["name"]:
                    alpha_path_id = alpha["path_id"]
                    output = alpha_merge(alpha["img"], img["img"])
                    output.save(os.path.join(DESTINATION, file_name, f'{img["name"]}.png'))
                    break
            if not alpha_path_id:
                img["img"].save(os.path.join(DESTINATION, file_name, f'{img["name"]}.png'))
            continue

        for img_alpha in path_array:
            if img_alpha["path_id"] == alpha_path_id:
                output = alpha_merge(img_alpha["img"], img["img"])
                output.save(os.path.join(DESTINATION, file_name, f'{img["name"]}.png'))
    return


def alpha_merge(alpha, base):
    r, g, b = base.split()[0:3]
    if alpha.width != base.width:
        alpha = alpha.resize((base.width, base.height))
    return Image.merge('RGBA', (r, g, b, alpha.split()[3]))


if __name__ == "__main__":
    # get_data()
    # unpack_data()
    # download()
    unpack()
