#!/usr/bin/python3
# -*- coding: UTF-8 -*-
'''
@Author  :   npist
@License :   (C) Copyright 2018, npist.com
@Contact :   npist35@gmail.com
@File    :   v2rayMS_Server.py
@Time    :   2018.8.3
@Ver     :   0.1
'''

from socketserver import BaseRequestHandler, ThreadingTCPServer
import time
import v2server

HOST = '0.0.0.0'
PORT = 8854

# socket缓冲区大小
BUFSIZE = 4096


# 多线程数据读取处理
class Handler(BaseRequestHandler):
    def handle(self):
        self.conn_sql = v2server.sqlconn()
        while True:
            try:
                data = self.request.recv(BUFSIZE)
                if data.decode() == 'pull_list':
                    msg_raw = self.conn_sql.pull_user()
                    if msg_raw is not None:
                        self.send_data(msg_raw)
                        print(
                            time.asctime(time.localtime(time.time())) +
                            '\nData interaction Successful')
                    else:
                        self.request.sendall(b'error')
            except Exception as e:
                print(e)
                break
        print("close:", self.request.getpeername())
        self.conn_sql.conn.close()
        self.request.close()

    # 数据分段发送
    def send_data(self, data):
        # 判断数据长度
        data_len = len(data)
        # 判断为空
        # if data_len == 0:
        #     return ''
        # 发送数据长度
        self.request.sendall(str(data_len).encode())
        time.sleep(1)
        # 发送数据
        self.request.sendall(data.encode())


if __name__ == '__main__':
    server = ThreadingTCPServer((HOST, PORT), Handler)
    print('listening')
    server.serve_forever()
    print(server)
