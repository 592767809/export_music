
import base64
import re
import os
import traceback
import requests
import json
from mysql3.mysql3 import SQL3
from utils.os import android_listdir, use_song_list, safe_title
from ExAndroidNativeEmu.androidemu.emulator import Emulator
from ExAndroidNativeEmu.androidemu.java.java_class_def import JavaClassDef
from ExAndroidNativeEmu.androidemu.java.java_method_def import java_method_def
from ExAndroidNativeEmu.androidemu.java.classes.array import Array


class Native(metaclass=JavaClassDef, jvm_name='com/ss/ttm/ttvideodecode/Native'):

    def __init__(self):
        pass

    @java_method_def(name='_getEncryptionKey', signature='([B)Ljava/lang/String;', native=True)
    def getEncryptionKe(self, mu):
        pass

    def test(self):
        pass


def app_key_decrypt(spade: str) -> str:
    emulator = Emulator(vfs_root='ExAndroidNativeEmu/vfs', config_path='ExAndroidNativeEmu/emu_cfg/default.json')
    emulator.java_classloader.add_class(Native)
    lib_module = emulator.load_library("so/libvideodec.so")
    emulator.call_symbol(lib_module, 'JNI_OnLoad', emulator.java_vm.address_ptr, 0x00)
    return Native().getEncryptionKe(emulator, Array(base64.b64decode(spade.encode()))).get_py_string()


def export_file(song_name, song_suffix, song_url, song_encrypt, song_spadea):
    song_data = requests.get(song_url).content
    with open('./song/' + song_name + '.' + song_suffix, 'wb') as f:
        f.write(song_data)
    if song_encrypt:
        key = app_key_decrypt(song_spadea)
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
