# 仅供测试使用<br />
实际部署请为socket通讯中的安全性进行强化<br />
效果可查看https://proxy.npist.com<br />
有问题请联系npist35@gmail.com<br />
# 更新日志<br />
## 2018.9.3<br />
添加流量统计、最后在线时间
更新数据库结构
添加示例v2ray配置文件（配合流量统计用）
## 2018.8.21<br />
优化socket传输中的数据量<br />
## 2018.8.13<br />
添加whmcs模块<br />
修改自https://github.com/kesuki/whmcs-shadowsocks-plugin<br />
安装请参考http://www.mak-blog.com/whmcs-shadowsocks-plugin.html<br />
## 2018.8.1<br />
初始版本<br />
<br />
# v2ray多用户后端安装说明<br />
建议使用Python3.6运行<br />
节点服务器运行前请参考官方文档安装v2ray<br />
安装命令行如下<br />
bash <(curl -L -s https://install.direct/go.sh)<br />
<br />
### Server目录存放进数据库服务器<br />
user.sql恢复进mysql或者mariadb
sqlconn.json为数据库连接文件  根据自己的mysql数据库配置<br />
执行以下命令启动<br />
nohup python3 -u v2rayMS_Server.py>> server.log 2>&1 &<br />
后台运行前建议首先前台执行python3 v2rayMS_Server.py或查看server.log分析Log<br />
<br />
### Client目录存放进节点服务器<br />
vim打开文件v2rayMS_Client.py  修改服务端IP<br />
执行以下命令启动<br />
nohup python3 -u v2rayMS_Client.py>> server.log 2>&1 &<br />
后台运行前建议首先前台执行python3 v2rayMS_Client.py或查看server.log分析Log<br />
