#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import time
import json
# import subprocess
'''
@Author  :   npist
@License :   (C) Copyright 2018, npist.com
@Contact :   npist35@gmail.com
@File    :   v2rayMS_Client.py
@Time    :   2018.8.3
@Ver     :   0.1
'''

# 用户自定义变量
UPDATE_TIME = 60  # 用户列表刷新时间
UPDATE_TRANSFER = 600  # 用户流量刷新时间
# 服务器端口
SERVER = '127.0.0.1'
PORT = 8854
BUFSIZE = 4096
# CONNECT_KEY = 'ok'
# v2ray用户默认值设置
LEVEL = 1
ALTERID = 64

# V2RAY_PATH = '/usr/bin/v2ray/v2ray'
config_path = '/etc/v2ray/config.json'


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
    if not os.path.exists('/usr/bin/v2ray/v2ray'):
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
        with open(config_path, 'rb+') as f:
            json_dict = json.loads(f.read().decode('utf8'))
        return json_dict

    # 根据数据库获取的userlist生成新的clients字段
    def make_config_json():
        # 根据list长度生成下标组成的list，倒序删除内容
        for sub in range(len(userlist))[::-1]:
            try:
                if userlist[sub]['enable'] is 0:
                    del userlist[sub]
                elif 'uuid' in userlist[sub]:
                    userlist[sub].update({'id': userlist[sub].pop('uuid')})
                    # userlist[sub].update({'level': user_arg.pop('enable')})
                    userlist[sub].update({'alterId': ALTERID})
                    userlist[sub].update({'level': LEVEL})
                    userlist[sub].pop('enable')
            except Exception:
                # 如果出错删除这条记录
                print(
                    'Connection information error of user %s,Please check the Mysql!'
                    % (userlist[sub]['email'], ))
                del userlist[sub]
            # print(userlist)
        return userlist

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
        with open(config_path, 'wb+') as f:
            f.write(config_str.encode('utf8'))

    # 生成默认配置文件
    # default_dict = {}
    # if not os.path.exists(config_str):
    #     # print('No v2ray configuration file was detected\n' + 'Generating file')
    #     try:
    #         with open(config_str, 'wb+') as f:
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


# 刷新配置文件
def update_cfg(u_list, run_os, change):
    if run_os == 'Linux':
        v2ray_status = isRunning(V2RAY_PATH)
        r_cmd = 'service v2ray restart'
        s_cmd = 'service v2ray start'
    if change:
        sql_cov_json(u_list)
        if v2ray_status:
            # 重启v2ray(加载新的配置文件)
            os.popen(r_cmd)
        else:
            os.popen(s_cmd)
    elif not v2ray_status:
        os.popen(s_cmd)


# 发送/接收数据
def add_verify(data, sock):
    sock.sendall(data.encode())
    time.sleep(1)
    # 接收长度信息
    data_size = sock.recv(BUFSIZE)
    # 初始化长度变量
    recevied_size = 0
    # 初始化字符串
    recevied_data = b''
    # 数据未接收全的情况进行循环监听
    while recevied_size < int(data_size.decode()):
        data_res = sock.recv(BUFSIZE)
        recevied_size += len(data_res)
        recevied_data += data_res
    else:
        print("data receive done ...", recevied_size)
    return recevied_data


# 主函数
def main():
    from copy import deepcopy
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
    # 初始化内存中的列表
    user_config_str = []
    while True:
        print(time.asctime(time.localtime(time.time())))
        # 刷新配置文件
        user_config_raw = add_verify('pull_list', sock).decode()
        # 数据有变化，刷新v2ray配置文件
        if user_config_raw != user_config_str:
            print('Update user list')
            user_config_list = user_config_raw.split("#")
            user_count = 0
            user_config = []
            for user in user_config_list:
                user_config.append(eval(user))
                user_count += 1
            change = True
            user_config_str = user_config_raw
            print('Update OK!')
        else:
            print('没有更新')
            change = False
        # 更新配置文件
        Processing_data = deepcopy(user_config)
        update_cfg(Processing_data, run_os, change)
        time.sleep(UPDATE_TIME)


if __name__ == "__main__":
    main()
