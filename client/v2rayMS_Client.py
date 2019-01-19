#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import time
import json
import subprocess
'''
@Author  :   Npist <npist35@gmail.com>
@File    :   v2rayMS_Client.py
@License :   http://opensource.org/licenses/MIT The MIT License
@Link    :   https://npist.com/
@Time    :   2019.01.19
@Ver     :   0.5
'''

UPDATE_TIME = 50
# UPDATE_TRANSFER_TIME = 600
SERVER = '127.0.0.1'
PORT = 8854
BUFSIZE = 4096

DOMAIN = 'npist.com'

AES_length = 128
AES_Key = ''
AES_iv = '0000000000000000'

LEVEL = 0
ALTERID = 64
V2RAY_PATH = '/usr/bin/v2ray/v2ray'
CONFIG_PATH = '/etc/v2ray/config.json'
V2CTL_PATH = '/usr/bin/v2ray/v2ctl'
CTL_PORT = 10085

User_list = []

TRAFFIC_SWITCH = False


def check_python():
    info = sys.version_info
    if info[0] == 3 and not info[1] >= 4:
        print('Python 3.4+ required')
        sys.exit(1)
    if info[0] < 3:
        print('Python 3.4+ required')
        sys.exit(1)


def check_os():
    import platform
    return platform.system()


def check_v2ray(run_os):
    global V2RAY_PATH
    run_os = 'Linux'
    if run_os == 'Linux':
        print('Linux')
    else:
        print('OS not supported')
        sys.exit(1)
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
    string = crytpion.encrypt(data)  # AES加密请求
    send_data(string)
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
        sock.sendall(string)
    else:
        print('error')


# 协商AES密钥
def pull_aes_key():
    def agreemnt_key(string):
        send_data(string)
        key_rsa = sock.recv(BUFSIZE)
        return key_rsa

    import rsa
    AES_Key_RSA = agreemnt_key(b'ApplyKey')
    with open('private.pem', 'r') as f:
        priv_key = rsa.PrivateKey.load_pkcs1(f.read().encode())
    AES_Key = rsa.decrypt(AES_Key_RSA, priv_key).decode('utf-8')
    print('Obtaining Key Success!')
    return AES_Key


# AES模块
class prpcrypt(object):
    def __init__(self):
        from Crypto.Cipher import AES
        from binascii import b2a_hex, a2b_hex
        self.AES = AES
        self.b2a_hex = b2a_hex
        self.a2b_hex = a2b_hex
        self.key = AES_Key
        self.iv = AES_iv
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        cryptor = self.AES.new(self.key, self.mode, self.iv)
        length = AES_length / 8
        count = len(text)
        if (count % length != 0):
            add = int(length - (int(count % length)))
        else:
            add = 0
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        return self.b2a_hex(self.ciphertext)

    def decrypt(self, text):
        cryptor = self.AES.new(self.key, self.mode, self.iv)
        plain_text = cryptor.decrypt(self.a2b_hex(text))
        return plain_text.rstrip(b'\0').decode()


def accept_cfg():
    Gud = ['pull_list']
    Gud_str = '#'.join(Gud)
    user_config_raw = accept_data(Gud_str)
    user_config_temp = crytpion.decrypt(user_config_raw)
    if user_config_temp != 'None':
        print('Update user list')
        try:
            user_config_list = [eval(i) for i in user_config_temp.split("#")]
            update_cfg(user_config_list, run_os)
            print('Update OK!')
        except Exception as e:
            print(e)
            print('Update Error!')
    else:
        print('Updates could not be found')


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
    if crytpion.decrypt(accept_data(Gud_str)) == '$%^':
        return
    else:
        pass


# 主函数
def main():
    global AES_Key
    while True:
        print(time.asctime(time.localtime(time.time())))
        try:
            accept_cfg()
            if TRAFFIC_SWITCH == True:
                update_traffic()
        except Exception as e:
            print(e)
        time.sleep(UPDATE_TIME)


# 启动参数
def run_scripts(argv):
    global UPDATE_TIME, SERVER, PORT, AES_length, LEVEL, ALTERID, V2RAY_PATH, V2CTL_PATH, CONFIG_PATH, CTL_PORT, TRAFFIC_SWITCH
    import getopt
    import re
    filename = os.path.basename(sys.argv[0])
    help_text = '''Start up the V2rayMS_Client.

Usage:
    ./{filename}
    ./{filename} -s <ip> -p <port>
    ./{filename} -h | --help
    ./{filename} --version

Options:
    -h --help          Show this screen.
    -u --updatetime    Data refresh interval time(s)[default: 50].
    -s --serverip      V2rayMS_Server IP[default: 127.0.0.1].
    -p --port          V2rayMS_Server Port[default: 8854].

    -a --aeslength     AES key length[default: 128].
                       Optional value: 128/256/512.
                       Must be consistent with the server.

    -l --level         Default user level[default: 0].
    -i --alterid       Default user alterid[default: 64].
    -o --v2ray         V2ray-core path[default: /usr/bin/v2ray/v2ray].
    -c --config        V2ray config path[default: /etc/v2ray/config.json].
    -l --v2ctl         V2ctl path[default: /usr/bin/v2ray/v2ctl].
    -t --v2cltport     V2ctl port[default: 10085].
    -m --traffic       Traffic statistics switch[default: 0].
                       (1:ON  0:OFF)
                       
    -v --version       Show version.'''.format(filename=filename)
    try:
        opts, args = getopt.getopt(argv, "h:u:s:p:a:l:i:o:c:l:t:m:v", [
            "help", "updatetime=", "--serverip=", "--port=", "--aeslength=",
            "--level=", "--alterid=", "--v2ray=", "--config=", "--v2ctl=",
            "--v2ctlport=", "--traffic=", "version"
        ])
    except getopt.GetoptError:
        print(help_text)
        sys.exit(2)
    error_count = 0
    for opt, arg in opts:
        if opt == ("-h", "--help"):
            print(help_text)
            sys.exit()
        elif opt in ("-u", "--updatetime"):
            try:
                arg = int(arg)
            except Exception:
                print(opt + ' must use integers')
                error_count += 1
            UPDATE_TIME = arg
        elif opt in ("-s", "--serverip"):
            compile_ip = re.compile(
                '^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$'
            )
            if compile_ip.match(arg):
                SERVER = arg
            else:
                print(arg + ' is not a legal ip address!')
                error_count += 1
        elif opt in ("-p", "--port"):
            try:
                arg = int(arg)
                if arg < 1 or arg > 65535:
                    print('The port numbers in the range from 1 to 65535.')
                    error_count += 1
            except Exception:
                print(opt + ' must use integers')
                error_count += 1
            PORT = arg
        elif opt in ("-a", "--aeslength"):
            try:
                arg = int(arg)
                if arg not in [128, 256, 512]:
                    print('AES encryption length must be 128, 256, 512.')
                    error_count += 1
            except Exception:
                print(opt + ' must use integers')
                error_count += 1
            AES_length = arg
        elif opt in ("-l", "--level"):
            try:
                arg = int(arg)
            except Exception:
                print(opt + ' must use integers')
                error_count += 1
            LEVEL = arg
        elif opt in ("-i", "--alterid"):
            try:
                arg = int(arg)
            except Exception:
                print(opt + ' must use integers')
                error_count += 1
            ALTERID = arg
        elif opt in ("-o", "--v2ray"):
            if os.path.exists(arg):
                V2RAY_PATH = arg
            else:
                print(arg + ' is not a legal path!')
                error_count += 1
        elif opt in ("-c", "--config"):
            if os.path.exists(arg):
                CONFIG_PATH = arg
            else:
                print(arg + ' is not a legal path!')
                error_count += 1
        elif opt in ("-l", "--v2ctl"):
            if os.path.exists(arg):
                V2CTL_PATH = arg
            else:
                print(arg + ' is not a legal path!')
                error_count += 1
        elif opt in ("-t", "--v2ctlport"):
            try:
                arg = int(arg)
            except Exception:
                print(opt + ' must use integers')
                error_count += 1
            CTL_PORT = arg
        elif opt in ("-m", "--traffic"):
            try:
                arg = int(arg)
                if arg not in [1, 0]:
                    print(opt + ' must be 1 or 0.')
                    error_count += 1
            except Exception:
                print(opt + ' must be 1 or 0.')
                error_count += 1
            if arg == 0:
                TRAFFIC_SWITCH = False
            elif arg == 1:
                TRAFFIC_SWITCH = True
        elif opt in ("-v", "--version"):
            print('v2rayMS_Client 0.5 2019/01/19')
            sys.exit()
    if error_count != 0:
        print(str(error_count) + ' error(s)')
        sys.exit()


def pri_par():
    if TRAFFIC_SWITCH is True:
        t_s = 'On'
    else:
        t_s = 'Off'
    print('''Refresh time：                    {0}S
Server IP:                        {1}
Server Port:                      {2}
AES:                              AES-{3}

v2ray users default level:        {4}
v2ray users default alterid:      {5}
v2ray bin path:                   {6}
v2ray config path                 {8}

Traffic Statistics Switch:        {10}
v2ctl bin path:                   {7}
v2ctl port:                       {9}
'''.format(UPDATE_TIME, SERVER, PORT, AES_length, LEVEL, ALTERID, V2RAY_PATH,
           V2CTL_PATH, CONFIG_PATH, CTL_PORT, t_s))


if __name__ == "__main__":
    import socket
    run_scripts(sys.argv[1:])
    pri_par()
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
    if AES_Key == '':
        AES_Key = pull_aes_key()
        crytpion = prpcrypt()
    main()
