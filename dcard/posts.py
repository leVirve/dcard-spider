try:
    from dcard import api
    from dcard.utils import Client
except ImportError:
    from . import api
    from .utils import Client


class Post:

    @staticmethod
    def get(post_meta=None, post_id=None):

        post_id = post_id if post_id else post_meta['id']

        post_url = '{api_root}/{api_posts}/{post_id}'.format(
            api_root=api.API_ROOT,
            api_posts=api.POSTS,
            post_id=post_id
        )
        links_url = '{post_url}/links'.format(post_url=post_url)
        comments_url = '{post_url}/comments'.format(post_url=post_url)

        params = {}

        content = Client.get(post_url)
        links = Client.get(links_url)
        comments = []
        while True:
            _comments = Client.get(comments_url, params=params, verbose=True)
            if len(_comments) == 0:
                break
            comments += _comments
            params['after'] = comments[-1]['floor']

        return {
            'content': content,
            'links': links,
            'comments': comments
        }
