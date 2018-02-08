"""
    2.5 创建一个 TCP 代理
"""
import threading
import socket
import sys


def receive_from(connection):
    buffer = ""
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer


def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2

    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join(x if 0x20 <= ord(x) < 0x7F else b'.' for x in s)
        result.append(b"%04X %-*s %s" % (i, length*(digits + 1), hexa,text))
        print(b'\n'.join(result))


def response_handler(buffer):
    return buffer


def request_handler(buffer):
    return buffer


# def proxy_handler(client_socket, remote_host, remote_port, receive_first):
#     # 连接远程主机
#     remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     remote_socket.connect((remote_host,remote_port))
#     if receive_first:
#         remote_buffer = receive_from(remote_socket)
#         hexdump(remote_buffer)
#         # 发送给我们的响应处理
#         remote_buffer = response_handler(remote_buffer)
#         # 如果我们有数据传送给本地客户端，发送它
#         print("[<==] Sending {} bytes to localhost.".format(len(remote_buffer)))
#         client_socket.send(remote_buffer)
#     while True:
#         # 从本地读取数据
#         local_buffer = receive_from(client_socket)
#         if len(local_buffer):
#             print("[==>] Received {} bytes from localhost.".format(len(local_buffer)))
#             hexdump(local_buffer)
#             # 发送给我们本地的请求
#             local_buffer = request_handler(local_buffer)
#             # 向远程主机发送数据
#             remote_socket.send(local_buffer)
#             print("[==>] Send to remote.")
#         # 接收响应的数据
#         remote_buffer = receive_from(remote_socket)
#         if len(remote_buffer):
#             print("[<==] Receive {} bytes from remote.".format(len(remote_buffer)))
#             hexdump(remote_buffer)
#             # 发送到响应处理函数
#             remote_buffer = response_handler(remote_buffer)
#             # 将响应发送给本地 socket
#             client_socket.send(remote_buffer)
#             print("[<==] Send to localhost")
#         # 如果两边都没有数据 关闭连接
#         if not len(local_buffer) or not len(remote_buffer):
#             client_socket.close()
#             remote_socket.close()
#             print("[*] No more data. Closing connection")
#             break

def proxy_handler(client_socket, remote_host, remote_port, receive_first=True):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = remote_socket.recv(4096)
        hexdump(remote_buffer)
        client_socket.send(remote_buffer)

    while True:
        local_buffer = client_socket.recv(4096)
        hexdump(local_buffer)
        remote_socket.send(local_buffer)

        remote_buffer = remote_socket.recv(4096)
        hexdump(remote_buffer)
        client_socket.send(remote_buffer)

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host,local_port))
    except:
        print("[!!] Failed to listen on %s:%d"%(local_host,local_port))
        print("[!!] Check for other listening sockets or correct-permissions.")
        sys.exit()
    print("[*] Listening on %s:%d"%(local_host,local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # 打印出本地连接信息
        print("[==>] Received incoming connection from %s:%d"%(addr[0],addr[1]))
        # 开启一个线程与远程主机通信
        proxy_thread = threading.Thread(target=proxy_handler,
                                        args=(client_socket,remote_host,remote_port,receive_first))
        proxy_thread.start()

# def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind((local_host,local_port))
#     server.listen(5)
#     while True:
#         client_socket,addr = server.accept()
#         proxy_thread = threading.Thread(target=proxy_handler,
#                                         args=(client_socket, remote_host, remote_port, receive_first))
#         proxy_thread.start()


def main():
    # 没有华丽的命令行解析
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    # 设置本地监听参数
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # 设置远程目标
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    # 告诉代理在发送远程主机之前连接和接收数据
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    # 现在设置好我们监听的 socket
    server_loop(local_host,local_port,remote_host,remote_port,receive_first)


if __name__ == '__main__':
    main()