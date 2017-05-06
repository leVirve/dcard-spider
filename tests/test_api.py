import requests
from dcard.api import route


def test_valid_api_forums():
    url = route.forums()
    assert requests.get(url).ok


def test_valid_api_forum():
    url = route.posts_meta(forum='funny')
    assert requests.get(url).ok


def test_valid_api_article():
    url = route.post(post_id=224341009)
    assert requests.get(url).ok


def test_valid_api_article_links():
    url = route.post(post_id=224341009, addition='links')
    assert requests.get(url).ok


def test_valid_api_article_comments():
    url = route.post(post_id=224341009, addition='comments')
    assert requests.get(url).ok
