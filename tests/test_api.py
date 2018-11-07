import requests
from dcard.api import route


_post_id = 230004779


def test_valid_api_forums():
    url = route.forums()
    assert requests.get(url).ok


def test_valid_api_forum():
    url = route.posts_meta(forum='funny')
    assert requests.get(url).ok


def test_valid_api_article():
    url = route.post(post_id=_post_id)
    assert requests.get(url).ok


def test_valid_api_article_links():
    url = route.post(post_id=_post_id, addition='links')
    assert requests.get(url).ok


def test_valid_api_article_comments():
    url = route.post(post_id=_post_id, addition='comments')
    assert requests.get(url).ok
