import pyvips
import boto3
from boto3.session import Session
import os
import urllib.parse
import json

def generateNewKey(key):
    dirname = os.path.dirname(key)
    if dirname != "":
        dirname += "/"
    filename = os.path.splitext(os.path.basename(key))[0]
    iiif_key = dirname + filename + ".tif"
    return iiif_key

def handler(event, context):
    if "profile" in os.environ:
        session = Session(profile_name=os.environ["profile"])
    else:
        session = boto3
    client = session.client('s3')

    # パラメータ
    ## eventbrideの場合
    if "detail" in event:
        param = event["detail"]
    else:
        param = event['Records'][0]['s3']
    
    key = urllib.parse.unquote_plus(param['object']['key'], encoding='utf-8')
    bucket_name = param['bucket']['name']
    tmpkey = key.replace('/', '')
    download_path = '/tmp/{}'.format(tmpkey)

    # ダウンロード
    client.download_file(bucket_name, key, download_path)

    # 変換
    ins = pyvips.Image.new_from_file(download_path)
    converted_path = download_path + ".tif"
    image = ins.tiffsave(converted_path, 
        tile=True, 
        compression='jpeg', 
        pyramid=True,
        tile_width=256,
        tile_height=256)
        

    # アップロード
    iiif_key = generateNewKey(key)
    iiif_bucket_name = os.environ["iiif_bucket_name"]
    client.upload_file(converted_path, iiif_bucket_name, iiif_key)

if __name__ == '__main__':
    # サンプルデータ
    with open('test.json', mode='rt', encoding='utf-8') as file:
        test = json.load(file)

    # 環境変数
    os.environ['profile'] = test["profile"]
    os.environ["iiif_bucket_name"] = test["iiif_bucket_name"]

    # 引数のサンプル
    event = test["event_s3"] # test["event_bridge"]

    handler(event, None)