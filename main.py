import os
from server import *


def main():
    if not os.path.exists('./db'):
        os.makedirs('./db')
    if not os.path.exists('./song'):
        os.makedirs('./song')
    print("""1.qq音乐-11.11.0.10
2.酷狗音乐-11.3.8
3.酷狗音乐概念版-3.0.0
4.网易云音乐-8.8.70
5.汽水音乐-6.0.0
6.学浪-6.7.0
7.悟饭游戏厅-5.0.4.9""")
    input_type = input('请输入导出类型：')
    if input_type == '1':
        qqmusic.main(ip)
    elif input_type == '2':
        kugoumusic.main(ip)
    elif input_type == '3':
        kugoulitemusic.main(ip)
    elif input_type == '4':
        wangyiyunmusic.main(ip)
    elif input_type == '5':
        qishuimusic.main(ip)
    elif input_type == '6':
        xuelang.main(ip)
    elif input_type == '7':
        wufanyouxiting.main(ip)
    else:
        input('选择类型错误')


if __name__ == '__main__':
    ip = '192.168.31.23:8000'
    main()
