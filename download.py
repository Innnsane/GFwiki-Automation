# %%
import os
import shutil
import unitypack
import pyjson5
from urllib import request
from Crypto.Hash import MD5
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
import base64
import re
import logging
from pySmartDL import SmartDL
import wget
from multiprocessing import Pool
import argparse
import socket


# %%
parser = argparse.ArgumentParser()
parser.add_argument('region',choices=['cn','tw','kr','jp','en'])
parser.add_argument('-l','--logging',choices=logging._nameToLevel.keys(),default='WARNING')
args = parser.parse_args()
logging.basicConfig(level=args.logging,force=True,format='%(asctime)s %(levelname)s:%(message)s')
socket.setdefaulttimeout(30)

# %%
class Downloader:
    def __init__(self, region='tw'):
        self.region = region
        with open('hosts.json5','r') as f:
            hosts = pyjson5.load(f)
        self.hosts = hosts[region]
        self.get_version()
        self.output_dir = f'./Asset_raw/{region}'
        # shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_version(self):
        request_url = self.hosts['game_host'] + '/Index/version'
        logging.info(f'requesting {request_url}')
        response = request.urlopen(request_url)
        self.version = pyjson5.loads(response.read().decode())
        self.dataVersion = self.version["data_version"]
        self.clientVersion = self.version["client_version"]
        self.minversion = round(eval(self.clientVersion)/100) * 10
        self.abVersion = self.version["ab_version"]

    def download_res_config(self):
        key = "kxwL8X2+fgM="
        iv = "M9lp+7j2Jdwqr+Yj1h+A"

        bkey = base64.standard_b64decode(key)
        biv = base64.standard_b64decode(iv)
        fname = f"{self.minversion}_{self.abVersion}_AndroidResConfigData"

        en = get_des_encrypted(fname,bkey,biv[:8])
        res_config = base64.standard_b64encode(en).decode('utf-8')
        res_config = re.sub(r"[^a-zA-Z0-9]","",res_config)+'.txt'
        download(self.get_asset_url(res_config),f'{self.output_dir}/AndroidResConfigData')

    def download_resource(self):
        with open(f'{self.output_dir}/AndroidResConfigData','rb') as f:
            res_data = unitypack.load(f)
        for asset in res_data.assets:
            for object in asset.objects.values():
                if object.type == "AssetBundleDataObject":
                    data = object.read()
                    res_url = data['resUrl']
                    tasks = []
                    for k in data.keys():
                        if 'AssetBundles' in k:
                            subdir = os.path.join(self.output_dir,k)
                            os.makedirs(subdir,exist_ok=True)
                            tasks += [(f'{res_url}{resource["resname"]}.ab',f'{subdir}/{resource["assetBundleName"]}.ab') for resource in data[k]]
                    pool = Pool(processes=16)
                    max_tasks = len(tasks)
                    cnt = 0
                    for i in pool.imap_unordered(download_multitask, tasks): 
                        cnt += 1
                        logging.info(f'progress {cnt:>4}/{max_tasks:>4}, downloaded {i}')
                    
                    for k in data.keys():
                        if 'AssetBundles' in k:
                            subdir = os.path.join(self.output_dir,k)
                            for f in os.listdir(subdir):
                                if os.path.splitext(f)[-1] != '.ab':
                                    os.remove(os.path.join(subdir,f))

    def get_asset_url(self,asset):
        return self.hosts['asset_host']+'/'+asset
    

# %%
def download(url, path):
    while True:
        try:
            if not os.path.exists(path):
                request.urlretrieve(url,path+'.tmp')
                os.rename(path+'.tmp',path)
        except:
            logging.warning(f'download {url} failed, retrying')
            continue
        else:
            break
    return path

def download_multitask(x):
    return download(*x)


# %%
def get_md5_hash(input:str):
    data = MD5.MD5Hash(input.encode('utf-8')).digest()
    return ('{:02x}'*len(data)).format(*data)

def get_des_encrypted(data, key, iv):
    des = DES.new(key=key,iv=iv,mode=DES.MODE_CBC)
    return des.encrypt(pad(data.encode('utf-8'),block_size=des.block_size))

# %%
if __name__=='__main__':
    downloader = Downloader(region=args.region)
    downloader.download_res_config()
    downloader.download_resource()
