"""
    2.4 取代 netcat
"""

import sys
import socket
import getopt
import threading
import subprocess

# 定义一些全局变量
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def run_command(command):
    command = command.rstrip()
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
    except:
        output = "Failed to execute command.\r\n"
    return output

# 客户端处理者
def client_handler(client_socket):
    global upload
    global execute
    global command

    # 检查上传文件
    if len(upload_destination):
        file_buffer = ""
    # 持续读取数据直到没有数据
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        else:
            file_buffer += data

    try:
        file_descriptor = open(upload_destination,"wb")
        file_descriptor.write(file_buffer)
        file_descriptor.close()

        client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
    except:
        client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    # 检查执行命令
    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            # 跳出一个窗口
            client_socket.send("<BHP:#>")

            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            response = run_command(cmd_buffer)
            client_socket.send(response)

def server_loop():
    global target
    # 如果没有定义目标，就监听所有端口
    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)

    while True:
        client_socket,addr = server.accept()
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target,port))
        if len(buffer):
            client.send(buffer)

        while True:
            # 等待数据回传
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            print(response)

            buffer = input("")
            buffer += "\n"
            client.send(buffer)
    except:
        print("[*] Exception Exiting.")
    client.close()


def usage():
    pass

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                   ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
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
    if not listen and len(target) and port>0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()

if __name__ == '__main__':
    main()