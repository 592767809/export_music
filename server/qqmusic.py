import os
import requests
import traceback
import re
import base64
import struct
from mysql3.mysql3 import SQL3
from utils.tc_tea import tc_tea_decrypt
from utils.os import android_listdir, use_song_list


FIRST_SEGMENT_SIZE = 0x80
SEGMENT_SIZE = 0x1400
music_suffix = {
    'flac': 'flac',
    'mflac0': 'flac',
    'qmcflac': 'flac'
}


def createInstWidthEKey(ekey):

    def isEncV2(key):
        return key.startswith(b'QQMusic EncV2,Key:')

    def DecryptV2Key(key):
        MixKey1 = [0x33, 0x38, 0x36, 0x5A, 0x4A, 0x59, 0x21, 0x40, 0x23, 0x2A, 0x24, 0x25, 0x5E, 0x26, 0x29, 0x28]
        MixKey2 = [0x2A, 0x2A, 0x23, 0x21, 0x28, 0x23, 0x24, 0x25, 0x26, 0x5E, 0x61, 0x31, 0x63, 0x5A, 0x2C, 0x54]
        decode_key_1 = tc_tea_decrypt(bytes(MixKey1), key[18:])
        decode_key_2 = tc_tea_decrypt(bytes(MixKey2), decode_key_1)
        return base64.b64decode(decode_key_2)

    simple_key_buf = bytes.fromhex('695646382b20150b')
    if isEncV2(ekey):
        dec_ekey = DecryptV2Key(ekey)
    else:
        dec_ekey = ekey

    tea_key = list()
    for i in range(0, 16, 2):
        tea_key.append(simple_key_buf[i // 2])
        tea_key.append(dec_ekey[i // 2])

    return dec_ekey[:8] + tc_tea_decrypt(bytes(tea_key), dec_ekey[8:])


def rotate(value, bits):
    rotate = (bits + 4) % 8
    left = value << rotate
    right = value >> rotate
    return (left | right) & 0xFF


def mapL(offset, key):
    if offset > 0x7FFF:
        offset %= 0x7FFF
    index = (offset * offset + 71214) % len(key)
    value = key[index]
    return rotate(value, index & 0b0111)


def EncFirstSegment(offset, buf, len_size, key, key_hash, decrypted_data):
    for i in range(len_size):
        next_key = key[offset % len(key)]
        decrypted_data.append(buf[i] ^ key[GetSegmentKey(offset, next_key, key_hash) % len(key)])
        offset += 1


def GetSegmentKey(offset, next_key, key_hash):
    return int(key_hash / ((offset + 1) * next_key) * 100)


def EncASegment(S, offset, buf, len_segment, key, key_hash, decrypt_data):
    S = S[:]
    segment_id = int(offset / SEGMENT_SIZE) & 0x1FF
    skip_len = GetSegmentKey(int(offset / SEGMENT_SIZE), key[segment_id], key_hash) & 0x1FF
    skip_len += offset % SEGMENT_SIZE
    N = len(key)
    j = 0
    k = 0
    for i in range(skip_len):
        j = (j + 1) % N
        k = (S[j] + k) % N
        S[j], S[k] = S[k], S[j]
    for i in range(len_segment):
        j = (j + 1) % N
        k = (S[j] + k) % N
        S[j], S[k] = S[k], S[j]
        decrypt_data.append(buf[i] ^ S[(S[j] + S[k]) % N])


def decrypt_file(song_file_buffer, key, out_file):
    decrypted_file = bytearray()
    if len(key) < 300:
        for i in range(len(song_file_buffer)):
            decrypted_file.append(song_file_buffer[i] ^ mapL(i, key))
        out_file.write(decrypted_file)
    else:
        N = len(key)
        S = [i & 0xFF for i in range(N)]
        j = 0
        for i in range(N):
            j = (S[i] + j + key[i % N]) % N
            S[i], S[j] = S[j], S[i]
        key_hash = 1
        for i in range(N):
            value = key[i]
            # // ignore if key char is '\x00'
            if not value:
                continue
            next_hash = (key_hash * value) & 0xFFFFFFFF
            if next_hash == 0 or next_hash <= key_hash:
                break
            key_hash = next_hash
        offset = 0
        buf = song_file_buffer
        size = len(song_file_buffer)
        len_size = size
        len_segment = min(size, FIRST_SEGMENT_SIZE)
        EncFirstSegment(offset, buf, len_segment, key, key_hash, decrypted_file)
        len_size -= len_segment
        buf = buf[len_segment:]
        offset += len_segment
        if offset % SEGMENT_SIZE != 0:
            len_segment = min(SEGMENT_SIZE - (offset % SEGMENT_SIZE), len_size)
            EncASegment(S, offset, buf, len_segment, key, key_hash, decrypted_file)
            len_size -= len_segment
            buf = buf[len_segment:]
            offset += len_segment
        while len_size > SEGMENT_SIZE:
            len_segment = min(SEGMENT_SIZE, len_size)
            EncASegment(S, offset, buf, len_segment, key, key_hash, decrypted_file)
            len_size -= len_segment
            buf = buf[len_segment:]
            offset += len_segment
        if len_size > 0:
            EncASegment(S, offset, buf, len_size, key, key_hash, decrypted_file)
        out_file.write(decrypted_file)


def decrypt_file_from_qmcflac(song_file_buffer, out_file):
    decrypted_file = bytearray()
    staticCipherBox = [119, 72, 50, 115, 222, 242, 192, 200, 149, 236, 48, 178, 81, 195, 225, 160, 158, 230, 157, 207,
                       250, 127, 20, 209, 206, 184, 220, 195, 74, 103, 147, 214, 40, 194, 145, 112, 202, 141, 162, 164,
                       240, 8, 97, 144, 126, 111, 162, 224, 235, 174, 62, 182, 103, 199, 146, 244, 145, 181, 246, 108,
                       94, 132, 64, 247, 243, 27, 2, 127, 213, 171, 65, 137, 40, 244, 37, 204, 82, 17, 173, 67, 104,
                       166, 65, 139, 132, 181, 255, 44, 146, 74, 38, 216, 71, 106, 124, 149, 97, 204, 230, 203, 187, 63,
                       71, 88, 137, 117, 195, 117, 161, 217, 175, 204, 8, 115, 23, 220, 170, 154, 162, 22, 65, 216, 162,
                       6, 198, 139, 252, 102, 52, 159, 207, 24, 35, 160, 10, 116, 231, 43, 39, 112, 146, 233, 175, 55,
                       230, 140, 167, 188, 98, 101, 156, 194, 8, 201, 136, 179, 243, 67, 172, 116, 44, 15, 212, 175,
                       161, 195, 1, 100, 149, 78, 72, 159, 244, 53, 120, 149, 122, 57, 214, 106, 160, 109, 64, 232, 79,
                       168, 239, 17, 29, 243, 27, 63, 63, 7, 221, 111, 91, 25, 48, 25, 251, 239, 14, 55, 240, 14, 205,
                       22, 73, 254, 83, 71, 19, 26, 189, 164, 241, 64, 25, 96, 14, 237, 104, 9, 6, 95, 77, 207, 61, 26,
                       254, 32, 119, 228, 217, 218, 249, 164, 43, 118, 28, 113, 219, 0, 188, 253, 12, 108, 165, 71, 247,
                       246, 0, 121, 74, 17]

    def getMask(t):
        if t > 32767:
            t %= 32767
        return staticCipherBox[t * t + 27 & 255]

    for i in range(len(song_file_buffer)):
        decrypted_file.append(song_file_buffer[i] ^ getMask(i))

    out_file.write(decrypted_file)


def export_file(song_name, song_suffix, file_name, file_path, sql3, ip):
    if song_suffix in music_suffix.keys():
        song_name = song_name + '.' + music_suffix[song_suffix]
    else:
        print('未支持的文件后缀： ' + song_suffix)
        return
    if os.path.exists('./song/' + song_name):
        return
    out_file = open('./song/' + song_name, 'wb')

    song_file_buffer = requests.get(f'http://{ip}{file_path}/{file_name}').content
    if song_suffix == 'flac':
        out_file.write(song_file_buffer)
    elif song_suffix == 'mflac0':
        assert song_file_buffer[-4:] == b'STag'
        song_file_buffer = song_file_buffer[:(struct.unpack('>i', song_file_buffer[-8:-4])[0] + 8) * -1]
        # 从数据库获取ekey
        ekey = sql3.query(f'SELECT ekey FROM audio_file_ekey_table where file_path="{file_path}/{file_name}";')[0][0]
        key = createInstWidthEKey(base64.b64decode(ekey))
        decrypt_file(song_file_buffer, key, out_file)
    elif song_suffix == 'qmcflac':
        decrypt_file_from_qmcflac(song_file_buffer, out_file)

    out_file.close()


def main(ip):
    # 首先下载db数据
    url = f'http://{ip}/data/data/com.tencent.qqmusic/databases/player_process_db'
    response = requests.get(url).content
    with open('./db/player_process_db', 'wb') as f:
        f.write(response)
    sql3 = SQL3('./db/player_process_db')
    values = sql3.query('''SELECT * FROM audio_file_ekey_table limit 1;''')
    if values:
        file_path = os.path.dirname(values[0][0])
    else:
        file_path = '/storage/emulated/0/qqmusic/song'
    song_list = []
    for file_name in android_listdir(ip, file_path):
        song_name, song_suffix = re.search('(.+?) \[.+?\]\.(.+)', file_name).groups()
        song_list.append([song_name, song_suffix, file_name])
    song_list = use_song_list(song_list)
    for song_name, song_suffix, file_name in song_list:
        try:
            export_file(song_name, song_suffix, file_name, file_path, sql3, ip)
        except:
            print(traceback.format_exc())
