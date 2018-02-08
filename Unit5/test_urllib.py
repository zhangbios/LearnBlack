"""
    5.1 web的套接字函数库： urllib
"""
import urllib.request


def get_urlopen():
    """
        向WEB页面发送一个GET请求
    """
    url = "http://pm25.in"
    body = urllib.request.urlopen(url)
    text = body.read()
    print(type(text))
    print(text.decode())


def change_header():
    """
        用自定义 header 向一个WEB发送请求
    """
    url = "http://pm25.in"
    header = {'User-Agent': "Googlebot"}
    request = urllib.request.Request(url, headers=header)
    response = urllib.request.urlopen(request)
    print("request : ", request)
    print("response.code : ", response.code)
    print(response.read().decode())
    response.close()


