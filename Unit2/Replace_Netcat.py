"""
    author : KsBios
    sys.argv[]说白了就是一个从程序外部获取参数的桥梁，
    这个“外部”很关键，所以那些试图从代码来说明它作用的解释一直没看明白。
    因为我们从外部取得的参数可以是多个，所以获得的是一个列表（list)，
    也就是说sys.argv其实可以看作是一个列表，所以才能用[]提取其中的元素。
    其第一个元素是程序本身，随后才依次是外部给予的参数。
"""
import sys
import socket
import getopt
import threading
import subprocess

listen = False
command = False
upload = False
target = ''
excute = ''
upload_destination = ''
port = 0

def run_command(command):
    # 删除字符串末尾的空行
    command = command.rstrip()
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True,)
    except:
        output = "Failed to excute command..\r\n"
    return output

def client_handler(client_socket):
    global upload
    global excute
    global command
    # if len(upload_destination):
    #     file_buffer = ""
    #     while True:
    #         data = client_socket.recv(1024)
    #         if not data:
    #             break
    #         else:
    #             file_buffer += data
    # try:
    #     with open(upload_destination,'wb') as file_descritor:
    #         # file_buffer = client_socket.recv(4096)
    #         file_descritor.write(file_buffer)
    #     client_socket.send(upload_destination)
    # except:
    #     client_socket.send("Failed to save file to {}\r\n".format(upload_destination))
    if len(upload_destination):
        with open(upload_destination,'wb') as file_descriptor:
            file_buffer = client_socket.recv(4096)
            file_descriptor.write(file_buffer)
        client_socket.send(upload_destination)

    if len(excute):
        output = run_command(excute)
        client_socket.send(output)

    # if command:
    #     while True:
    #         client_socket.send("<BHP:#>")
    #         cmd_buffer = ""
    #         while '\n' not in cmd_buffer:
    #             cmd_buffer += client_socket.recv(1024)
    #         response = run_command(cmd_buffer)
    #         client_socket.send(response)

    if command:
        cmd_buffer = client_socket.recv(1024)
        response = run_command(cmd_buffer)
        client_socket.send(response)


def server_loop():
    global target
    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)

    while True:
        client_socket,addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def client_sender(buffer):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # try:
    #     client_socket.connect((target,port))
    #     if len(buffer):
    #         client_socket.send(buffer)
    #         while True:
    #             recv_len = 1
    #             response = ""
    #             while recv_len:
    #                 data = client_socket.recv(4096)
    #                 recv_len += len(data)
    #                 response += data
    #                 if recv_len < 4096:
    #                     break
    #             print(response)
    #             buffer = input()
    #             buffer += "\n"
    #             client_socket.send(buffer)
    #
    # except:
    #     print("[*] Exception! Exiting.")
    client_socket.connect((target,port))
    client_socket.send(buffer)
    response = client_socket.recv(4096)
    print(response)
    client_socket.close()

def usage():
    print("BHP Net tool\r\n")
    print("Usage: bhpnet.py -t target -p port")
    print("-l --listen                  - listen on [host]:[port] for incoming connections")
    print("-e --execute = file_to_run   - execute the given file upload receiving a connections")
    print("-c --command                 - initialize a command shell")
    print("-u --upload = destination    - upon receiving connection upload a file and write to [destination]")
    print("")
    print("Examples:")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | python ./bhpnet.py -t 192.168.11.12 -p 135")
    sys.exit(0)

def main():
    global listen
    global port
    global excute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    try:
        opts,args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:",
                                  ["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e","--execute"):
            excute = a
        elif o in ("-t","--target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        elif o in ("-c","--command"):
            command = True
        elif o in ("-u","--upload"):
            upload_destination = a
        else:
            assert False,"Unhandled Option"

    if not listen and len(target) and port>0:
        buffer = sys.stdin.read()
        client_sender(buffer)
    if listen:
        server_loop()


if __name__ == '__main__':
    main()