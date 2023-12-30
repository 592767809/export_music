
import os
import json
import requests
import traceback
from mysql3.mysql3 import SQL3
from utils.util import decrypt_spade_a
from utils.os import android_listdir, use_song_list, safe_title


def get_download_info(video_id, download_values):
    for download_info in download_values:
        download_info = json.loads(download_info[0])
        if video_id == download_info['base_json']['vid']:
            return download_info


def export_file(video_path, audio_path, lesson_title, video_model, download_path, ip):
    if os.path.exists(os.path.join(download_path, lesson_title + '.mp4')):
        return
    video_name = os.path.basename(video_path)
    with open(os.path.join(download_path, video_name), 'wb') as f:
        f.write(requests.get(f'http://{ip}{video_path}').content)
    if video_model['video_info']['data']['dynamic_video']['dynamic_video_list'][0]['encrypt']:
        key = decrypt_spade_a(video_model['video_info']['data']['dynamic_video']['dynamic_video_list'][0]['spade_a'])
        os.system('ffmpeg.exe -decryption_key ' + key + ' -i "' + os.path.join(download_path, video_name) + '" -c copy -copyts -movflags +faststart -movflags +use_metadata_tags -y "' + os.path.join(download_path, video_name.replace('.mdl', '.mp4')) + '"')
        os.remove(os.path.join(download_path, video_name))
    else:
        os.rename(os.path.join(download_path, video_name), os.path.join(download_path, video_name.replace('mdl', '.mp4')))
    audio_name = os.path.basename(audio_path)
    with open(os.path.join(download_path, audio_name), 'wb') as f:
        f.write(requests.get(f'http://{ip}{audio_path}').content)
    if video_model['video_info']['data']['dynamic_video']['dynamic_audio_list'][0]['encrypt']:
        key = decrypt_spade_a(video_model['video_info']['data']['dynamic_video']['dynamic_audio_list'][0]['spade_a'])
        os.system('ffmpeg.exe -decryption_key ' + key + ' -i "' + os.path.join(download_path, audio_name) + '" -c copy -copyts -movflags +faststart -movflags +use_metadata_tags -y "' + os.path.join(download_path, audio_name.replace('.mdl', '.mp4')) + '"')
        os.remove(os.path.join(download_path, audio_name))
    else:
        os.rename(os.path.join(download_path, audio_name), os.path.join(download_path, audio_name.replace('mdl', '.mp4')))
    os.system('ffmpeg.exe -i "' + os.path.join(download_path, video_name.replace('.mdl', '.mp4')) + '" -i "' + os.path.join(download_path, audio_name.replace('.mdl', '.mp4')) + '" -c copy -y "' + os.path.join(download_path, lesson_title + '.mp4') + '"')
    os.remove(os.path.join(download_path, video_name.replace('.mdl', '.mp4')))
    os.remove(os.path.join(download_path, audio_name.replace('.mdl', '.mp4')))
    print('导出成功：' + lesson_title)


def main(ip):
    # 首先下载db数据
    file_path = '/data/data/com.bytedance.ep.android/databases'
    for file_name in android_listdir(ip, file_path):
        if file_name == 'lesson_download':
            url = f'http://{ip}{file_path}/{file_name}'
            response = requests.get(url).content
            with open('./db/lesson_download.db', 'wb') as f:
                f.write(response)
        elif file_name == 'TTVideoEngine_download_database_v01':
            url = f'http://{ip}{file_path}/{file_name}'
            response = requests.get(url).content
            with open('./db/TTVideoEngine_download_database_v01.db', 'wb') as f:
                f.write(response)
    sql3 = SQL3('./db/lesson_download.db')
    values = sql3.query('''SELECT course_id, title FROM course_download_info;''')
    song_list = []
    for item in values:
        song_list.append([item[1], item[0]])
    song_list = use_song_list(song_list)
    download_values = SQL3('./db/TTVideoEngine_download_database_v01.db').query('''SELECT value FROM TTVideoEngine_download_database_v01;''')
    for clss_title, course_id in song_list:
        download_path = os.path.join('./song', safe_title(clss_title))
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        values = sql3.query(f'''SELECT lesson_id, lesson_title, video_model FROM lesson_download_info WHERE course_id={course_id};''', )
        class_list = []
        for lesson_id, lesson_title, video_model in values:
            class_list.append([lesson_title, lesson_id, video_model])
        class_list = use_song_list(class_list)
        for lesson_title, lesson_id, video_model in class_list:
            video_model = json.loads(video_model)
            video_id = video_model['video_info']['data']['video_id']
            download_info = get_download_info(video_id, download_values)
            assert download_info
            file_base = os.path.dirname(download_info['base_json']['file_path'])
            video_file_hash, audio_file_hash = list(download_info['base_json']['bytes_expect_map'].keys())
            if download_info['base_json']['bytes_expect_map'][video_file_hash] < download_info['base_json']['bytes_expect_map'][audio_file_hash]:
                video_file_hash, audio_file_hash = audio_file_hash, video_file_hash
            video_path = file_base + '/' + video_file_hash + '.mdl'
            audio_path = file_base + '/' + audio_file_hash + '.mdl'
            try:
                export_file(video_path, audio_path, safe_title(lesson_title), video_model, download_path, ip)
            except:
                print(traceback.format_exc())
