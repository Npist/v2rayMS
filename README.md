# 仅供测试使用<br />
实际部署请为socket通讯中的安全性进行强化<br />
效果可查看https://proxy.npist.com<br />
有问题请联系npist35@gmail.com<br />
# 更新日志<br />
## 2018.9.22<br />
添加ClientApi模块，为计划中的客户端提供接口<br />
添加/更新开源协议(MIT)<br />
whmcs modules自GPLv3开源项目修改而来并以WHMCS插件形式存在，故继续遵守GPLv3协议<br />
## 2018.9.3<br />
添加流量统计、最后在线时间<br />
更新数据库结构<br />
添加示例v2ray配置文件（配合流量统计用）<br />
## 2018.8.21<br />
优化socket传输中的数据量<br />
## 2018.8.13<br />
添加whmcs模块<br />
修改自https://github.com/kesuki/whmcs-shadowsocks-plugin<br />
安装请参考http://www.mak-blog.com/whmcs-shadowsocks-plugin.html<br />
## 2018.8.1<br />
初始版本<br />
<br />
# 1.V2Ray多用户后端安装说明<br />
建议使用Python3.6运行<br />
节点服务器运行前请参考官方文档安装v2ray<br />
V2Ray安装命令行如下<br />
bash <(curl -L -s https://install.direct/go.sh)<br />
<br />
### 2.server目录存放进数据库服务器<br />
user.sql恢复进mysql或者mariadb<br />
sqlconn.json为数据库连接文件，根据自己的mysql数据库配置<br />
cron.php为流量定期重置程序，请将第3行的文件目录修改成server文件夹所在目录<br />
v2server.py为数据库更新程序，请将第47行的文件目录修改成server文件夹所在目录<br />
<br />
<del>执行以下命令启动<br />
nohup python3 -u v2rayMS_Server.py>> server.log 2>&1 &<br />
后台运行前建议首先前台执行python3 v2rayMS_Server.py或查看server.log分析Log<br /></del>
建议使用screen命令 在session中运行python3 v2rayMS_Server.py
<br />
### 3.client目录存放进节点服务器<br />
v2rayMS_Client.py为节点服务器主程序，请将第314行的IP修改成节点服务器的IP<br />
<br />
<del>执行以下命令启动<br />
nohup python3 -u v2rayMS_Client.py>> server.log 2>&1 &<br />
后台运行前建议首先前台执行python3 v2rayMS_Client.py或查看server.log分析Log<br /></del>
建议使用screen命令 在session中运行python3 v2rayMS_Client.py
SSH登录服务器使用nohup后台运行的话可能会出现broken pipe报错，原因应该是nohup会重定向stderr到stdout，ssh会话结束后会断开pipe
### 4.whmcs目录存放进WHMCS前端服务器<br />

