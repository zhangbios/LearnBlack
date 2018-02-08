"""
    利用cookie模拟网站登录
"""
import re
import requests
import http.cookiejar
from PIL import Image
import time
import json

header = {
    "host": "www.zhihu.com",
    "Referer": "https://www.zhihu.com/",
    }
# 建立会话，可以把同一用户的不同请求联系起来；直到会话结束都会自动处理cookies
session = requests.session()
session.cookies = http.cookiejar.LWPCookieJar("cookie")

# 若本地有cookie则不用再POST数据了
try:
    session.cookies.load(ignore_discard=True)
except IOError:
    print("Cookie未加载!")


def get_xsrf():
    """
    获取参数 _xsrf
    """
    response = session.get('https://www.zhihu.com', headers=header)
    html = response.text
    get_xsrf_pattern = re.compile(r'<input type="hidden" name="_xsrf" value="(.*?)"')
    _xsrf = re.findall(get_xsrf_pattern, html)[0]
    return _xsrf


def get_captcha():
    """
    获取验证码本地显示
    返回你输入的验证码
    """
    t = str(int(time.time() * 1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    response = session.get(captcha_url, headers=header)
    with open('captcha.gif', 'wb') as f:
        f.write(response.content)
    # Pillow显示验证码
    im = Image.open('captcha.gif')
    im.show()
    captcha = input('本次登录需要输入验证码：')
    return captcha


def login(username, password):
    """
        输入自己的用户名和密码
        模拟登录知乎
    """
    if re.match(r'\d{11}&', username):
        url = 'http://www.zhihu.com/login/phone_num'
        data = {'_xsrf': get_xsrf(),
                'password': password,
                'remember_me': 'true',
                'phone_num': username
                }
    else:
        url = 'http://www.zhihu.com/login/email'
        data = {'_xsrf': get_xsrf(),
                'password': password,
                'remember_me': 'true',
                'email': username
                }
    # 若不用验证码，直接登录
    result = session.post(url, data=data, headers=header)
    if (json.loads(result.text))["r"] == 1:
        # 要用验证码，post后登录
        data['captcha'] = get_captcha()
        result = session.post(url, data=data, headers=header)
        print((json.loads(result.text))['msg'])
    session.cookies.save(ignore_discard=True, ignore_expires=True)


def isLogin():
    # 通过查看用户个人信息来判断是否已经登录
    url = "https://www.zhihu.com/settings/profile"
    # 禁止重定向，否则登录失败重定向到首页也是响应200
    login_code = session.get(url, headers=header, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False


if __name__ == '__main__':
    if isLogin():
        print("您已登录")
    else:
        account = input('输入账号：')
        secret = input('输入密码：')
        login(account, secret)
