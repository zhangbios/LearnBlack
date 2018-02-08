"""
    暴力破解目录和文件位置
"""
import urllib.request
import threading
import queue

threads = 50
target_url = "http://testphp.vulnweb.com"
word_list_file = "/tmp/all.txt"     # from SVNDigger
resume = None
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"


def build_word_list(the_word_list_file):
    with open(the_word_list_file, "rb") as fd:
        raw_buffer = fd.readlines()
    found_resume = False
    words = queue.Queue()
    for word in raw_buffer:
        word = word.rstrip()
        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print("Resuming word_list from:{}".format(resume))
        else:
            words.put(word)
    return words


def dir_bruter(word_queue, extensions=None):
    """
        attempt : admin or admin.php
    """
    while not word_queue.empty():
        attempt = word_queue.get()
        attempt_list = []
        if "." not in attempt:
            attempt_list.append("/{}/".format(attempt))
        else:
            attempt_list.append("/{}".format(attempt))

        # 拓展 www.python.com/admin.php 或 www.python.com/admin.html 或 www.python.com/admin.jsp
        if extensions:
            for extension in extensions:
                attempt_list.append("/{}{}".format(attempt, extension))

        for brute in attempt_list:
            # urllib.request.quote(filename):URL标准中只会允许一部分ASCII字符比如数字、字母、部分符号等，
            # 而其他的一些字符，比如汉字等，是不符合URL标准的。此时，我们需要编码
            url = "{}{}".format(target_url, urllib.request.quote(brute))
            try:
                headers = {"User-Agent": user_agent}
                r = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(r)
                if len(response.read()):
                    print("[{}] => {}".format(response.code, url))

            except urllib.request.HTTPError as e:
                # hasattr 判断一个对象有没有某个属性
                if hasattr(e, 'code') and e.code != 404:
                    print("!!! {} => {}".format(e.code, url))


def main():
    word_queue = build_word_list(word_list_file)
    extensions = [".php", ".bak", ".orig", ".inc"]
    for i in range(threads):
        thr = threading.Thread(target=dir_bruter, args=(word_queue, extensions,))
        thr.start()


if __name__ == '__main__':
    main()