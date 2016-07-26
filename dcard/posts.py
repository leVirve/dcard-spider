from __future__ import absolute_import
from six.moves import zip_longest

from dcard import api
from dcard.manager import ContentParser, Downloader
from dcard.utils import client


class Post:

    def __init__(self, metas):
        if isinstance(metas, list):
            first = metas[0]
            ids = [meta['id'] for meta in metas] if isinstance(first, dict) \
                else metas
        else:
            ids = [metas['id']] if isinstance(metas, dict) \
                else [metas]
        self.ids = ids

    def get(self, content=True, comments=True, links=True, callback=None):
        bundle = {}
        if links:
            bundle['links_futures'] = [
                client.sget(api.post_links_url_pattern.format(post_id=post_id))
                for post_id in self.ids
            ]
        if content:
            bundle['content_futures'] = [
                client.sget(api.post_url_pattern.format(post_id=post_id))
                for post_id in self.ids
            ]
        if comments:
            bundle['comments_async'] = \
                client.parallel_tasks(Post._get_comments, self.ids)

        return PostsResult(self.ids, bundle, callback)

    @staticmethod
    def _get_comments(post_id):
        comments_url = api.post_comments_url_pattern.format(post_id=post_id)

        params = {}
        comments = []
        while True:
            _comments = client.get(comments_url, params=params)
            if len(_comments) == 0:
                break
            comments += _comments
            params['after'] = _comments[-1]['floor']

        return comments


class PostsResult:

    reduce_threshold = 1000

    def __init__(self, ids, bundle, callback=None):
        self.ids = ids
        self.results = self.format(bundle, callback)
        self.downloader = Downloader()

    def __len__(self):
        return len(self.results)

    def __iter__(self):
        return self.results.__iter__()

    def __getitem__(self, key):
        return self.results[int(key)]

    def format(self, bundle, callback):
        links = bundle.get('links_futures', [])
        content = bundle.get('content_futures', [])
        comments = bundle.get('comments_async')
        comments = comments.get() if comments else []

        posts, results = [], []
        for lnks, cont, cmts in zip_longest(links, content, comments):
            post = {}
            post.update(cont.result().json()) if cont else None
            post.update({
                'links': lnks.result().json() if lnks else None,
                'comments': cmts,
            })
            posts.append(post)

            if len(posts) >= PostsResult.reduce_threshold:
                results.append(callback(posts) if callback else posts)
                posts = []
        results.append(callback(posts) if callback else posts)

        if len(results) and isinstance(results[0], list):
            results = client.flatten_result_lists(results)

        return results

    def parse_resources(self):
        parser = ContentParser(self.results)
        return parser.parse()

    def download(self, resource_bundles):
        self.downloader.set_bundles(resource_bundles)
        return self.downloader.download()
