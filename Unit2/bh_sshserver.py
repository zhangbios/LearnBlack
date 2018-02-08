"""
     SSH Server 启用
"""

import socket
import paramiko
import threading
import sys


host_key = paramiko.RSAKey(filename='private.key',password='ksbios')


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'zhang') and (password == 'ksbios'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


def ssh_server_loop(server_host, server_port):
    # 开启本地套接字监听：
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((server_host, server_port))
        server.listen(100)
        print("Listening for connection...")
        client,addr = server.accept()
    except Exception as e:
        print("Listen failed:",str(e))
        sys.exit(1)
    print("Got a connection")

    try:
        bhSession = paramiko.Transport(client)
        bhSession.add_server_key(host_key)
        server = Server()
        try:
            bhSession.start_server(server=server)
            print("Starting server...")
        except paramiko.SSHException as x:
            print("[！]开启服务失败！")
            sys.exit(1)
            # print("SSH negotiation failed 协商失败：",str(x))
        chan = bhSession.accept(20)
        print("认证成功!")
        print(chan.recv(1024).decode())     # 接收命令
        chan.send('Welcome to bh_ssh')      # 发送欢迎光临

        # 正式发送/接收 消息
        while True:
            try:
                command = input("Enter command:").strip()
                if command != 'exit':
                    chan.send(command)
                    print(chan.recv(4096).decode('gbk'))
                    # print('{}\n'.format(chan.recv(1024)))
                else:
                    chan.send('exit')
                    print("exiting!")
                    bhSession.close()
                    raise Exception('exit')
            except KeyboardInterrupt:
                bhSession.close()
    except Exception as e:
        print("Caught exception:",str(e))
        # bhSession.close()
        sys.exit(1)


def main():
    server_host = '10.10.10.61'
    server_port = 22
    ssh_server_loop(server_host,server_port)


if __name__ == '__main__':
    main()

