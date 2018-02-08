"""
    开源web应用框架遍历 web 后缀
"""
import queue
import threading
import os
import urllib.request


threads = 10
target = "http://www.blackhatpython.com"
directory = "D:\\"
filters = [".jpg", ".gif", ".png", ".css"]

os.chdir(directory)

web_paths = queue.Queue()
# 遍历当前目录下所有文件并将其放入 队列 当中
for r,d,f in os.walk("."):
    for file in f:
        remote_path = "%s/%s"%(r,file)
        if remote_path.startswith("."):
            remote_path = remote_path[1:]
        if os.path.splitext(file)[1] not in filters:
            web_paths.put(remote_path)


def test_remote():
    while not web_paths.empty():
        path = web_paths.get()
        url = "%s/%s"%(target, path)

        request = urllib.request.Request(url)
        try:
            response = urllib.request.urlopen(request)
            content = response.read()

            print("{} => {}".format(response.code, path))
            response.close()
        except urllib.request.HTTPError as error:
            print("Failed {}".format(error.code))


for i in range(threads):
    print("Spawning thread: {}".format(i))
    t = threading.Thread(target=test_remote)
    t.start()
