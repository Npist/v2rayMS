#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import json
import sys
'''
@Author  :   Npist <npist35@gmail.com>
@File    :   server.py
@License :   http://opensource.org/licenses/MIT The MIT License
@Link    :   https://npist.com/
@Time    :   2019.01.19
@Ver     :   0.5
'''


# 数据处理
class sqlconn(object):
    def __init__(self):
        self.CHECK_CHANGE = True
        self.userlist = {}
        # 数据
        self.data = []
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
        # print('Get Mysql Connection information successfully!')

    # 读取数据库连接
    def get_sql(self):
        import pymysql
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
            # cursor.close()
            # self.conn.close()
        except Exception as e:
            # print(e)
            data = 'error'
            # sys.exit(1)
        finally:
            cursor.close()
        return data

    # 检索用户列表
    def pull_user(self):
        from copy import deepcopy
        sql_exec = "SELECT uuid, enable, sid FROM user"
        data_cache = self.execute_sql(sql_exec)
        if data_cache == 'error':
            return 'error'
        self.traffic_check(data_cache)
        if data_cache == self.data:
            return 'None'
        else:
            # 检索变更内容
            data_change = [
                i for i in data_cache
                if i not in [m for m in self.data if m in data_cache]
            ]
            data_sid = [x['sid'] for x in self.data]
            data_cache_sid = [y['sid'] for y in data_cache]
            sid_change = [z for z in data_sid if z not in data_cache_sid]
            data_delete = []
            for n1 in self.data:
                for n2 in sid_change:
                    if n1['sid'] == n2:
                        n1['enable'] = 0
                        data_delete.append(n1)
            data_all = data_change + data_delete
            # 提取values
            data_cov = [list(n.values()) for n in data_all]
            # 转换整个list为字符串
            data_str = '#'.join('%s' % o for o in data_cov)
            self.data = deepcopy(data_cache)
        return data_str

    # 判断用户流量是否超标
    def traffic_check(self, all_user):
        sql_exec = "SELECT uplink, downlink, transfer_enable, sid FROM user"
        tmp = self.execute_sql(sql_exec)
        for i in tmp:
            if i['uplink'] + i['downlink'] > i['transfer_enable']:
                for n in all_user:
                    if n['sid'] == i['sid']:
                        n['enable'] = 0

    # 更新流量到数据库
    def update_traffic(self, traffic_data):
        d_tra_sql = 'UPDATE user SET downlink=downlink+' + str(
            traffic_data[1]) + ' WHERE sid=' + str(traffic_data[0])
        u_tra_sql = 'UPDATE user SET uplink=uplink+' + str(
            traffic_data[2]) + ' WHERE sid=' + str(traffic_data[0])
        use_time_sql = 'UPDATE user SET usetime=' + str(
            traffic_data[3]) + ' WHERE sid=' + str(traffic_data[0])
        self.execute_sql(d_tra_sql)
        self.execute_sql(u_tra_sql)
        self.execute_sql(use_time_sql)
