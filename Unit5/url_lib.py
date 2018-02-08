"""
    定义 header 访问目标 web
"""
import urllib.request


def toGetWeb():
    body = urllib.request.urlopen("http://pm25.in/")
    print(body.read())


def RequestCustomHeader():
    url = "http://127.0.0.1:9000/"
    # header = {}
    # header['User-Agent'] = "Googlebot"
    header = {'User-Agent': "Googlebot"}
    print(header)
    request = urllib.request.Request(url, headers=header)
    response = urllib.request.urlopen(request)
    print(response.read())
    response.close()


if __name__ == '__main__':
    RequestCustomHeader()