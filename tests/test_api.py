import requests
from dcard.api import route

try:
    from fake_useragent import UserAgent
    USER_AGENT = UserAgent().random
except ImportError:
    USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) '
        'Gecko/20100101 Firefox/64.0'
    )


_post_id = 230004779
headers = {'User-Agent': USER_AGENT}


def test_valid_api_forums():
    url = route.forums()
    assert requests.get(url, headers=headers).ok


def test_valid_api_forum():
    url = route.posts_meta(forum='funny')
    assert requests.get(url, headers=headers).ok


def test_valid_api_article():
    url = route.post(post_id=_post_id)
    assert requests.get(url, headers=headers).ok


def test_valid_api_article_links():
    url = route.post(post_id=_post_id, addition='links')
    assert requests.get(url, headers=headers).ok


def test_valid_api_article_comments():
    url = route.post(post_id=_post_id, addition='comments')
    assert requests.get(url, headers=headers).ok
