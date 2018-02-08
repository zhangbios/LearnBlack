"""
    5.2 开源WEB应用安装
"""
import urllib.request
import queue
import threading
import os

threads = 10
target = "http://www.blackcatpython.com"
directory = "D://my_site"
filters = [".jpg", ".gif", ".png", ".css"]


def test_remote(web_paths, target):
    """
        遍历queue，取出字段加至 url自后，暴力测试url
    """
    while not web_paths.empty():
        path = web_paths.get()
        url = "{}{}".format(target, path)
        request = urllib.request.Request(url)
        try:
            response = urllib.request.urlopen(request)
            content = response.read()
            # print(content.decode())
            print("[{}] => {}".format(response.code, path))
            response.close()

        except urllib.request.HTTPError as err:
            print("Failed {}".format(err.code))


def web_app_mapper():
    os.chdir(directory)
    web_paths = queue.Queue()

    for r, d, f in os.walk("."):
        for files in f:
            remote_path = "{}/{}".format(r, files)
            if remote_path.startswith("."):
                remote_path = remote_path[1:]
            if os.path.splitext(files)[1] not in filters:
                web_paths.put(remote_path)

    for i in range(threads):
        print("Spawning thread: {}".format(i))
        thr = threading.Thread(target=test_remote, args=(web_paths, target))
        thr.start()


if __name__ == '__main__':
    web_app_mapper()
