"""
    3.1 windows or Linux 嗅探包
"""
import socket
import os

# 监听主机
host = "192.168.0.105"

# 创建原始套接字，绑定在公开接口上
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer_sock.bind((host, 0))

"""
setsockopt()函数功能介绍 :
设置与某个套接字关联的选项。选项可能存在于多层协议中，它们总会出现在最上面的套接字层。
当操作套接字选项时，选项位于的层和选项的名称必须给出。为了操作套接字层的选项，
应该将层的值指定为SOL_SOCKET。为了操作其它层的选项，控制选项的合适协议号必须给出。
例如，为了表示一个选项由TCP协议解析，层应该设定为协议号TCP。
"""
# 设置在捕获的数据包中包含 IP 头
sniffer_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# windows 平台上，设置IOCTL 启用混杂模式
if os.name == "nt":
    sniffer_sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# 读取单个数据包
print(sniffer_sock.recvfrom(65565))

# 在Windows平台上关闭混杂模式
if os.name == "nt":
    sniffer_sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)