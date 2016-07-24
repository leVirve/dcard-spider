import requests
from dcard import api
from dcard import Dcard


def test_valid_api_forums(forums):
    url = api.forums_url
    assert requests.get(url).ok


def test_valid_api_forum(forums):
    forum = forums.get('test')['alias']
    url = api.posts_meta_url_pattern.format(forum=forum)
    assert requests.get(url).ok


def test_valid_api_article(article_id):
    url = api.post_url_pattern.format(post_id=article_id)
    assert requests.get(url).ok


def test_valid_api_article_links(article_id):
    url = api.post_links_url_pattern.format(post_id=article_id)
    assert requests.get(url).ok


def test_valid_api_article_comments(article_id):
    url = api.post_comments_url_pattern.format(post_id=article_id)
    assert requests.get(url).ok
