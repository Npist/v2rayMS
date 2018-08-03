#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import json
import sys
'''
@Author  :   npist
@License :   (C) Copyright 2018, npist.com
@Contact :   npist35@gmail.com
@File    :   v2server.py
@Time    :   2018.8.3
@Ver     :   0.1
'''


# 数据处理
class sqlconn(object):
    def __init__(self):
        self.CHECK_CHANGE = True
        self.userlist = {}
        # self.userlist_temp = {}
        self.usertransfer = {}
        self.username_dict = {}
        self.username_list = []
        self.all_userstatus = {}
        self.cfg = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "v2ray",
            "password": "pass",
            "db": "v2ray",
            "transfer_mul": 1.0,
            "ssl_enable": 0,
            "ssl_ca": "",
            "ssl_cert": "",
            "ssl_key": ""
        }
        # 初始化配置文件
        self.load_sqlcfg()
        # 初始化连接
        self.get_sql()

    # 加载数据库配置
    def load_sqlcfg(self):
        config_path = './sqlconn.json'
        conncfg = None
        # 如果不存在文件，生成默认配置文件，并使用默认配置继续
        if not os.path.exists(config_path):
            try:
                with open(config_path, 'wb+') as f:
                    jsonstr = json.dumps(
                        self.cfg,
                        sort_keys=False,
                        indent=4,
                        separators=(',', ': '))
                    f.write(jsonstr.encode('utf8'))
            except Exception as e:
                print(e)
                sys.exit(1)
        # 如果存在文件，读取并载入
        else:
            try:
                with open(config_path, 'rb+') as f:
                    conncfg = json.loads(f.read().decode('utf8'))
            except Exception as e:
                print('The database configuration file was not detected!')
                print('The default connection information is used!')
            if conncfg:
                self.cfg.update(conncfg)

    # 读取数据库连接
    def get_sql(self):
        import pymysql
        try:
            if self.cfg["ssl_enable"] == 1:
                self.conn = pymysql.connect(
                    host=self.cfg["host"],
                    port=self.cfg["port"],
                    user=self.cfg["user"],
                    passwd=self.cfg["password"],
                    db=self.cfg["db"],
                    charset='utf8',
                    ssl={
                        'ca': self.cfg["ssl_ca"],
                        'cert': self.cfg["ssl_cert"],
                        'key': self.cfg["ssl_key"]
                    })
            else:
                self.conn = pymysql.connect(
                    host=self.cfg["host"],
                    port=self.cfg["port"],
                    user=self.cfg["user"],
                    passwd=self.cfg["password"],
                    db=self.cfg["db"],
                    charset='utf8')
        except Exception as e:
            print(e)
            # sys.exit(1)

    # sql执行函数
    def execute_sql(self, sql_exec):
        import pymysql
        try:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            # 执行SQL
            cursor.execute(sql_exec)
            data = cursor.fetchall()
            self.conn.commit()
            # 关闭
            cursor.close()
            # self.conn.close()
        except Exception as e:
            print(e)
            data = None
            # sys.exit(1)
        return data

    # 检索用户列表
    def pull_user(self):
        sql_exec = "SELECT uuid, email, enable FROM user"
        data = self.execute_sql(sql_exec)
        if data is not None:
            data_list = []
            for a in data:
                user_dict = json.dumps(a)
                data_list.append(user_dict)
            data_str = '#'.join(data_list)
        else:
            data_str = None
        return data_str
