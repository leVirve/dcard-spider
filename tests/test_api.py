import requests
from dcard import api


def test_valid_api_forums():
    url = api.forums_url
    assert requests.get(url).ok


def test_valid_api_forum():
    url = api.posts_meta_url_pattern.format(forum='funny')
    assert requests.get(url).ok


def test_valid_api_article():
    url = api.post_url_pattern.format(post_id=224341009)
    assert requests.get(url).ok


def test_valid_api_article_links():
    url = api.post_links_url_pattern.format(post_id=224341009)
    assert requests.get(url).ok


def test_valid_api_article_comments():
    url = api.post_comments_url_pattern.format(post_id=224341009)
    assert requests.get(url).ok
