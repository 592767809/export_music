
from server import *


def main():
    print("""1.qq音乐
2.酷狗概念版""")
    input_type = input('请输入导出类型：')
    if input_type == '1':
        qqmusic.main(ip)
    elif input_type == '2':
        kugoumusic.main(ip)
    else:
        input('选择类型错误')


if __name__ == '__main__':
    ip = '192.168.1.12:8000'
    main()