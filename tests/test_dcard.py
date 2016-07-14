import requests
from dcard import Dcard


def test_valid_api_forums(forums):
    all_forums = forums.get('all')
    assert all_forums is not None


def test_valid_api_forum(forums):
    forum = forums.get('test')['alias']
    url = Dcard.forums.build_url(forum)
    assert requests.get(url).ok


def test_valid_api_article(article_url):
    assert requests.get(article_url).ok


def test_valid_api_article_links(article_url):
    assert Dcard.posts.get_links(article_url).result().ok


def test_valid_api_article_comments(article_url):
    assert Dcard.posts.get_comments(article_url)
