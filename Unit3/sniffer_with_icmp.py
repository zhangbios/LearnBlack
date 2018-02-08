"""
    ICMP解码
"""
import struct
import ctypes
import socket
import os,sys
import threading
import time
from netaddr import IPNetwork, IPAddress

host = "10.10.10.61"
subnet = "10.10.10.0/24"
magic_message = "PTHONLABEL".encode('utf-8')
g_verbose = True


class IP(ctypes.Structure):
    _fields_ = [
        ("ihl", ctypes.c_ubyte, 4),
        ("version", ctypes.c_ubyte, 4),
        ("tos", ctypes.c_ubyte),
        ("len", ctypes.c_short),
        ("id", ctypes.c_short),
        ("offset", ctypes.c_short),
        ("ttl", ctypes.c_ubyte),
        ("protocol_num", ctypes.c_ubyte),
        ("sum", ctypes.c_short),
        ("src", ctypes.c_ulong),
        ("dst", ctypes.c_ulong)
    ]

    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        super(IP, self).__init__()
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))
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

    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        super(ICMP, self).__init__()
        pass


def __verbose(s):
    if g_verbose:
        print("*********** {} ***********".format(s))


def udp_sender(subnet, message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for ip in IPNetwork(subnet):
        sender.sendto(message, ('%s' % ip, 65212))


def main():
    if os.name == "nt":
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host,0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    thr = threading.Thread(target=udp_sender, args=(subnet, magic_message))
    thr.start()

    try:
        while True:
            raw_buffer = sniffer.recvfrom(4096)[0]
            __verbose(raw_buffer)
            ip_header = IP(raw_buffer[0:20])
            print("protocol: {}, source: {} -> destination: {}"
                  .format(ip_header.protocol, ip_header.src_address, ip_header.dst_address))
            if ip_header.protocol == 'ICMP':
                # 计算ICMP起始位置
                offset = ip_header.ihl * 4
                __verbose(offset)
                buffer = raw_buffer[offset : offset + sys.getsizeof(ICMP)]
                __verbose(sys.getsizeof(ICMP))
                # 解析ICMP数据
                icmp_header = ICMP(buffer)
                print("ICMP - > type: {} Code: {}".format(icmp_header.type, icmp_header.code))

                if icmp_header.type == 3 and icmp_header.code ==3:
                    if IPAddress(ip_header.src_address) in IPNetwork(subnet):
                        if raw_buffer[len(raw_buffer) - len(magic_message):] == magic_message:
                            print("Host Up:{}!".format(ip_header.src_address))

    except KeyboardInterrupt:
        if os.name == 'nt':
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


if __name__ == '__main__':
    main()