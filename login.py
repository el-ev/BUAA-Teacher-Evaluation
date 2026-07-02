from urllib.parse import quote
from bs4 import BeautifulSoup
import requests

login_url = 'https://sso.buaa.edu.cn/login?service='
mainpage_url = 'https://spoc.buaa.edu.cn/pjxt/authentication/main'

# Cookie 中与认证相关的关键字段
COOKIE_DOMAINS = ['sso.buaa.edu.cn', 'spoc.buaa.edu.cn', '.buaa.edu.cn']


def get_token(session: requests.Session, target: str) -> str:
    response = session.get(target)
    soup = BeautifulSoup(response.text, 'html.parser')
    token = soup.find('input', {'name': 'execution'})['value']
    return token


def login(session: requests.Session, target_url: str, username: str, password: str) -> bool:
    """使用用户名密码通过 SSO CAS 登录"""
    target = login_url + quote(target_url, 'utf-8')
    form = {
        'username': username,
        'password': password,
        'execution': get_token(session, target),
        '_eventId': 'submit',
        'type': 'username_password',
        'submit': "LOGIN"
    }
    response = session.post(target, data=form, allow_redirects=True)
    return response.url == mainpage_url


def login_with_cookie(session: requests.Session, cookie_str: str) -> bool:
    """
    使用浏览器 Cookie 字符串来认证。
    用户手动在浏览器中登录 https://spoc.buaa.edu.cn/pjxt/ 后，
    从浏览器开发者工具中复制 Cookie 字符串粘贴到这里。

    Cookie 字符串格式示例: "key1=value1; key2=value2; ..."
    """
    # 解析 Cookie 字符串并设置到 session
    cookies = {}
    for item in cookie_str.strip().split(';'):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key.strip()] = value.strip()

    # 为 session 设置 cookies
    for key, value in cookies.items():
        session.cookies.set(key, value, domain='spoc.buaa.edu.cn')
        session.cookies.set(key, value, domain='sso.buaa.edu.cn')
        session.cookies.set(key, value, domain='.buaa.edu.cn')

    # 验证登录状态：访问评教首页看是否被重定向到登录页
    test_url = 'https://spoc.buaa.edu.cn/pjxt/authentication/main'
    response = session.get(test_url, allow_redirects=False)

    # 如果返回 200 且未被重定向，说明认证成功
    if response.status_code == 200:
        return True

    # 如果被重定向到 SSO 登录页，说明 Cookie 无效
    if response.status_code in (301, 302):
        location = response.headers.get('Location', '')
        if 'sso.buaa.edu.cn' in location:
            return False

    # 其他情况也尝试访问主页
    return response.status_code == 200
