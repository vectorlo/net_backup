#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko, telnetlib
import sys, os
import time
from concurrent.futures import ThreadPoolExecutor
#定义ssh登录函数
def ssh_connect(mgmt_ip, username, password, port=22):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(mgmt_ip, port, username, password, look_for_keys=False, timeout=10)
    return ssh

#定义telnet登录函数
def tn_connect(mgmt_ip, username, password, port=23):
    tn = telnetlib.Telnet(mgmt_ip, port=23, timeout=10)
    tn.read_until(b":")
    tn.write(username.encode('ascii') + b"\n") 
    tn.read_until(b":")
    tn.write(password.encode('ascii') + b"\n")
    return tn

#判断ssh/telnet连接，备份配置
def login(hostname, mgmt_ip, username, password, port, type):
    path = ".%sconfig%s%s.txt" % (os.sep, os.sep, hostname)

    if type == "juniper" and port == "22":
        try:
            ssh = ssh_connect(mgmt_ip, username, password)
            stdin, stdout, stderr = ssh.exec_command("show configuration; show configuration | display set")
            output = stdout.read().decode('ascii')
            ssh.close()
        except:
            log(hostname,mgmt_ip)
        else:
            backup(path, output, hostname, mgmt_ip)
    elif type == "juniper" and port == "23":
        try:
            t = tn_connect(mgmt_ip, username, password)
            t.write(b"show configuration | no-more\n")
            t.write(b"show configuration | display set | no-more\n")
            t.write(b"exit\n")
            output = t.read_all().decode('ascii')
        except:
            log(hostname,mgmt_ip)
        else:
            backup(path, output, hostname, mgmt_ip)
    elif type == "h3c" and port == "22":
        try:
            ssh = ssh_connect(mgmt_ip, username, password)
            conn = ssh.invoke_shell()
            conn.send("screen-length disable\n")
            time.sleep(0.1)
            conn.send("display cu\n")
            time.sleep(5)
            output = conn.recv(65535).decode('gbk')
            ssh.close()
        except:
            log(hostname,mgmt_ip)
        else:
            backup(path, output, hostname, mgmt_ip)
    elif type == "h3c" and port == "23":
        try:
            t = tn_connect(mgmt_ip, username, password)
            t.write(b"screen-length disable\n")
            t.write(b"display cu\n")
            t.write(b"exit\n")
            output = t.read_all().decode('gbk')
        except:
            log(hostname,mgmt_ip)
    elif type == "cisco" and port == "22":
        try:
            ssh = ssh_connect(mgmt_ip, username, password)
            stdin, stdout, stderr = ssh.exec_command("show run")
            output = stdout.read().decode()
            ssh.close()
        except:
            log(hostname,mgmt_ip)
        else:
            backup(path, output, hostname, mgmt_ip)
    elif type == "cisco" and port == "23":
        try:
            t = tn_connect(mgmt_ip, username, password)
            t.write(b"terminal length 0\n")
            t.write(b"show run\n")
            t.write(b"exit\n")
            output = t.read_all().decode('ascii')
        except:
            log(hostname,mgmt_ip)
        else:
            backup(path, output, hostname, mgmt_ip)

#读取txt文件，获取登录设备信息
def get_info():
    with open(sys.argv[1]) as f:
        info = f.read().split('\n') 
    for d in info:
        yield d.split() 

#记录错误日志
def log(hostname, mgmt_ip):
    log = "%s %s backup failed!" % (hostname, mgmt_ip)
    print(log) 
    with open("log.txt","a") as f:
        f.write(log)
        f.write("\n")

#将配置写入txt文件
def backup(path, output, hostname, mgmt_ip):
    with open(path, "w") as f:
        f.write(output)
    print("%s %s backup successful!" % (hostname, mgmt_ip))

#遍历get_info，调用connect函数
def main():
    path = ".%slog.txt" % os.sep
    if os.path.exists(path):
        os.remove(path)
    with ThreadPoolExecutor(20) as executor:
        for d in get_info():
            if d != []:
                executor.submit(login, *d)  
            else:
                break

if __name__ == "__main__":
    main()
