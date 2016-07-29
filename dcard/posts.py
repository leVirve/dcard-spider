from __future__ import absolute_import

import logging
from six.moves import zip_longest

from dcard import api
from dcard.manager import ContentParser, Downloader
from dcard.utils import Client, flatten_lists, chunks

logger = logging.getLogger('dcard')


class Post:

    reduce_threshold = 1000
    comments_per_page = 30
    client = Client()

    def __init__(self, metadata):
        metadata = metadata if isinstance(metadata, list) else [metadata]
        self.only_id = type(metadata[0]) is int

        self.ids = metadata if self.only_id else [m['id'] for m in metadata]
        self.metas = metadata if not self.only_id else None

    def get(self, **kwargs):
        if self.only_id:
            raw_posts = self.get_posts_by_id(**kwargs)
            return PostsResult(raw_posts, massive=False)
        else:
            raw_posts = self.get_post_by_meta(**kwargs)
            return PostsResult(raw_posts)

    def get_posts_by_id(self, content=True, links=True, comments=True):
        return {
            'content': self.get_content(self.ids) if content else [],
            'links': self.get_links(self.ids) if links else [],
            'comments': (
                self.get_comments_serial(post_id)
                for post_id in self.ids
                if comments
            )
        }

    def get_post_by_meta(self, content=True, links=True, comments=True):
        return {
            'content': self.get_content(self.ids) if content else [],
            'links': self.get_links(self.ids) if links else [],
            'comments': (
                self.get_comments_parallel(meta['id'], meta['commentCount'])
                for meta in self.metas
                if comments
            )
        }

    @classmethod
    def get_content(cls, post_ids):
        content_futures = (
            cls.client.fut_get(
                api.post_url_pattern.format(post_id=post_id))
            for post_id in post_ids
        )
        return content_futures

    @classmethod
    def get_links(cls, post_ids):
        links_futures = (
            cls.client.fut_get(
                api.post_links_url_pattern.format(post_id=post_id))
            for post_id in post_ids
        )
        return links_futures

    @classmethod
    def get_comments_parallel(cls, post_id, comments_count):
        pages = -(-comments_count // cls.comments_per_page)
        comments_futures = (
            cls.client.fut_get(api.post_comments_url_pattern.format(post_id=post_id),
                params={'after': page * cls.comments_per_page})
            for page in range(pages)
        )
        return comments_futures

    @classmethod
    def get_comments_serial(cls, post_id):
        print('comment of %d' % post_id)
        comments_url = api.post_comments_url_pattern.format(post_id=post_id)

        params = {}
        comments = []
        while True:
            _comments = Post.client.get(comments_url, params=params)
            if len(_comments) == 0:
                break
            comments += _comments
            params['after'] = _comments[-1]['floor']

        return comments


class PostsResult:

    downloader = Downloader()

    def __init__(self, bundle, massive=True, callback=None):
        self.results = list(
            self.format(bundle, callback)
            if massive else
            self.simple_format(bundle, callback)
        )

    def __len__(self):
        return len(self.results)

    def __iter__(self):
        return self.results.__iter__()

    def __getitem__(self, key):
        return self.results[int(key)]

    def simple_format(self, bundle, callback):
        for content, links, comments in zip_longest(
            bundle['content'], bundle['links'], bundle['comments']
        ):
            post = {}
            post.update(content.result().json()) if content else None
            post.update({
                'links': links.result().json() if links else None,
                'comments': comments
            })
            yield post

    def format(self, bundle, callback):
        for content, links, comments in zip_longest(
            bundle['content'], bundle['links'], bundle['comments']
        ):
            post = {}
            post.update(content.result().json()) if content else None
            post.update({
                'links': links.result().json() if links else None,
                'comments': flatten_lists([cmts.result().json() for cmts in comments]) if comments else None
            })
            yield post

    def parse_resources(self):
        parser = ContentParser(self.results)
        return parser.parse()

    def download(self, resource_bundles):
        self.downloader.set_bundles(resource_bundles)
        return self.downloader.download()
