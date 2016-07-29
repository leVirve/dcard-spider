from __future__ import absolute_import

import logging
from six.moves import zip_longest

from dcard import api
from dcard.manager import ContentParser, Downloader
from dcard.utils import Client, flatten_lists, chunks

logger = logging.getLogger('dcard')


class Post:

    comments_per_page = 30
    client = Client()

    def __init__(self, metadata):
        metadata = metadata if isinstance(metadata, list) else [metadata]
        self.only_id = type(metadata[0]) is int

        self.ids = metadata if self.only_id else [m['id'] for m in metadata]
        self.metas = metadata if not self.only_id else None

    def get(self, content=True, links=True, comments=True):
        raw_posts = {
            'content': self.get_content(self.ids) if content else [],
            'links': self.get_links(self.ids) if links else [],
            'comments': self.get_comments(self.ids, self.metas) if comments else ()
        }
        return PostsResult(raw_posts, massive=(not self.only_id))

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
    def get_comments(cls, post_ids, post_metas):
        return (
            cls.get_comments_parallel(meta['id'], meta['commentCount'])
            for meta in post_metas
        ) if post_metas else (
            cls.get_comments_serial(post_id)
            for post_id in post_ids
        )

    @classmethod
    def get_comments_parallel(cls, post_id, comments_count):
        pages = -(-comments_count // cls.comments_per_page)
        comments_futures = (
            cls.client.fut_get(
                api.post_comments_url_pattern.format(post_id=post_id),
                params={'after': page * cls.comments_per_page})
            for page in range(pages)
        )
        return comments_futures

    @classmethod
    def get_comments_serial(cls, post_id):
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
        logger.info('[PostResult] takes hand.')
        self.massive = massive
        self.results = list(self.reformat(bundle, callback))
        logger.info('[PostResult] {} posts processed.'.format(len(self.results)))

    def __len__(self):
        return len(self.results)

    def __iter__(self):
        return self.results.__iter__()

    def __getitem__(self, key):
        return self.results[int(key)]

    def reformat(self, bundle, callback):
        for content, links, comments in zip_longest(
            bundle['content'], bundle['links'], bundle['comments']
        ):
            post = {}
            post.update(content.result().json()) if content else None
            post.update({
                'links': links.result().json() if links else None,
                'comments': self.extract_comments(comments)
            })
            yield post

    def extract_comments(self, comments):
        return flatten_lists([cmts.result().json() for cmts in comments]) \
            if self.massive and comments else comments

    def parse_resources(self):
        parser = ContentParser(self.results)
        return parser.parse()

    def download(self, resource_bundles):
        self.downloader.set_bundles(resource_bundles)
        return self.downloader.download()
