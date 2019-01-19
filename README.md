# 仅供测试使用<br />
效果可查看https://proxy.npist.com<br />
有问题请联系npist35@gmail.com<br />
telegram：https://t.me/Npist<br />
# 客户端项目
https://github.com/Npist/v2rayMSC<br />
请根据该项目说明配置./whmcs/clientapi.php中的RSA密钥字符串<br />
# 更新日志<br />
## 2019.1.19<br />
1.数据加密，保证账户下发到节点过程中的数据安全（需配置RSA公私钥，详见使用说明）<br />
2.启动参数，无需修改程序本身（详细参数见帮助 -h ）<br />
## 2018.10.3<br />
修复服务端若干BUG<br />
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
# 程序结构<br />
最初构想是直接有客户端访问数据库，但是需要开放数据库的3306端口到公网<br />
安全起见，写了两个程序，通过数据库服务器上的程序分析用户账户数据，再下发到节点服务器<br />
全程使用rsa加密对于机器性能也有影响，所以使用rsa对随机生成的高强度AES密码进行加密，下发到节点服务器以后使用aes进行数据加密<br />
# 兼容性说明<br />
项目中提供的前端仅为简单演示，但也具备了大部分基础功能。<br />
如果需要更完整的功能，请使用其他更加完善的前端。<br />
需要自行修改服务端v2server.py中对应的数据库字段。<br />
# v2ray多用户后端安装说明<br />
建议使用Python3.6运行<br />
使用前请自行安装python的以下模块<br /><br />
PyMySQL (0.9.2)<br />
rsa (3.4.2)<br />
cryptography (2.3.1)<br />
节点服务器运行前请参考官方文档安装v2ray<br /> 
安装命令行如下<br />
bash <(curl -L -s https://install.direct/go.sh)<br />
### RSA密钥对生成<br />
项目根目录下运行python3 rsa.py
将会在同位置生成public.pem和private.pem
放入对应位置即可
### Server目录里的内容及public.pem存放进数据库服务器<br />
user.sql恢复进mysql或者mariadb<br />
sqlconn.json为数据库连接文件  根据自己的mysql数据库配置<br />
执行以下命令启动<br />
python3 v2rayMS_Server.py<br />
后台运行建议使用screen新建session<br />
不带启动参数将以默认参数启动，即只监听本地IP<br />
#### 启动参数说明
    -s --serverip       服务器监听地址范围 默认为本地127.0.0.1 不限制设置为0.0.0.0
    -p --port           服务器监听端口 默认为8854 请打开防火墙对应端口

    -a --aeslength      AES加密长度 默认为128 可设置为128/256/512
                        客户端需一致
### Client目录里的内容及private.pem存放进节点服务器<br />
执行以下命令启动<br />
python3 v2rayMS_Client.py<br />
后台运行建议使用screen新建session<br />
不带启动参数将以默认参数启动，即server端运行在同一服务器上<br />
#### 启动参数说明
v2rayMS相关<br />

    -u --updatetime    数据刷新时间 默认为50秒
    -s --serverip      服务器IP
    -p --port          服务器端口

    -a --aeslength     AES加密长度 默认为128 可设置为128/256/512
                       客户端需一致
v2ray-core相关<br />

    -o --v2ray         V2ray-core程序位置
    -c --config        V2ray配置文件位置
v2ray用户相关<br />

    -l --level         v2ray默认用户level
    -i --alterid       v2ray默认用户alterid
v2ray流量统计相关<br />

    -l --v2ctl         V2ctl程序位置
    -t --v2cltport     V2ctl端口
    -m --traffic       流量统计开关 默认为关

使用流量统计请根据官方文档配置config.json，用户level v2ctl v2ctl端口均有关系<br />
client目录中提供的config.json为演示配置，可参考<br />

# 示例启动
服务器192.168.0.1（数据库，whmcs等）：<br />
python3 v2ray_Server.py -s 0.0.0.0 -p 9000<br />
即在9000端口上监听所有来源<br />

节点服务器192.168.2.1：<br />
python3 v2ray_client.py -u 100 -s 192.168.0.1 -p 9000 -m 1<br />
即连接到192.168.0.1的服务器上通过9000端口获取数据，刷新时间为100秒<br />