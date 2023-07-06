import re
import requests


def android_listdir(ip, file_path):
    file_list = []
    url = f'http://{ip}{file_path}'
    response = requests.get(url).text
    for li in re.findall('(?<=<li>).+(?=</li>)', re.findall('(?<=<ul>).+(?=</ul>)', response, re.S)[0]):
        file_name = re.sub('<.+?>', '', li)
        if file_name[-1] == '/':
            file_name = file_name[:-1]
        file_list.append(file_name)
    return file_list


def use_song_list(song_list):
    i = 0
    return_list = []
    print('序号      歌曲')
    for each_song in song_list:
        print(str(i) + '         ' + each_song[0])
        i += 1
    xuhaolist = input('请输入要下载视频的序号:')
    if xuhaolist:
        if '@' in xuhaolist:
            return []
        if ',' in xuhaolist:
            for each1 in xuhaolist.split(','):
                if '-' in each1:
                    sta, ena = each1.split('-')
                    for each2 in range(int(sta), int(ena) + 1):
                        return_list.append(song_list[each2])
                else:
                    return_list.append(song_list[int(each1)])
        else:
            if '-' in xuhaolist:
                sta, ena = xuhaolist.split('-')
                for each in range(int(sta), int(ena) + 1):
                    return_list.append(song_list[each])
            else:
                return_list.append(song_list[int(xuhaolist)])
        print('你选择的是如下歌曲')
        i = 1
        for each in return_list:
            print(str(i) + '. ' + each[0])
            i += 1
        return return_list
    else:
        print('你选择的是全部歌曲')
        return song_list


def safe_title(title):
    title = re.sub('[\\\/\:\*\?\"\<\>\|]', '', title)
    for i in ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08', '\x09', '\x0a', '\x0b', '\x0c',
              '\x0d', '\x0e', '\x0f', '\x10', '\x11', '\x12', '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19',
              '\x1a', '\x1b', '\x1c', '\x1d', '\x1e', '\x1f', '\x7F']:
        if i in title:
            title = title.replace(i, '')
    return title
