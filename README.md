# 项目介绍
此项目旨在从你的手机里导出音乐。
## 使用环境
1. 你的手机必须已经root
    
2. 手机和电脑必须在同一个局域网

## 使用指南

1. 确保您的设备满足所需的环境。

2. 在手机上使用 Root 权限开启一个可访问整个手机目录的http服务：

    1. 前往 [F-Droid](https://f-droid.org/) 下载并安装 [Termux](https://f-droid.org/zh_Hans/packages/com.termux/) 。

    2. 使用下列两个命令，更新 Termux 的软件源和软件
    ```bash
        pkg update
        pkg upgrade
    ```

    3. 安装 Python
    ```bash
    pkg install python
    ```

    4. 获取Root权限
    ```bash
    su
    ```

    5. 设置环境变量或进入指定目录（二选一）
        1. 设置环境变量（推荐）
            执行如下指令：
            ```bash
            export PATH=/data/data/com.termux/files/usr/bin:$PATH
            ```
        2. 进入指定路径（不推荐）
            路径为 `/data/data/com.termux/files/usr/bin` 。不推荐方法不给出相应指令，请自行解决。

    6. 查看局域网地址
        1. 在 Termux 内查看
            执行 `ifconfig` 。可能会有多个地址，请一一尝试。
        2. 在 系统设置 查看
            如果使用的是 Wi-Fi ，则可查看 Wi-Fi 的详细信息以找到手机的局域网地址。
    7. 启动 http 服务
        1. 若你设置了环境变量，则直接执行如下命令
            ```bash
                python -m http.server -d /
            ```
        2. 若你进入指定文件夹：该方法不推荐，请自行修改命令。

3. 克隆或下载此项目的源代码。

4. 安装 `Python 3`
    
5. 安装项目依赖
    ```bash
        pip install -r requirements.txt
    ```
    
5. 把你手机的局域网ip与端口修改到main.py的入口函数中
    
6. 运行
```bash
    python main.py
```

# 更新日志

 - 2022.11.15
    1.初版上线