#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import time
import json
'''
@Author  :   npist
@License :   (C) Copyright 2018, npist.com
@Contact :   npist35@gmail.com
@File    :   v2rayMS_Client.py
@Time    :   2018.8.20
@Ver     :   0.2
'''

# 用户自定义变量
UPDATE_TIME = 60  # 用户列表刷新时间
UPDATE_TRANSFER = 600  # 用户流量刷新时间
# 服务器端口
SERVER = '127.0.0.1'
PORT = 8854
BUFSIZE = 4096

# v2ray用户默认值设置
LEVEL = 1
ALTERID = 64
V2RAY_PATH = '/usr/bin/v2ray/v2ray'
# V2RAY_PATH = '.\\bin\\v2ray.exe'
CONFIG_PATH = '/etc/v2ray/config.json'
# CONFIG_PATH = '.\\bin\\config.json'
V2CTL_PATH = '/usr/bin/v2ray/v2ctl'
# V2CTL_PATH = '.\\bin\\v2ctl.exe'
# CTL_PORT
CTL_PORT = 8855

# 程序配置
User_list = []
GUD = ['pull_list']  # 获取列表


# 检查更新
def check_update():
    pass


# 检查python版本
def check_python():
    info = sys.version_info
    if info[0] == 3 and not info[1] >= 4:
        print('Python 3.4+ required')
        sys.exit(1)
    if info[0] < 3:
        print('Python 3.4+ required')
        sys.exit(1)


# 检查操作系统
def check_os():
    import platform
    return platform.system()


# 检查v2ray
def check_v2ray(run_os):
    global V2RAY_PATH
    run_os = 'Linux'
    if run_os == 'Linux':
        print('Linux')
    else:
        print('OS not supported')
        sys.exit(1)
    # 检查支持库
    # try:
    #     import pymysql
    # except Exception:
    #     print('No module named \'PyMysql\'\n' +
    #           'Please confirm that this python module will' +
    #           'be executed again after installation.')
    #     sys.exit(1)
    # 检查v2ray
    if not os.path.exists(V2RAY_PATH):
        print('Please run "bash <(curl -L -s https://install.direct/go.sh)"' +
              'to install v2ray')
        sys.exit(1)


# Log输出
def save_log():
    pass


# 转换数据库为json
def sql_cov_json(userlist, user_os=None):
    # 获取配置文件
    def get_config_json():
        with open(CONFIG_PATH, 'rb+') as f:
            json_dict = json.loads(f.read().decode('utf8'))
        return json_dict

    # 根据数据库获取的userlist生成新的clients字段
    def make_config_json():
        global User_list
        for user in userlist:
            if user[1] == 1:
                usrname_cfg = {}
                usrname_cfg['id'] = user[0]
                usrname_cfg['email'] = str(user[2]) + '@npist.com'
                usrname_cfg['alterId'] = ALTERID
                usrname_cfg['level'] = LEVEL
                # 添加进数据库
                User_list.append(usrname_cfg)
            elif user[1] == 0:
                del_user = [i for i in User_list if i['id'] == user[0]]
                # 从数据库删除
                User_list = [m for m in User_list if m not in del_user]
        return User_list

    # 在配置文件中更新clients字段
    def create_config_json():
        c_dict = get_config_json()
        c_dict["inbound"]["settings"].update({'clients': make_config_json()})
        return c_dict

    # 更新json并格式化
    def format_json():
        config_dict = create_config_json()
        config_str = json.dumps(
            config_dict, sort_keys=False, indent=4, separators=(',', ': '))
        with open(CONFIG_PATH, 'wb+') as f:
            f.write(config_str.encode('utf8'))

    # 生成默认配置文件
    # default_dict = {}
    # if not os.path.exists(CONFIG_PATH):
    #     print('No v2ray configuration file was detected\n' + 'Generating file')
    #     try:
    #         with open(CONFIG_PATH, 'wb+') as f:
    #             cfg_str = json.dumps(
    #                 default_dict,
    #                 sort_keys=False,
    #                 indent=4,
    #                 separators=(',', ': '))
    #             f.write(cfg_str.encode('utf8'))
    #     except Exception:
    #         print('error')
    #         sys.exit(1)
    # 执行
    format_json()


# 进程检查
def isRunning(process_name):
    try:
        process = len(
            os.popen('ps aux | grep "' + process_name +
                     '" | grep -v grep').readlines())
        if process >= 1:
            return True
        else:
            return False
    except Exception:
        print("Check process ERROR!!!")
        return False


# 检查用户流量
def transfer_check(user):
    pass


# 刷新配置文件
def update_cfg(u_list, run_os):
    if run_os == 'Linux':
        v2ray_status = isRunning(V2RAY_PATH)
        r_cmd = 'service v2ray restart'
        s_cmd = 'service v2ray start'
    sql_cov_json(u_list)
    if v2ray_status:
        # 重启v2ray(加载新的配置文件)
        os.popen(r_cmd)
    else:
        os.popen(s_cmd)


# 请求数据
def accept_data(data):
    # 发送请求
    send_data(data)
    time.sleep(0.1)
    # 接收长度信息
    data_size = sock.recv(BUFSIZE)
    if data_size == b'error':
        return None
    # 回复已接收
    sock.sendall(b'!#%')
    # 初始化长度变量, 字符串
    recevied_size = 0
    recevied_data = b''
    # 数据未接收全的情况进行循环监听
    while recevied_size < int(data_size.decode()):
        data_res = sock.recv(BUFSIZE)
        recevied_size += len(data_res)  # 每次收到的服务端的数据有可能小于1024，所以必须用len判断
        recevied_data += data_res
    else:
        # 数据接收完毕
        print("data receive done ....", recevied_size)
    return recevied_data


# 发送数据
def send_data(string):
    # 判断数据长度 并发送长度
    str_len = len(string)
    sock.sendall(str(str_len).encode())
    time.sleep(0.1)
    if sock.recv(BUFSIZE) == b'!#%':
        # 发送数据
        sock.sendall(string.encode())
    else:
        print('error')


def accept_cfg():
    # 刷新配置文件
    GUD_str = '#'.join(GUD)
    user_config = accept_data(GUD_str)  # 接收数据
    # 数据有变化，刷新v2ray配置文件
    if user_config is not None:
        print('Update user list')
        user_config_list = [eval(i) for i in user_config.decode().split("#")]
        update_cfg(user_config_list, run_os)
        print('Update OK!')
    else:
        print('没有更新')


# 主函数
def main():
    global AES_Key
    while True:
        print(time.asctime(time.localtime(time.time())))
        accept_cfg()
        time.sleep(UPDATE_TIME)


if __name__ == "__main__":
    import socket
    # 检查OS，检查Python，检查主程序
    try:
        run_os = check_os()
        check_v2ray(run_os)
        check_python()
    except Exception:
        print('error')
    # 初始化连接
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER, PORT))
    main()

