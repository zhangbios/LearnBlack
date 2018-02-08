"""
    暴力破解目标 WEB 连接
"""
import urllib.request
import threading
import queue
import urllib.parse

threads = 50
target_url = "https://www.xs8.cn"
word_list_file = "D://all.txt"
resume = None
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"
attempt_list = []


def build_word_list(the_word_list_file):
    words = queue.Queue()
    with open(word_list_file, "rb") as f:
        raw_buffer = f.readlines()
        for word in raw_buffer:
            word = word.rstrip()
            words.put(word.decode())
            # print(word.decode())
        return words


def dir_bruter(word_queue, extensions=None):
    while not word_queue.empty():
        attempt = word_queue.get()
        print(attempt)
        if "." not in attempt:
            attempt_list.append("/{}/".format(attempt))
            if extensions:
                for extension in extensions:
                    attempt_list.append("/{}{}".format(attempt,extension))
        else:
            attempt_list.append("/{}".format(attempt))

        for brute in attempt_list:
            url = "{}{}".format(target_url, urllib.parse.quote(brute))
            try:
                headers = {"User-Agent": user_agent}
                opener = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(opener)
                if len(response.read()):
                    print("[{}] => {}".format(response.code, url))
            except urllib.request.URLError as e:
                if hasattr(e, "code") and e.code != 404:
                    print("[{}] => {}".format(e.code, url))


def main():
    words_queue = build_word_list(word_list_file)
    extensions = [".php", ".bak", ".orig", ".inc"]

    for i in range(threads):
        thr = threading.Thread(target=dir_bruter, args=(words_queue, extensions))
        thr.start()


if __name__ == '__main__':
    main()