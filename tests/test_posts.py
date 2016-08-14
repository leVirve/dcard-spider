# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class TestPosts:

    def test_with_none_in_dcard_instance(self, dcard):
        posts = dcard.posts
        assert not posts.ids
        assert not posts.metas
        assert not posts.use_only_id

    def test_with_metas_through__call__(self, dcard, metas):
        posts = dcard.posts(metas)
        assert posts.ids
        assert posts.metas
        assert not posts.use_only_id

    def test_with_ids_through__call__(self, dcard, metas):
        ids = [m['id'] for m in metas]
        posts = dcard.posts(ids)
        assert posts.ids
        assert not posts.metas
        assert posts.use_only_id

    def test_get_content(self, dcard, client):
        reqs = dcard.posts.get_content([9487])
        result = list(client.imap(reqs))[0]
        assert isinstance(result.json(), dict)

    def test_get_links(self, dcard, client):
        reqs = dcard.posts.get_links([9487])
        result = list(client.imap(reqs))[0]
        assert isinstance(result.json(), list)

    def test_get_comments_serial(self, dcard):
        reqs = dcard.posts.get_comments_serial(9487)
        result = reqs
        assert isinstance(result, list)

    def test_get_comments_parallel(self, dcard, client, metas):
        comments_count = 87
        reqs = dcard.posts.get_comments_parallel(9487, comments_count)
        result = list(client.imap(reqs))[0]
        assert isinstance(result.json(), list)

    def test_get_post_bundle(self, dcard):
        posts = dcard.posts(9487).get()
        first_post = posts.result()[0]
        comment_count = first_post['commentCount']
        assert comment_count == len(first_post['comments'])

    def test_get_post_bundles(self, dcard, metas):
        ids = [m['id'] for m in metas]
        posts1 = dcard.posts(metas).get(comments=False, links=False).result()
        posts2 = dcard.posts(ids).get(comments=False, links=False).result()
        titles = [post['title'] for post in posts1]
        assert len(posts1) == len(posts2)
        assert all(titles)


class TestPostsResult:

    def test_postsresult_from_post_with_ids(self, dcard):
        posts = dcard.posts(9487).get(comments=False, links=False).result()
        assert len(posts) == 1
        assert posts[0] is not None

    def test_postsresult_from_post_with_metas(self, dcard, metas):
        posts = dcard.posts(metas[0]).get(comments=False, links=False).result()
        assert len(posts) == 1
        assert posts[0] is not None

    def test_parse_resourses_in_content(self, dcard):
        posts = dcard.posts(9487).get(comments=False, links=False)
        resources = posts.parse_resources()
        assert len(resources) > 0

    def test_parse_resourses_in_content_and_comments(self, dcard):
        posts = dcard.posts(9487).get(links=False)
        resources = posts.parse_resources()
        assert len(resources) > 0

    def test_download_resourses(self, dcard):
        posts = dcard.posts(9487).get(comments=False, links=False)
        resources = posts.parse_resources()
        status, fails = posts.download(resources)
        assert type(status) is int
        assert len(fails) == 0
