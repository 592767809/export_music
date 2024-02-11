
import traceback
import requests
import struct
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from utils.os import android_listdir, use_song_list


def getKeyData(dataView, offset):
    keyLen = struct.unpack("<I", dataView[offset: offset + 4])[0]
    offset += 4
    cipherText = bytearray(dataView[offset:offset + keyLen])
    for i in range(len(cipherText)):
        cipherText[i] ^= 0x64
    offset += keyLen
    crypto = AES.new(key=bytes.fromhex('687a4852416d736f356b496e62617857'), mode=AES.MODE_ECB)
    plainText = unpad(crypto.decrypt(cipherText), AES.block_size)
    return {"offset": offset, "data": plainText[17:]}


def getKeyBox(keyData):
    box = [i for i in range(256)]
    keyDataLen = len(keyData)
    j = 0
    for i in range(256):
        j = (box[i] + j + keyData[i % keyDataLen]) & 0xff
        box[i], box[j] = box[j], box[i]
    boxmap = bytearray()
    for i in range(256):
        i = (i + 1) & 0xff
        si = box[i]
        sj = box[(i + si) & 0xff]
        boxmap.append(box[(si + sj) & 0xff])
    return boxmap


def getMetaData(dataView, offset):
    metaDataLen = struct.unpack("<I", dataView[offset: offset + 4])[0]
    offset += 4
    cipherText = bytearray(dataView[offset:offset + metaDataLen])
    for i in range(len(cipherText)):
        cipherText[i] ^= 0x63
    offset += metaDataLen
    crypto = AES.new(key=bytes.fromhex('2331346C6A6B5F215C5D2630553C2728'), mode=AES.MODE_ECB)
    plainText = unpad(crypto.decrypt(base64.b64decode(cipherText[22:])), AES.block_size)
    result = json.loads(plainText[plainText.find(b":") + 1:].decode())
    return {'data': result, 'offset': offset}


def export_file(song_name, file_url):
    decrypted_file = bytearray()
    response = requests.get(file_url).content
    ncm = {}
    ncm['filebuffer'] = response
    keyDataObj = getKeyData(ncm['filebuffer'], 10)
    keyBox = getKeyBox(keyDataObj['data'])
    musicMetaObj = getMetaData(ncm['filebuffer'], keyDataObj['offset'])
    audioOffset = musicMetaObj['offset'] + struct.unpack("<I", ncm['filebuffer'][musicMetaObj['offset'] + 5: musicMetaObj['offset'] + 5 + 4])[0] + 13
    audioData = ncm['filebuffer'][audioOffset:]
    lenAudioData = len(audioData)
    for i in range(lenAudioData):
        decrypted_file.append(audioData[i] ^ keyBox[i & 0xff])
    with open('./song/' + musicMetaObj['data']['musicName'] + '.' + musicMetaObj['data']['format'], 'wb') as f:
        f.write(decrypted_file)


def main(ip):
    song_list = []
    file_path = '/storage/emulated/0/Download/netease/cloudmusic/Music/'
    for file_name in android_listdir(ip, file_path):
        if file_name.endswith('.ncm'):
            file_url = f'http://{ip}{file_path}{file_name}'
            song_list.append([file_name, file_url])
    song_list = use_song_list(song_list)
    for song_name, file_url in song_list:
        try:
            export_file(song_name, file_url)
        except:
            print(traceback.format_exc())
