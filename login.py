from urllib.parse import quote
from bs4 import BeautifulSoup
import requests

login_url = 'https://sso.buaa.edu.cn/login?service='
mainpage_url = 'https://spoc.buaa.edu.cn/pjxt/authentication/main'

def get_token(session: requests.Session, target: str) -> str:
    response = session.get(target)
    soup = BeautifulSoup(response.text, 'html.parser')
    token = soup.find('input', {'name': 'execution'})['value']
    return token


def login(session: requests.Session, target_url: str, username: str, password: str) -> bool:
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