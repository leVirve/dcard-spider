from __future__ import absolute_import
from six.moves import zip_longest

from dcard import api
from dcard.utils import Client


client = Client()


class Post:

    def __init__(self, metas):
        '''
        :params `metas`: list of article_metas/ids, or one article_meta/id,
                        article_meta must contain `id` field
        '''
        if isinstance(metas, list):
            first = metas[0]
            ids = [meta['id'] for meta in metas] if isinstance(first, dict) else metas
        else:
            ids = [metas['id']] if isinstance(metas, dict) else [metas]
        self.ids = ids

    @staticmethod
    def get_comments(post_id):
        comments_url = api.post_comments_url_pattern.format(post_id=post_id)

        params = {}
        comments = []
        while True:
            _comments = Client.get(comments_url, params=params)
            if len(_comments) == 0:
                break
            comments += _comments
            params['after'] = _comments[-1]['floor']

        return comments

    def get(self, **kwargs):

        crawl_links    = kwargs.get('links', True)
        crawl_content  = kwargs.get('content', True)
        crawl_comments = kwargs.get('comments', True)

        bundle = {}
        if crawl_links:
            bundle['links_futures'] = [
                client.sget(api.post_links_url_pattern.format(post_id=post_id))
                for post_id in self.ids
            ]
        if crawl_content:
            bundle['content_futures'] = [
                client.sget(api.post_url_pattern.format(post_id=post_id))
                for post_id in self.ids
            ]
        if crawl_comments:
            bundle['comments'] = [
                Post.get_comments(post_id)
                for post_id in self.ids
            ]

        return PostsResult(self.ids, bundle)


class PostsResult:

    def __init__(self, ids, bundle):
        self.ids = ids
        self.results = self.format(bundle)

    def __len__(self):
        return len(self.results)

    def __getitem__(self, key):
        ''' for single post result '''
        return self.results[key]

    def __iter__(self):
        return self.results.__iter__()

    def format(self, bundle):
        links = bundle.get('links_futures', [])
        content = bundle.get('content_futures', [])
        comments = bundle.get('comments', [])

        results = [
            {
                'links': lnks.result().json() if lnks else None,
                'content': cont.result().json() if cont else None,
                'comments': cmts,
            } for lnks, cont, cmts in zip_longest(links, content, comments)
        ]

        return results[0] if len(results) == 1 else results
