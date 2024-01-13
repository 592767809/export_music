
import json
import zipfile
import requests
import traceback
from io import BytesIO
from mysql3.mysql3 import SQL3
from utils.os import android_listdir, use_song_list, safe_title


def main(ip):
    # 首先下载db数据
    file_path = '/data/data/com.join.android.app.mgsim.wufun/databases'
    for file_name in android_listdir(ip, file_path):
        if file_name == 'mgdb':
            url = f'http://{ip}{file_path}/{file_name}'
            response = requests.get(url).content
            with open('./db/mgdb.db', 'wb') as f:
                f.write(response)
    sql3 = SQL3('./db/mgdb.db')
    values = sql3.query('''SELECT showName, gameZipPath, sp_tag_info_s FROM downloadtask where sp_tag_info_s is not null;''')
    song_list = []
    for item in values:  # 可能需要过滤一些东西
        song_list.append(item)
    song_list = use_song_list(song_list)
    for showName, gameZipPath, sp_tag_info_s in song_list:
        url = f'http://{ip}/{gameZipPath}'
        response = requests.get(url)
        if response.status_code != 200:
            print('下载游戏失败：' + showName)
            continue
        song = response.content
        if gameZipPath.endswith('.zip'):
            file = zipfile.ZipFile(BytesIO(song), 'r')
            with file.open(file.filelist[0]) as source:
                song = source.read()
        info = json.loads(sp_tag_info_s)
        if info['model']['name'] == 'GBA':
            with open('./song/' + showName + '.gba', 'wb') as f:
                f.write(song)
        elif info['model']['name'] == 'NDS':
            with open('./song/' + showName + '.nds', 'wb') as f:
                f.write(song)
        else:
            print('未知的文件类型：' + info['model']['name'])
