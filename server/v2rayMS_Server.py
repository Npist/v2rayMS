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
@Time    :   2018.10.3
@Ver     :   0.3.1
'''

HOST = '0.0.0.0'
PORT = 8854

BUFSIZE = 4096

ins_queue = queue.Queue()


# 多线程
class Handler(BaseRequestHandler):
    def handle(self):
        ipadd = str(self.request.getpeername()[0])
        c_port = str(self.request.getpeername()[1])
        s_msg = '[' + ipadd + ':' + c_port + ']'
        conn_sql = init_sqlconn(0, s_msg)
        while True:
            try:
                # 接收数据
                data = self.accept_data()
                proc_data = data.decode().split('#')
                if proc_data[0] == 'pull_list':
                    msg = conn_sql.pull_user()
                    if msg is not None:
                        self.send_data(msg)
                        if msg == 'error':
                            conn_sql = init_sqlconn(1, s_msg)
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
        except Exception as e:
            print('Mysql Connection Error')
            print(e)
            time.sleep(10)
            continue
    return conn


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


if __name__ == '__main__':
    main()
