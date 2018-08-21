#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from socketserver import BaseRequestHandler, ThreadingTCPServer
import time
import v2server
'''
@Author  :   npist
@License :   (C) Copyright 2018, npist.com
@Contact :   npist35@gmail.com
@File    :   v2rayMS_Server.py
@Time    :   2018.8.20
@Ver     :   0.2
'''

HOST = '0.0.0.0'
PORT = 8854

BUFSIZE = 4096


# 多线程数据读取处理
class Handler(BaseRequestHandler):
    def handle(self):
        # 初始化数据库
        self.conn_sql = v2server.sqlconn()
        while True:
            try:
                # 接收数据
                data = self.accept_data()
                # 无连接时
                if data is None:
                    break
                proc_data = data.decode().split('#')
                # client拉取配置信息
                if proc_data[0] == 'pull_list':
                    msg = self.conn_sql.pull_user()
                if msg is not None:
                    self.send_data(msg)  # 分段发送
                else:
                    self.request.sendall(b'error')
            except Exception as e:
                print(e)
                break
        # 结束处理
        print("close:", self.request.getpeername())
        # 关闭sql连接
        self.conn_sql.conn.close()
        # 关闭socket连接
        # self.server.shutdown()
        self.request.close()

    # 发送数据
    def send_data(self, data):
        # 判断数据长度 并发送长度
        data_len = len(data)
        self.request.sendall(str(data_len).encode())
        time.sleep(0.1)
        if self.request.recv(BUFSIZE) == b'!#%':
            # 发送数据
            self.request.sendall(data.encode())

    # 接收数据
    def accept_data(self):
        # 接收长度信息
        data_size = self.request.recv(BUFSIZE)
        if data_size == b'':
            return None
        # 回复已接受
        self.request.sendall(b'!#%')
        # 初始化长度变量, 字符串
        recevied_size = 0
        recevied_data = b''
        # 数据未接收全的情况进行循环监听
        while recevied_size < int(data_size.decode()):
            data_res = self.request.recv(BUFSIZE)
            recevied_size += len(data_res)
            recevied_data += data_res
        return recevied_data


def main():
    ADDR = (HOST, PORT)
    server = ThreadingTCPServer(ADDR, Handler)
    print('listening')
    server.serve_forever()  # 监听
    print(server)


if __name__ == '__main__':
    main()
