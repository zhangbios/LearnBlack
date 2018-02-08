import subprocess
import getopt
import sys,os
import getpass
from optparse import OptionParser

import ctypes
import socket
import struct
import csv
import json

from urllib import request
from urllib import parse
from http import cookiejar
from html.parser import HTMLParser

listen = False
command = False
execute = ""
target = ""
upload_destination = ""
port = 0


def test_type():
    """
        python中几种字符类型:
    """
    test_buffer_1 = b'123'
    test_buffer_2 = 123
    test_buffer_3 = b'test'
    test_buffer_4 = "test"
    print(type(test_buffer_1))
    print(type(test_buffer_2))
    print(type(test_buffer_3))
    print(type(test_buffer_4))


def CheckOutput_Function():
    output = subprocess.check_output('dir',stderr=subprocess.STDOUT,shell=True)
    print(type(output))
    print(output)
    print("***************************************************")
    print(output.decode('gbk'))
    print(type(output.decode('gbk')))


def getopt_Function():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                               ["help", "listen", "execute", "target", "port", "command", "upload"])
    print("get opts:{}.".format(opts))
    print("get args:{}.".format(args))
    print("**************************")
    for o, a in opts:
        if o in ("-h", "--help"):
            print("help!!")
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandler Option"
        if not listen and len(target) and port > 0:
            print("Get listen:{}, target:{}, port:{}.".format(listen, target, port))
        print("---------- 分隔符 -----------")
        if len(execute):
            print("get execute:{}.".format(execute))
        if len(upload_destination):
            print("get upload_destination:{}.".format(upload_destination))
        if len(target):
            print("get target:{}.".format(target))
        if port > 0:
            print("get port:{}.".format(port))


def parse_options():
    """
        python _Function_test.py 192.168.100.133 -p 8008 -r 192.168.100.128:80 --user justin --password
    """
    Usage = "usage: %prog [options] <ssh-server>[:<server-port>]"
    Ver = "%prog 1.0"
    Help = "this is Help"
    parser = OptionParser(usage=Usage, version=Ver, description=Help)
    parser.add_option('-q', '--quiet', action='store_false', dest='verbose',
                      default=True, help = 'squelch all informational output')
    parser.add_option('-p', '--remote-port', action='store', type='int', dest='port',
                      default = 4000, help = 'port on server to forward (default: %d)')
    parser.add_option('-u', '--user', action='store', type='string', dest='user',
                      default = getpass.getuser(), help = 'username for SSH authentication (default: %s)' % getpass.getuser())
    parser.add_option('-K', '--key', action='store', type='string', dest='keyfile',
                      default = None, help = 'private key file to use for SSH authentication')
    parser.add_option('', '--no-key', action='store_false', dest='look_for_keys',
                      default=True, help = 'don\'t look for or use a private key file')
    parser.add_option('-P', '--password', action='store_true', dest='readpass',
                      default=False, help = 'read password (for key or password auth) from stdin')
    parser.add_option('-r', '--remote', action='store', type='string', dest='remote',
                      default=None, metavar='host:port', help = 'remote host and port to forward to')
    options, args = parser.parse_args()
    print("--------------------------------")
    print("get options:{}.".format(options))
    print("get args:{}.".format(args))
    print("**********************************")
    print("Got args[0]:{}.".format(args[0]))
    print("Got options.remote:{}.".format(options.remote))
    print("**********************************")


class MyStruct(ctypes.Structure):
    # _fields_ = [('id', ctypes.c_ubyte, 4), ('perm', ctypes.c_ubyte, 4)]
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


def test_From_buffer_copy_Function():
    # value = "\xAA\xAA\xAA\xAA\x11\x11\x11\x11"
    # print(type(value))
    # print(value.encode('utf-8'))
    # ms = MyStruct.from_buffer_copy(value.encode('utf-8'))
    # print("id:{}, perm:{}.".format(ms.id, ms.perm))

    value1 = b'E\x00\x00()\xfe@\x00\x80\x069\xf3\xc0\xa8\x00i\xb4a!l\xf9\xd7\x01\xbb?.\x8c\xd3\xa1\xed\x1d@P\x11\x04\x00\x8e2\x00\x00'
    print("value1: ",value1)
    print("type value1:", type(value1))
    ms = MyStruct.from_buffer_copy(value1[0:20])
    print("ihl:{}, version:{}, tos:{}, len:{}, id:{}, offset:{}, ttl:{}, protocol_num:{}, sum:{}, src:{}, dst:{}"
          .format(ms.ihl, ms.version, ms.tos, ms.len, ms.id, ms.offset, ms.ttl, ms.protocol_num, ms.sum, ms.src, ms.dst))
    src_address = socket.inet_ntoa(struct.pack("<L", ms.src))
    dst_address = socket.inet_ntoa(struct.pack("<L", ms.dst))
    print(src_address)
    print(dst_address)


class parent1(object):
    def __init__(self):
        super(parent1, self).__init__()
        print("is prarent 1")
        print("goes parent 1")

class parent2(object):
    def __init__(self):
        super(parent2, self).__init__()
        print("is parent 2")
        print("goes parent 2")

class child1(parent2):
    def __init__(self):
        print("is child 1")
        super(child1, self).__init__()
        print("goes child 1")

class child2(parent1):
    def __init__(self):
        print("is child 2")
        super(child2, self).__init__()
        print("goes child 2")

class child3(parent2):
    def __init__(self):
        print("is child 3")
        super(child3, self).__init__()
        print("goes child 3")

class grandson(child3,child2,child1):
    def __init__(self):
        print("is grandson")
        super(grandson, self).__init__()
        print("goes grandson")


def Decode_Encode():
    buffer1 = b'example'
    buffer2 = buffer1.decode()
    buffer3 = str(buffer1, encoding='utf-8')
    buffer4 = bytes(buffer2, encoding='utf-8')
    print(buffer1, type(buffer1))
    print(buffer2, type(buffer2))
    print(buffer3, type(buffer3))
    print(buffer4, type(buffer4))


def process_csv_file(filepath):
    """
        读取 CSV 文件
    """
    with open(file=filepath, mode="rb", encoding='utf-8') as fp:
        text = csv.reader(fp)
        for file in text:
            print(file)


def process_json_file(filepath):
    """
        读取 json 文件
    """
    with open(filepath, mode='r', encoding='utf-8') as f:
        text = json.load(f)
    print(text)


def BianliDirect():
    os.chdir("D:\\mysite_test")
    with open("test.txt", "a") as fp:
        for r,d,f in os.walk("."):
            for files in f:
                remote_path = "{}\{}\n".format(r, files)
                if remote_path.startswith("."):
                    remote_path = remote_path[1:]
                    print(remote_path)
                    fp.write(remote_path)


def TestReadfile():
    os.chdir("D:\\mysite_test")
    with open(file="test.txt", mode='r', encoding='utf-8', newline='') as f:
        raw_buffer = f.readlines()
        for raw in raw_buffer:
            print(raw)


def cookie_instance():
    """
        将 cookie 保存到变量当中
    """
    # 声明一个Cookiejar对象实例来保存 cookie
    cookie = cookiejar.CookieJar()
    # 利用urllib库中的request的HTTPCookieProcessor对象来创建cookie处理器
    handler = request.HTTPCookieProcessor(cookie)
    # 通过handler来构建opener
    opener = request.build_opener(handler)
    # 此处的open方法同urllib的openurl方法，也可以传入request
    response = opener.open('http://www.baidu.com')
    for item in cookie:
        print("Name = {}".format(item.name))
        print("Value = {}".format(item.value))


def cookie_file_instance():
    """
        将 cookie 保存到文件当中
    """
    filename = "cookie.txt"
    cookie = cookiejar.MozillaCookieJar(filename)
    handler = request.HTTPCookieProcessor(cookie)
    opener = request.build_opener(handler)
    response = opener.open('http://www.baidu.com')
    cookie.save(ignore_discard=True, ignore_expires=True)


def read_cookie():
    """
        从文件中获取 cookie 并访问
    """
    cookie = cookiejar.MozillaCookieJar()
    cookie.load("cookie.txt", ignore_expires=True, ignore_discard=True)
    req = request.Request("http://www.baidu.com")
    opener = request.build_opener(request.HTTPCookieProcessor(cookie))
    response = opener.open(req)
    print(response.read())


class BruterParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}

    def handle_starttag(self, tag, attrs):
        # if tag == "input":
        #     print("Encountered a start tag:", tag)
        #     print("attrs :",attrs)
        #     for name,value in attrs:
        #         print("attrs[0]:{} value :{}".format(name, value))
        #     print("***********************")
        if tag == "input":
            tag_name = None
            tag_value = None
            for name,value in attrs:
                if name == "name":
                        tag_name = value
                if name == "value":
                    tag_value = value
            if tag_name is not None:
                self.tag_results[tag_name] = tag_value


def web_bruter():
    target_url = "https://passport.tianya.cn/register/default.jsp?sourceURL=http%3A%2F%2Fbbs.tianya.cn%2F"

    # response = request.urlopen(target_url)
    # print(response.read().decode())

    cookie = cookiejar.MozillaCookieJar("cookies")
    handler = request.HTTPCookieProcessor(cookie)
    opener = request.build_opener(handler)
    response = opener.open(target_url)
    page_text = response.read()
    cookie.save("cookies", ignore_discard=True, ignore_expires=True)
    # print(page_text.decode())

    parser = BruterParser()
    # print("***********************************************")
    parser.feed(page_text.decode())
    # print("_______________________________________________")
    post_tags = parser.tag_results
    print(post_tags)


if __name__ == '__main__':
    web_bruter()