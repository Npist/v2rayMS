仅供测试使用

有问题请联系npist35@gmail.com


更新日志

2018.8.1 

初始版本


v2ray多用户后端

建议使用Python3.6运行

节点服务器运行前请参考官方文档安装v2ray

安装命令行如下

bash <(curl -L -s https://install.direct/go.sh)


数据库服务器存放以下文件

v2rayMS_Server.py

v2server.py

sqlconn.json

sqlconn.json为数据库连接文件  根据自己的mysql数据库配置

执行以下命令启动

nohup python3 v2rayMS_Server.py>> server.log 2>&1 &


节点服务器存放以下文件

v2rayMS_Client.py

打开文件  修改服务端IP

执行以下命令启动

nohup python3 v2rayMS_Client.py>> server.log 2>&1 &
