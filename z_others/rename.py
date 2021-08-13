import os
import ujson
import UnityPy


def unpack_data():
    env = UnityPy.load('.\\AndroidResConfigData.txt')
    for obj in env.objects:
        if obj.type == "MonoBehaviour" and obj.serialized_type.nodes:
            tree = obj.read_typetree()
            fp = '.\\AndroidResConfigData.json'
            with open(fp, "wt", encoding="utf8") as f:
                ujson.dump(tree, f, ensure_ascii=False, indent=4)
                f.close()
    return


def rename():
    with open('.\\AndroidResConfigData.json', "r", encoding="utf8") as f:
        data = ujson.load(f)
        f.close()

    for file_a in os.listdir("./"):
        if not file_a.endswith(".ab"):
            continue

        for title in ["passivityAssetBundles", "BaseAssetBundles", "AddAssetBundles"]:
            for res in data[title]:
                if file_a[:-3] == res['resname']:
                    os.renames(os.path.join("./", file_a), os.path.join("./", res['assetBundleName'] + ".ab"))
                    print(res['assetBundleName'] + ".ab")
                    break
    return


unpack_data()
rename()
