#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import threading
from socketserver import BaseRequestHandler, ThreadingTCPServer
import queue
import time
import v2server
'''
@Author  :   Npist <npist35@gmail.com>
@File    :   v2rayMS_Server.py
@License :   http://opensource.org/licenses/MIT The MIT License
@Link    :   https://npist.com/
@Time    :   2018.9.6
@Ver     :   0.3
'''


HOST = '0.0.0.0'
PORT = 8854

BUFSIZE = 4096

ins_queue = queue.Queue()


# 多线程
class Handler(BaseRequestHandler):
    def handle(self):
        global AES_Key
        conn_sql = v2server.sqlconn()
        while True:
            try:
                # 接收数据
                data = self.accept_data()
                proc_data = data.decode().split('#')
                if proc_data[0] == 'pull_list':
                    msg = conn_sql.pull_user()
                    if msg is not None:
                        self.send_data(msg)
                elif proc_data[0] == 'push_traffic':
                    if len(proc_data) != 1:
                        users_traffic = [
                            eval(i) for i in proc_data if i != 'push_traffic'
                        ]
                        ins_queue.put(users_traffic)
                    # 回复确认
                    self.send_data('$%^')
            except Exception as e:
                print(e)
                break
        # 结束处理
        print("close:", self.request.getpeername())
        # 关闭连接
        conn_sql.conn.close()
        self.request.close()

    # 发送数据
    def send_data(self, data):
        data_len = len(data)
        self.request.sendall(str(data_len).encode())
        time.sleep(0.1)
        if self.request.recv(BUFSIZE) == b'!#%':
            self.request.sendall(data.encode())

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


# 流量更新
def sql_queue():
    conn_sql = v2server.sqlconn()
    while True:
        if ins_queue.empty() is not True:
            sql_task = ins_queue.get()
            for i in sql_task:
                conn_sql.update_traffic(i)
        time.sleep(0.1)


# 服务器监听
def serve_listen():
    server = ThreadingTCPServer((HOST, PORT), Handler)
    print('listening')
    server.serve_forever()
    print(server)


# 主函数
def main():
    que_thread = threading.Thread(target=sql_queue)
    ser_thread = threading.Thread(target=serve_listen)
    que_thread.start()
    ser_thread.start()
    que_thread.join()
    ser_thread.join()


if __name__ == '__main__':
    main()
