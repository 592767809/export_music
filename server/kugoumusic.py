
import os
import traceback
import requests
from mysql3.mysql3 import SQL3
from utils.os import use_song_list, android_exists, android_download


def export_file(song_name, song_suffix, file_url):
    if os.path.exists('./song/' + song_name + '.' + song_suffix):
        print('文件已存在：./song/' + song_name + '.' + song_suffix)
        return
    response = requests.get(file_url).content
    with open('./song/' + song_name + '.' + song_suffix, 'wb') as f:
        f.write(response)
    print('导出成功：./song/' + song_name + '.' + song_suffix)


def main(ip):
    # 首先下载db数据
    android_download(ip, '/data/data/com.kugou.android/databases/kugou_music_phone_v7.db', './db/kugou_music_phone_v7.db')
    if android_exists(ip, '/data/data/com.kugou.android/databases/kugou_music_phone_v7.db-wal'):
        android_download(ip, '/data/data/com.kugou.android/databases/kugou_music_phone_v7.db-wal', './db/kugou_music_phone_v7.db-wal')
        android_download(ip, '/data/data/com.kugou.android/databases/kugou_music_phone_v7.db-shm', './db/kugou_music_phone_v7.db-shm')
    sql3 = SQL3('./db/kugou_music_phone_v7.db')
    values = sql3.query('''SELECT downloadurl, temppath FROM file_downloading where temppath like '%.kgm%' or temppath like '%.flac%';''')
    song_list = []
    for file_url, file_path in values:
        song_name, song_suffix = sql3.query(f'SELECT musicname, extname FROM file where filepath="{file_path}";')[0]
        song_list.append([song_name, song_suffix, file_url])
    song_list = use_song_list(song_list)
    for song_name, song_suffix, file_url in song_list:
        try:
            export_file(song_name, song_suffix, file_url)
        except:
            print(traceback.format_exc())
