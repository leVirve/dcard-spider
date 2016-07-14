try:
    from dcard import api
    from dcard.utils import Client
except ImportError:
    from . import api
    from .utils import Client

client = Client()


class Post:

    def __init__(self):
        pass

    @staticmethod
    def build_url(post_id):
        post_url = '{api_root}/{api_posts}/{post_id}'.format(
            api_root=api.API_ROOT,
            api_posts=api.POSTS,
            post_id=post_id
        )
        return post_url

    @staticmethod
    def get_content(post_url):
        return client.sget(post_url)

    @staticmethod
    def get_links(post_url):
        links_url = '{post_url}/links'.format(post_url=post_url)
        return client.sget(links_url)

    @staticmethod
    def get_comments(post_url):
        comments_url = '{post_url}/comments'.format(post_url=post_url)

        params = {}
        comments = []
        while True:
            _comments = Client.get(comments_url, params=params)
            if len(_comments) == 0:
                break
            comments += _comments
            params['after'] = _comments[-1]['floor']

        return comments

    @staticmethod
    def _get(post_ids, **kwargs):

        post_urls = [Post.build_url(i) for i in post_ids]

        crawl_links    = kwargs.get('links', True)
        crawl_content  = kwargs.get('content', True)
        crawl_comments = kwargs.get('comments', True)

        if crawl_links:
            links_futures = [Post.get_links(url) for url in post_urls]
        if crawl_content:
            content_futures = [Post.get_content(url) for url in post_urls]

        results = [{}] * len(post_urls)
        if crawl_links:
            for i, f in enumerate(links_futures):
                results[i]['links'] = f.result().json()
        if crawl_content:
            for i, f in enumerate(content_futures):
                results[i]['content'] = f.result().json()
        if crawl_comments:
            for i, url in enumerate(post_urls):
                results[i]['comments'] = Post.get_comments(url)

        return results

    @staticmethod
    def get(post_meta=None, post_id=None, **kwargs):
        ids = []
        if post_meta:
            if isinstance(post_meta, list):
                ids = [m['id'] for m in post_meta]
            else:
                ids = [post_meta['id']]
        if post_id:
            if isinstance(post_id, list):
                ids = post_id
            else:
                ids = [post_id]
        return Post._get(ids, **kwargs)
