import sys
import threading
import paramiko
import subprocess
import socket

target = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
command = sys.argv[4]


def ssh_remote_cmd(target, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=target, username=username, password=password)
    ssh_session = ssh.get_transport().open_session()
    # paramiko.Transport().open_session() == (self._transport) paramiko.SSHClient().get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print(ssh_session.recv(1024))
    stdin,stdout,stderr = ssh.exec_command(command)
    # result = stdout.read()
    # print(result)
    res,err = stdout.read(),stderr.read()
    result = res if res else err
    print(result.decode())
    ssh.close()


def ssh_transport_file(transport, username, password):
    transport_instance = paramiko.Transport(transport)
    transport_instance.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport_instance)
    sftp.put('test','opt/ssh_transe.txt')
    sftp.get('/opt/ssh_transe.txt','test2')
    transport_instance.close()