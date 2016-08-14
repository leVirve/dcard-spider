from __future__ import absolute_import

import logging
from itertools import takewhile
from six.moves import zip_longest

from dcard import api
from dcard.manager import ContentParser, Downloader
from dcard.utils import flatten_lists

logger = logging.getLogger(__name__)


class Post:

    comments_per_page = 30

    def __init__(self, metadata=None, client=None):
        self.use_only_id = False
        self.ids = []
        self.metas = None
        self.client = client
        self._initial_metadata(metadata)

    def __call__(self, value):
        self._initial_metadata(value)
        return self

    def get(self, content=True, links=True, comments=True):

        _content = self.get_content(self.ids) if content else []
        _links = self.get_links(self.ids) if links else []
        _comments = self.get_comments(self.ids, self.metas) if comments else ()

        def gen_posts():
            for content, links, comments in zip_longest(
                self.client.imap(_content), self.client.imap(_links), _comments
            ):
                post = {}
                post.update(content.json()) if content else None
                post.update({
                    'links': links.json() if links else None,
                    'comments': self.extract_comments(comments)
                })
                if post:
                    yield post

            logger.info('[Posts.gen_posts <gen>] Processed.')

        return PostsResult(gen_posts)

    def extract_comments(self, comments):
        return flatten_lists([cs.json() for cs in self.client.imap(comments)]) \
            if not self.use_only_id and comments else comments

    def get_content(self, post_ids):
        reqs = (
            self.client.get(api.post_url_pattern.format(post_id=post_id))
            for post_id in post_ids
        )
        return reqs

    def get_links(self, post_ids):
        reqs = (
            self.client.get(
                api.post_links_url_pattern.format(post_id=post_id))
            for post_id in post_ids
        )
        return reqs

    def get_comments(self, post_ids, post_metas):
        return (
            self.get_comments_parallel(meta['id'], meta['commentCount'])
            for meta in post_metas
        ) if post_metas else (
            self.get_comments_serial(post_id)
            for post_id in post_ids
        )

    def get_comments_parallel(self, post_id, comments_count):
        pages = -(-comments_count // self.comments_per_page)
        reqs = (
            self.client.get(
                api.post_comments_url_pattern.format(post_id=post_id),
                params={'after': page * self.comments_per_page})
            for page in range(pages)
        )
        return reqs

    def get_comments_serial(self, post_id):
        comments_url = api.post_comments_url_pattern.format(post_id=post_id)
        params = {}

        def gen_cmts():
            while True:
                yield self.client.get_json(comments_url, params=params)

        comments = []
        for cmts in takewhile(lambda x: len(x), gen_cmts()):
            comments += cmts
            params['after'] = cmts[-1]['floor']

        return comments

    def _initial_metadata(self, metadata):
        if not metadata:
            return
        metadata = metadata if isinstance(metadata, list) else [metadata]
        self.use_only_id = type(metadata[0]) is int
        self.ids = metadata if self.use_only_id else [m['id'] for m in metadata]
        self.metas = metadata if not self.use_only_id else None


class PostsResult:

    downloader = Downloader()
    parser = ContentParser()

    def __init__(self, generator):
        logger.info('[PostResult] takes hand.')
        self.results = generator()

    def result(self):
        self.results = list(self.results)
        return self.results

    def parse_resources(self):
        self.parser.posts = self.results
        return self.parser.parse()

    def download(self, resource_bundles):
        self.downloader.resource_bundles = resource_bundles
        return self.downloader.download()
