# 仅供测试使用<br />
# 效果可查看https://proxy.npist.com<br />
# 有问题请联系npist35@gmail.com<br />
# 更新日志<br />
## 2018.8.13<br />
添加whmcs模块<br />
修改自https://github.com/kesuki/whmcs-shadowsocks-plugin<br />
## 2018.8.1<br />
初始版本<br />
<br />
# v2ray多用户后端安装说明<br />
建议使用Python3.6运行<br />
节点服务器运行前请参考官方文档安装v2ray<br />
安装命令行如下<br />
bash <(curl -L -s https://install.direct/go.sh)<br />
<br />
## 数据库服务器存放以下文件<br />
v2rayMS_Server.py<br />
v2server.py<br />
sqlconn.json<br />
### sqlconn.json为数据库连接文件  根据自己的mysql数据库配置<br />
### 执行以下命令启动<br />
nohup python3 v2rayMS_Server.py>> server.log 2>&1 &<br />
<br />
## 节点服务器存放以下文件<br />
v2rayMS_Client.py<br />
打开文件  修改服务端IP<br />
执行以下命令启动<br />
nohup python3 v2rayMS_Client.py>> server.log 2>&1 &<br />
