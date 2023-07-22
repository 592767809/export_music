
import base64
import re
import os
import traceback
import requests
import json
from mysql3.mysql3 import SQL3
from utils.os import android_listdir, use_song_list, safe_title


def decrypt_spade_a(spade):
    spade = base64.b64decode(spade.encode())
    slat = spade[0] ^ spade[1] ^ spade[2]
    key_len = len(spade) - slat + 47
    key_ptr = bytearray(spade[1: 1 + key_len])
    v2 = 85
    v3 = 250
    v5 = 85
    for i in range(key_len):
        v6 = key_ptr[i]
        if i % 2 == 1:
            v6 = v3
            v5 = key_ptr[i]
            v3 = v2
        v7 = v3 ^ key_ptr[i]
        v8 = 0
        if i:
            v9 = i
            while v9:
                v8 += 1
                v9 &= v9 - 1
        v2 = v5
        key_ptr[i] = v7 - 21 - v8
        i += 1
        v3 = v6
    return key_ptr[1:-1].decode()


def export_file(song_name, song_suffix, song_url, song_encrypt, song_spadea):
    song_data = requests.get(song_url).content
    with open('./song/' + song_name + '.' + song_suffix, 'wb') as f:
        f.write(song_data)
    if song_encrypt:
        key = decrypt_spade_a(song_spadea)
        os.rename('./song/' + song_name + '.' + song_suffix, './song/' + song_name + 'en.' + song_suffix)
        os.system('ffmpeg.exe -decryption_key ' + key + ' -i "' + './song/' + song_name + 'en.' + song_suffix + '" -c copy -copyts -movflags +faststart -movflags +use_metadata_tags -y "' + './song/' + song_name + '.' + song_suffix + '"')
        os.remove('./song/' + song_name + 'en.' + song_suffix)


def main(ip):
    # 首先下载db数据
    file_path = '/data/data/com.luna.music/databases'
    for file_name in android_listdir(ip, file_path):
        if file_name.startswith('download_') and file_name.endswith('.db') and len(re.findall('\d+', file_name)[0]) > 2:
            url = f'http://{ip}{file_path}/{file_name}'
            response = requests.get(url).content
            with open('./db/download.db', 'wb') as f:
                f.write(response)
            break
    sql3 = SQL3('./db/download.db')
    values = sql3.query('''SELECT * FROM downloaded_track;''')
    song_list = []
    for item in values:
        item_info = json.loads(item[1])
        song_name = item_info['name'] + '-' + ','.join([each['name'] for each in item_info['artists']])
        item_info = json.loads(item[3])
        song_suffix = item_info['m_codec_type']
        song_url = item_info['m_main_url']
        song_spadea = item_info.get('m_spadea')
        song_encrypt = item_info['m_encrypt']
        song_list.append([song_name, song_suffix, song_url, song_encrypt, song_spadea])
    song_list = use_song_list(song_list)
    for song_name, song_suffix, song_url, song_encrypt, song_spadea in song_list:
        try:
            export_file(safe_title(song_name), song_suffix, song_url, song_encrypt, song_spadea)
        except:
            print(traceback.format_exc())
