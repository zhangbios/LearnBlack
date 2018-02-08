"""
     代理TCP
     使用方式：python TcpProxy.py 127.0.0.1 9000 www.baidu.com 80 True
"""

import sys
import socket
import threading


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host,local_port))
    except:
        print("[!!] Failed to listen on {}:{}".format(local_host,local_port))
        print("[!!] Check for other listening sockets or correct permissions")
        sys.exit(0)

    print("Listening on {}:{}".format(local_host,local_port))
    server.listen(5)
    while True:
        client_socket,addr = server.accept()

        # 打印本地连接:
        print("[==>] Received incoming connection from {}:{}".format(addr[0],addr[1]))
        proxy_thread = threading.Thread(target=proxy_handler,
                                        args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    output = client_socket.recv(4096)
    print(output)
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote_socket.connect((remote_host, remote_port))
        print("Success to connect remote host {}:{}".format(remote_host,remote_port))
        # remote_socket.send('GET / HTTP/1.1\r\nHost:baidu.com\r\n\r\n'.encode('utf-8'))
        # remote_buffer = remote_socket.recv(4096)
        # print(remote_buffer)
    except:
        print("Failed to Connect remote host {}:{}".format(remote_host,remote_port))
        sys.exit(0)
    if receive_first:
        # 处理从client.socket接受到的消息
        output = response_handler(output)
        # 发送从client.socket接受到的请求
        remote_socket.send(output)
        remote_buffer = remote_socket.recv(4096)
        # hexdump(remote_buffer)
        # remote_buffer = response_handler(remote_buffer)
        if len(remote_buffer):
            print("[<==] Sending {} bytes to localhost.".format(len(remote_buffer)))
            client_socket.send(remote_buffer)
    while True:
        # 从本地读取数据
        local_buffer = client_socket.recv(4096)
        if len(local_buffer):
            print("[==>] Received {} bytes from localhost.".format(len(local_buffer)))
            # hexdump(local_buffer)
            # local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Send to remote")

        # 接受响应的数据
        remote_buffer = remote_socket.recv(4096)
        if len(remote_buffer):
            print("[<==] Received {} bytes from remote.".format(remote_buffer))
            # hexdump(remote_buffer)
            # remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Send to localhost.")

        # 两端无数据关闭
        if not len(local_buffer) and not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def request_handler(buffer):
    return buffer


def response_handler(buffer):
    # 将接收到的消息：
    """
    b'GET / HTTP/1.1\r\nHost: 127.0.0.1:9000\r\nConnection: keep-alive\r\nUpgrade-In
    secure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKi
    t/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36\r\nAccept: text/h
    tml,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nAccept-L
    anguage: zh-CN,zh;q=0.8\r\nCookie: __guid=96992031.3520626244700369400.151470314
    5756.6072\r\nAccept-Encoding: gzip, deflate\r\n\r\n'
    当中的 Host: 127.0.0.1:9000 修改为 
    """
    return buffer


def hexdump(buffer, length=16):
    result = []
    # Python 3中基本的str就是unicode，所以可以直接判断str
    digits = 4 if isinstance(buffer, str) else 2
    # python2.7中有xrange函数和range函数 python3中把range优化了，
    # 合并了xrange和range函数 用range函数就行
    # for i in xrang(0, len(buffer), length)
    for i in range(0, len(buffer), length):
        s = buffer[i:i+length]
        # ord()函数主要用来返回对应字符的ascii码，
        # chr()主要用来表示ascii码对应的字符他的输入时数字，可以用十进制，也可以用十六进制。
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X    %-*s    %s" % (i, length*(digits + 1), hexa, text))
    print(b'\n'.join(result))


def main():
    if len(sys.argv[1:]) != 5:
        print("usage ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    # 设置本地监听参数
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # 设置远程目标
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    # 告诉代理在发送给远程主机之前连接和接受数据
    receive_first = sys.argv[5]

    print("argv[1]:{},argv[2]:{},argv[3]:{},argv[4]:{},argv[5]:{}\r\n".format(local_host,local_port,
                                                                          remote_host,remote_port,receive_first))

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


if __name__ == '__main__':
    main()