#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import time
import json
import subprocess
'''
@Author  :   npist
@License :   (C) Copyright 2018, npist.com
@Contact :   npist35@gmail.com
@File    :   v2rayMS_Client.py
@Time    :   2018.9.6
@Ver     :   0.3
'''

# 刷新时间
UPDATE_TIME = 50
# 服务器端口
SERVER = '127.0.0.1'
PORT = 8854
BUFSIZE = 4096

DOMAIN = 'npist.com'

# v2ray用户默认值设置
LEVEL = 0
ALTERID = 64
V2RAY_PATH = '/usr/bin/v2ray/v2ray'
# V2RAY_PATH = '.\\bin\\v2ray.exe'
CONFIG_PATH = '/etc/v2ray/config.json'
# CONFIG_PATH = '.\\bin\\config.json'
V2CTL_PATH = '/usr/bin/v2ray/v2ctl'
# V2CTL_PATH = '.\\bin\\v2ctl.exe'
# CTL_PORT
CTL_PORT = 10085

# 初始化用户列表
User_list = []


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
                usrname_cfg['email'] = str(user[2]) + '@' + DOMAIN
                usrname_cfg['alterId'] = ALTERID
                usrname_cfg['level'] = LEVEL
                User_list.append(usrname_cfg)
            elif user[1] == 0:
                del_user = [i for i in User_list if i['id'] == user[0]]
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
def traffic_check(user):
    def traffic_get_msg(cmd):
        import re
        try:
            exec_cmd = subprocess.Popen(
                (cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True)
            outs, errs = exec_cmd.communicate(timeout=1)
        except subprocess.TimeoutExpired as e:
            exec_cmd.kill()
            return 0
        finally:
            exec_cmd.kill()
        allouts = (outs + errs).decode()
        # temp = b'stat: <\n  name: "user>>>9DvGOBEtLiyjqMxd@npist.com>>>traffic>>>downlink"\n  value: 588\n>\n\n'
        # allouts = temp.decode()
        error_str = 'failed to call service StatsService.GetStats'
        check_error = re.search(error_str, str(allouts))
        if check_error is not None:
            return 0
        else:
            try:
                traffic_values = [
                    i for i in allouts.split('\n') if re.search('value:', i)
                ][0].strip()[7:]
                return traffic_values
            except Exception as e:
                return 0

    # 设置查询参数
    cmd_downlink = V2CTL_PATH + ' api --server=127.0.0.1:' + str(
        CTL_PORT
    ) + ' StatsService.GetStats \'name: \"user>>>' + user + '>>>traffic>>>downlink\" reset: true\''
    cmd_uplink = V2CTL_PATH + ' api --server=127.0.0.1:' + str(
        CTL_PORT
    ) + ' StatsService.GetStats \'name: \"user>>>' + user + '>>>traffic>>>uplink\" reset: true\''
    # 查询
    d_data = int(traffic_get_msg(cmd_downlink))
    u_data = int(traffic_get_msg(cmd_uplink))
    if u_data == 0:
        return 0
    else:
        use_time = int(time.time())
        return d_data, u_data, use_time


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
    send_data(data)
    time.sleep(0.1)
    data_size = sock.recv(BUFSIZE)
    if data_size == b'error':
        return None
    sock.sendall(b'!#%')
    recevied_size = 0
    recevied_data = b''
    while recevied_size < int(data_size.decode()):
        data_res = sock.recv(BUFSIZE)
        recevied_size += len(data_res)
        recevied_data += data_res
    else:
        print("data receive done ....", recevied_size)
    return recevied_data


# 发送数据
def send_data(string):
    str_len = len(string)
    sock.sendall(str(str_len).encode())
    time.sleep(0.1)
    if sock.recv(BUFSIZE) == b'!#%':
        sock.sendall(string.encode())
    else:
        print('error')


def accept_cfg():
    Gud = ['pull_list']
    Gud_str = '#'.join(Gud)
    user_config_temp = accept_data(Gud_str)
    if user_config_temp != b'None':
        print('Update user list')
        user_config_temp = user_config_temp.decode()
        user_config_list = [eval(i) for i in user_config_temp.split("#")]
        update_cfg(user_config_list, run_os)
        print('Update OK!')
    else:
        print('没有更新')


# 更新流量
def update_traffic():
    Gud = ['push_traffic']
    for user in User_list:
        try:
            traffic_msg = traffic_check(user['email'])
            if traffic_msg != 0:
                Gud.append([
                    int(user['email'][:-(len(DOMAIN) + 1)]), traffic_msg[0],
                    traffic_msg[1], traffic_msg[2]
                ])
        except Exception as e:
            print('ID:' + user['email'][:-(len(DOMAIN) + 1)] +
                  ' Traffic read error!')
            print(e)
    Gud_str = '#'.join('%s' % i for i in Gud)
    if accept_data(Gud_str) == '$%^':
        return
    else:
        pass


# 主函数
def main():
    while True:
        print(time.asctime(time.localtime(time.time())))
        accept_cfg()
        update_traffic()
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
    # 初始化
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER, PORT))
    main()
