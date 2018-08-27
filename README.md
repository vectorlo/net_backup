# net_backup

##系统环境
1. python 3+版本，安装paramiko模块
2. 支持linux&windows

##实现功能
1.自动备份网络设备配置，支持Cisco,Juniper,H3C，支持telnet%ssh
2.v0.02版本支持多线程

##sw.txt文件定义
存放设备登录信息，格式如下：
[hostname] [mgmt_ip] [username] [password] [port] [vendor]

##使用方法
windows:
C:\Users\vector\Desktop\net_backup_v0.01>python net_backup_v0.01.py sw.txt 

