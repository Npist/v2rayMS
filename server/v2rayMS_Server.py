#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys
import threading
from socketserver import BaseRequestHandler, ThreadingTCPServer
from queue import Queue
import time
import v2server
'''
@Author  :   Npist <npist35@gmail.com>
@File    :   v2rayMS_Server.py
@License :   http://opensource.org/licenses/MIT The MIT License
@Link    :   https://npist.com/
@Time    :   2019.01.19
@Ver     :   0.5
'''

HOST = '127.0.0.1'
PORT = 8854

BUFSIZE = 4096

AES_length = 128
AES_Key = ''
AES_iv = '0000000000000000'

ins_queue = Queue()


# 多线程数据读取处理
class Handler(BaseRequestHandler):
    def handle(self):
        global AES_Key
        ipadd = str(self.request.getpeername()[0])
        c_port = str(self.request.getpeername()[1])
        s_msg = '[' + ipadd + ':' + c_port + ']'
        conn_sql = init_sqlconn(0, s_msg)
        while True:
            try:
                # 接收数据
                data = self.accept_data()
                if data is None:
                    break
                elif data.decode() == 'ApplyKey':
                    key_send = self.push_aes_key()
                    AES_Key = self.key
                    self.crytpion = prpcrypt()
                    print(s_msg + ':' +
                          time.asctime(time.localtime(time.time())) + ':' +
                          'Generating AES key success')
                    self.request.sendall(key_send)
                else:
                    proc_data = self.crytpion.decrypt(data).split('#')
                    if proc_data[0] == 'pull_list':
                        msg = conn_sql.pull_user()
                        if msg is not None:
                            self.send_data(msg)
                            if msg == 'error':
                                conn_sql = init_sqlconn(1, s_msg)
                    elif proc_data[0] == 'push_traffic':
                        if len(proc_data) != 1:
                            users_traffic = [
                                eval(i) for i in proc_data
                                if i != 'push_traffic'
                            ]
                            ins_queue.put(users_traffic)
                        self.send_data('$%^')
            except Exception as e:
                print(e)
                break
        # 结束处理
        print("close:", self.request.getpeername())
        # 关闭连接
        conn_sql.conn.close()
        self.request.close()

    # 生成AES密钥并使用RSA公钥加密
    def push_aes_key(self):
        from rsa import PublicKey, encrypt
        from random import sample
        from string import digits, ascii_letters, punctuation
        # 生成AES密钥
        key_rules = digits + ascii_letters + punctuation
        self.key = ''.join(sample(key_rules * 10, 32))
        # 导入加密公钥
        with open('public.pem', 'r') as f:
            pub_key = PublicKey.load_pkcs1(f.read().encode())
        # 加密数据
        crypto = encrypt(self.key.encode(), pub_key)
        return crypto

    # 发送数据
    def send_data(self, data_raw):
        data = self.crytpion.encrypt(data_raw)
        data_len = len(data)
        self.request.sendall(str(data_len).encode())
        time.sleep(0.1)
        if self.request.recv(BUFSIZE) == b'!#%':
            self.request.sendall(data)

    # 接收数据
    def accept_data(self):
        data_size = self.request.recv(BUFSIZE)
        if data_size == b'':
            return None
        self.request.sendall(b'!#%')
        recevied_size = 0
        recevied_data = b''
        while recevied_size < int(data_size.decode()):
            data_res = self.request.recv(BUFSIZE)
            recevied_size += len(data_res)
            recevied_data += data_res
        return recevied_data


def init_sqlconn(i, source):
    mark = True
    while mark:
        print(
            source + ':' + time.asctime(time.localtime(time.time())) + ':',
            end='')
        try:
            conn = v2server.sqlconn()
            if i == 0:
                print('Mysql Connection Successfully')
            elif i == 1:
                print('Mysql Connection Successfully Recovered')
            mark = False
        except Exception:
            print('Mysql Connection Error')
            time.sleep(10)
            continue
    return conn


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


# 流量更新
def sql_queue():
    s_msg = '[Queue]'
    conn_sql = init_sqlconn(0, s_msg)
    while True:
        if ins_queue.empty() is not True:
            sql_task = ins_queue.get()
            for i in sql_task:
                try:
                    conn_sql.update_traffic(i)
                except Exception:
                    conn_sql = init_sqlconn(1, s_msg)
        time.sleep(0.1)


# 服务器监听
def serve_listen():
    server = ThreadingTCPServer((HOST, PORT), Handler)
    server.serve_forever()
    print(server)


# 主函数
def main():
    print('listening')
    que_thread = threading.Thread(target=sql_queue)
    ser_thread = threading.Thread(target=serve_listen)
    que_thread.start()
    ser_thread.start()
    que_thread.join()
    ser_thread.join()


# 启动参数
def run_scripts(argv):
    global HOST, PORT, AES_length
    import getopt
    import re
    import os
    filename = os.path.basename(sys.argv[0])
    help_text = '''Start up the V2rayMS_Client.

Usage:
    ./{filename}
    ./{filename} -s <ip> -p <port>
    ./{filename} -h | --help
    ./{filename} --version

Options:
    -h --help           Show this screen.
    -s --serverip       V2rayMS_Server Listen address[default: 127.0.0.1].
    -p --port           V2rayMS_Server Port[default: 8854].

    -a --aeslength      AES key length[default: 128].
                        Optional value: 128/256/512.
                        Must be consistent with the client.
    
    -v --version       Show version.'''.format(filename=filename)
    try:
        opts, args = getopt.getopt(
            argv, "h:s:p:a:v",
            ["--help", "--serverip=", "--port=", "--aeslength=", "--version"])
    except getopt.GetoptError:
        print(help_text)
        sys.exit(2)
    error_count = 0
    for opt, arg in opts:
        if opt == ("-h", "--help"):
            print(help_text)
            sys.exit()
        elif opt in ("-s", "--serverip"):
            compile_ip = re.compile(
                '^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$'
            )
            if compile_ip.match(arg):
                HOST = arg
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
        elif opt in ("-v", "--version"):
            print('v2rayMS_Client 0.5 2018/12/30')
            sys.exit()
    if error_count != 0:
        print(str(error_count) + ' error(s)')
        sys.exit()


def pri_par():
    print('''
Bind Address:                        {0}
Connector Port:                      {1}
AES:                                 AES-{2}
'''.format(HOST, PORT, AES_length))


if __name__ == '__main__':
    run_scripts(sys.argv[1:])
    pri_par()
    main()
