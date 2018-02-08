"""
    3.3 解码 ICMP
    解析监听到的数据包
"""
import threading
import socket
import os
import sys
import struct
import ctypes

# 监听的主机
host = "192.168.0.105"


# 定义 IP 头
class IP(ctypes.Structure):
    _fields_ = [
        ("ihl", ctypes.c_ubyte, 4),
        ("version", ctypes.c_ubyte, 4),
        ("tos", ctypes.c_ubyte),
        ("len", ctypes.c_ushort),
        ("id", ctypes.c_ushort),
        ("offset", ctypes.c_ushort),
        ("ttl", ctypes.c_ubyte),
        ("protocol_num", ctypes.c_ubyte),
        ("sum", ctypes.c_ushort),
        ("src", ctypes.c_ulong),
        ("dst", ctypes.c_ulong)
    ]

    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        super(IP, self).__init__()
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # 可读性更强的 IP 地址
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))

        # 协议类型
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


class ICMP(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ubyte),
        ("code", ctypes.c_ubyte),
        ("checksum", ctypes.c_short),
        ("unset", ctypes.c_short),
        ("next_hop_mtu", ctypes.c_short)
    ]

    def __new__(cls, socket_buffer):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        super(ICMP, self).__init__()
        pass


def main():
    if os.name == "nt":
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer_sock.bind((host, 0))
    sniffer_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)    # 设置在捕获的数据包中包含 IP 头

    # windows 平台上，设置IOCTL 启用混杂模式
    if os.name == "nt":
        sniffer_sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:
        while True:
            raw_buffer = sniffer_sock.recvfrom(65565)[0]
            ip_header = IP(raw_buffer[0:20])
            print("protocol: {} source: {} ->  destination: {}."
                  .format(ip_header.protocol, ip_header.src_address, ip_header.dst_address))

            if ip_header.protocol == "ICMP":
                offset = ip_header.ihl * 4
                buf = raw_buffer[offset : offset + sys.getsizeof(ICMP)]
                icmp_header = ICMP(buf)
                print("ICMP -> Type: {}, code: {}.".format(icmp_header.type, icmp_header.code))

    except KeyboardInterrupt:
        # 在Windows平台上关闭混杂模式
        if os.name == "nt":
            sniffer_sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


if __name__ == '__main__':
    main()