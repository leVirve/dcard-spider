# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from dcard import Dcard


@pytest.fixture()
def may_contain_resourse_post_ids():
    def contain_keyword(metas):
        return [meta['id'] for meta in metas if '#圖' in meta['title']]

    return Dcard.forums('sex').get_metas(num=10, callback=contain_keyword)


def test_post_bundle(article_id):
    post = Dcard.posts(article_id).get()
    comment_count = post['content']['commentCount']
    assert comment_count == len(post['comments'])


def test_post_bundles(forums):
    forum = forums.get('test')['alias']

    metas = Dcard.forums(forum).get_metas(num=10)
    ids   = [m['id'] for m in metas]

    posts1 = Dcard.posts(metas).get(comments=False, links=False)
    posts2 = Dcard.posts(ids).get(comments=False, links=False)
    assert len(posts1) == len(posts2)

    titles = [post['content']['title'] for post in posts1]
    assert all(titles)


def test_parse_resourses_from_post(may_contain_resourse_post_ids):
    post_id = may_contain_resourse_post_ids[0]

    posts = Dcard.posts(post_id).get(comments=False, links=False)
    resources = posts.parse_resources()

    assert len(resources) >= 0


def test_parse_resourses_from_posts(may_contain_resourse_post_ids):
    ids = may_contain_resourse_post_ids

    posts = Dcard.posts(ids).get(comments=False, links=False)
    resources = posts.parse_resources(constraints={'commentCount': '>5'})

    assert len(resources) >= 0


def test_parse_resourses_from_post(may_contain_resourse_post_ids):
    posts = Dcard.posts(224341009).get(comments=False, links=False)

    resources = posts.parse_resources()
    status = posts.download(resources)

    assert all(status)
