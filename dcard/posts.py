from __future__ import absolute_import

import logging
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
        raw_posts = {
            'content': self.get_content(self.ids) if content else [],
            'links': self.get_links(self.ids) if links else [],
            'comments': self.get_comments(self.ids, self.metas) if comments else ()
        }
        return PostsResult(raw_posts, massive=(not self.use_only_id))

    def get_content(self, post_ids):
        content_futures = (
            self.client.fut_get(
                api.post_url_pattern.format(post_id=post_id))
            for post_id in post_ids
        )
        return content_futures

    def get_links(self, post_ids):
        links_futures = (
            self.client.fut_get(
                api.post_links_url_pattern.format(post_id=post_id))
            for post_id in post_ids
        )
        return links_futures

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
        comments_futures = (
            self.client.fut_get(
                api.post_comments_url_pattern.format(post_id=post_id),
                params={'after': page * self.comments_per_page})
            for page in range(pages)
        )
        return comments_futures

    def get_comments_serial(self, post_id):
        comments_url = api.post_comments_url_pattern.format(post_id=post_id)

        params = {}
        comments = []
        while True:
            _comments = self.client.get(comments_url, params=params)
            if len(_comments) == 0:
                break
            comments += _comments
            params['after'] = _comments[-1]['floor']

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
            post.update(content.json()) if content else None
            post.update({
                'links': links.json() if links else None,
                'comments': self.extract_comments(comments)
            })
            yield post

    def extract_comments(self, comments):
        return flatten_lists([cmts.json() for cmts in comments]) \
            if self.massive and comments else comments

    def parse_resources(self):
        parser = ContentParser(self.results)
        return parser.parse()

    def download(self, resource_bundles):
        self.downloader.set_bundles(resource_bundles)
        return self.downloader.download()
