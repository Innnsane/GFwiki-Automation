# %%
import os
import ujson
import shutil
import UnityPy
import datetime

from PIL import Image
from datetime import *
from shutil import copyfile
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('region',choices=['cn','tw','kr','jp','en'])
args = parser.parse_args()
region = args.region

SOURCE = f"Asset_raw/{region}"
PREFABS = f"prefabs/{region}"
DESTINATION = f"extracted/{region}"
SAVED = f"extracted_save/{region}"
UPDATE = f"extracted_up/{region}"
os.makedirs(SOURCE,exist_ok=True)
os.makedirs(PREFABS,exist_ok=True)
os.makedirs(DESTINATION,exist_ok=True)
os.makedirs(SAVED,exist_ok=True)
os.makedirs(UPDATE,exist_ok=True)


def find_alpha_info():
    for root, dirs, files in os.walk(SOURCE):
        for file in files:
            if file.find("prefab") != -1:
                shutil.copy(os.path.join(root, file), os.path.join(PREFABS, file))

    data_json = []
    for root, dirs, files in os.walk(PREFABS):
        for file in files:
            if file.find("prefab") != -1:
                print(file)
                file_path = os.path.join(root, file)
                env = UnityPy.load(file_path)

                for obj in env.objects:
                    if obj.type.name == "MonoBehaviour":
                        data = obj.read()

                        type_tree = data.read_typetree()
                        if 'pic' in type_tree and 'picAlpha' in type_tree:
                            count = 0
                            while count < len(type_tree['pic']):
                                if count >= len(type_tree['picAlpha']):
                                    break

                                if count >= len(type_tree['orderScale']):
                                    order_scale = {'picname': '',
                                                   'scale': 1,
                                                   'avgOffset': {'x': 0, 'y': 0}}
                                else:
                                    order_scale = type_tree['orderScale'][count]

                                data_json.append({"pic": type_tree['pic'][count],
                                                  "picAlpha": type_tree['picAlpha'][count],
                                                  "orderScale": order_scale})
                                count += 1

    json_path = os.path.join(PREFABS, "alpha_data.json")
    with open(json_path, "w", encoding='utf-8') as f:
        f.write(ujson.dumps(data_json))
        f.close()

# %%
def alpha_handle(path_array, file_name):
    for img in path_array:
        if str(img["TextureFormat"]).endswith('Alpha8'):
            continue

        path = os.path.join(PREFABS, "alpha_data.json")
        with open(path, "r", encoding='utf-8') as f:
            path_json = ujson.load(f)
            f.close()

        alpha_path_id = 0
        for path_id in path_json:
            if path_id["pic"]["m_PathID"] == img["link"]:
                alpha_path_id = path_id["picAlpha"]["m_PathID"]
                break

        if not alpha_path_id:
            for alpha in path_array:
                if f'{img["name"]}_Alpha' == alpha["name"]:
                    alpha_path_id = alpha["path_id"]
                    output = alpha_merge(alpha["img"], img["img"])
                    output.save(os.path.join(file_name, f'{img["name"]}.png'))
                    break
            if not alpha_path_id:
                img["img"].save(os.path.join(file_name, f'{img["name"]}.png'))
            continue

        for img_alpha in path_array:
            if img_alpha["path_id"] == alpha_path_id:
                output = alpha_merge(img_alpha["img"], img["img"])
                output.save(os.path.join(file_name, f'{img["name"]}.png'))
    return

# %%
def alpha_merge(alpha, base):
    r, g, b = base.split()[0:3]
    if alpha.width != base.width:
        alpha = alpha.resize((base.width, base.height))
    return Image.merge('RGBA', (r, g, b, alpha.split()[3]))


def unpack_all_assets():
    print(f'--Begin unpacking--')

    for root, dirs, files in os.walk(SOURCE):
        for file_name in files:
            if file_name.find("prefab") != -1:
                continue
            if file_name.find("live2d") != -1:
                continue

            file_destination_folder = os.path.join(DESTINATION, file_name[:-3])
            if not os.path.exists(file_destination_folder):
                os.mkdir(file_destination_folder)

            file_path = os.path.join(root, file_name)
            env = UnityPy.load(file_path)
            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--{file_name}')

            # spine file
            if file_name.find("spine") != -1:

                dorm_name = ""
                for obj in env.objects:
                    data = obj.read()
                    if 'name' not in dir(data):
                        continue
                    if data.name.endswith(".skel"):
                        if not dorm_name and data.name[:1] == "R":
                            dorm_name = data.name
                        elif dorm_name and len(data.name) > len(dorm_name) and data.name[:1] == "R":
                            dorm_name = data.name
                dorm_name = dorm_name[:3]

                for obj in env.objects:
                    if obj.type.name in ['Sprite','MonoBehaviour','Shader']:
                        continue

                    data = obj.read()
                    if 'name' not in dir(data):
                        continue
                    export = None
                    spine_file_name = data.name

                    if obj.type.name == 'Texture2D':
                        if dorm_name == "" or data.name.startswith(dorm_name[1:]):
                            spine_file_name = data.name + "_chibi_spritemap.png"
                        elif data.name.startswith(dorm_name):
                            spine_file_name = data.name[1:] + "_chibi_dorm_spritemap.png"
                        else:
                            spine_file_name = data.name + ".png"
                        data.image.save(os.path.join(file_destination_folder, spine_file_name))

                    elif obj.type.name == 'TextAsset' and data.name.endswith(".skel"):
                        if dorm_name == "" or data.name.startswith(dorm_name[1:]):
                            spine_file_name = data.name.replace(".skel", "_chibi_skel.skel")
                        elif data.name.startswith(dorm_name):
                            spine_file_name = data.name[1:].replace(".skel", "_chibi_dorm_skel.skel")
                        export = data.script

                    elif obj.type.name == 'TextAsset' and data.name.endswith(".atlas"):
                        if dorm_name == "" or data.name.startswith(dorm_name[1:]):
                            spine_file_name = data.name.replace(".atlas", "_chibi_atlas.txt")
                        elif data.name.startswith(dorm_name):
                            spine_file_name = data.name[1:].replace(".atlas", "_chibi_dorm_atlas.txt")
                        export = data.script

                    if export:
                        with open(os.path.join(file_destination_folder, spine_file_name), "wb") as f:
                            f.write(export)

                continue

            # Sprite(not unpack) and TextAsset
            sprite2tex_path_array = []
            for obj in env.objects:
                
                data = obj.read()
                if 'name' not in dir(data):
                    continue

                if obj.type.name == 'TextAsset':
                    with open(os.path.join(file_destination_folder, f"{data.name}.txt"), "wb") as f:
                        f.write(data.script)

                if obj.type.name == 'Sprite':
                    sprite_path_id = obj.path_id
                    texture2d_path_id = data.m_RD.texture.path_id
                    sprite2tex_path_array.append({"sprite": sprite_path_id,
                                                  "texture2d": texture2d_path_id})

            # Texture2D (after Sprite)
            path_array = []
            for obj in env.objects:
                if obj.type.name == 'Texture2D':
                    pic = obj.read()
                    if pic.name == 'Font Texture':
                        continue
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

    print(f'--End unpacking--')
    return


def delete_before():
    shutil.rmtree(DESTINATION)
    os.mkdir(DESTINATION)

def remove_empty():
    for dir in os.listdir(DESTINATION):
        if len(os.listdir(os.path.join(DESTINATION,dir))) == 0:
            shutil.rmtree(os.path.join(DESTINATION,dir))

def compare_and_save():
    target = os.path.join(UPDATE, datetime.now().strftime(r"%Y-%m-%d-%H-%M-%S"))
    os.makedirs(target)

    for file_name in os.listdir(DESTINATION):

        if os.path.exists(os.path.join(SAVED, file_name)):
            for file in os.listdir(os.path.join(DESTINATION, file_name)):

                path_1 = os.path.join(DESTINATION, file_name, file)
                path_2 = os.path.join(SAVED, file_name, file)

                if not os.path.exists(os.path.join(SAVED, file_name, file)):
                    copyfile(path_1, path_2)

                    if not os.path.exists(os.path.join(target, file_name)):
                        os.makedirs(os.path.join(target, file_name))
                    copyfile(path_1, os.path.join(target, file_name, file))
                    print("new file", f'{file} in {file_name}')

                elif os.stat(path_1).st_size == os.stat(path_2).st_size:
                    continue

                else:
                    os.remove(path_2)
                    copyfile(path_1, path_2)

                    if not os.path.exists(os.path.join(target, file_name)):
                        os.makedirs(os.path.join(target, file_name))
                    copyfile(path_1, os.path.join(target, file_name, file))
                    print("update file", f'{file} in {file_name}')
        else:
            os.makedirs(os.path.join(SAVED, file_name))
            os.makedirs(os.path.join(target, file_name))
            files = os.listdir(os.path.join(DESTINATION, file_name))
            for f in files:
                shutil.copyfile(os.path.join(DESTINATION, file_name, f), os.path.join(SAVED, file_name, f))
                shutil.copyfile(os.path.join(DESTINATION, file_name, f), os.path.join(target, file_name, f))
            print("new folder", f'{file_name}')

# %%
delete_before()
find_alpha_info()
unpack_all_assets()
remove_empty()
compare_and_save()


# %%
