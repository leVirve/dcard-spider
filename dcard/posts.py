try:
    from dcard import api
    from dcard.utils import Client
except ImportError:
    from . import api
    from .utils import Client

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

        if crawl_links:
            links_futures = [
                client.sget(api.post_links_url_pattern.format(post_id=post_id))
                for post_id in self.ids
            ]
        if crawl_content:
            content_futures = [
                client.sget(api.post_url_pattern.format(post_id=post_id))
                for post_id in self.ids
            ]

        results = [{} for _ in range(len(self.ids))]
        if crawl_links:
            for i, f in enumerate(links_futures):
                results[i]['links'] = f.result().json()
        if crawl_content:
            for i, f in enumerate(content_futures):
                results[i]['content'] = f.result().json()
        if crawl_comments:
            for i, post_id in enumerate(self.ids):
                results[i]['comments'] = Post.get_comments(post_id)

        return results[0] if len(results) == 1 else results
