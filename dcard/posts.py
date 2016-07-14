try:
    from dcard import api
    from dcard.utils import Client
except ImportError:
    from . import api
    from .utils import Client


class Post:

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
        return Client.get(post_url)

    @staticmethod
    def get_links(post_url):
        links_url = '{post_url}/links'.format(post_url=post_url)
        return Client.get(links_url)

    @staticmethod
    def get_comments(post_url):
        comments_url = '{post_url}/comments'.format(post_url=post_url)
        
        params = {}
        comments = []
        while True:
            _comments = Client.get(comments_url, params=params, verbose=True)
            if len(_comments) == 0:
                break
            comments += _comments
            params['after'] = _comments[-1]['floor']

        return comments

    @staticmethod
    def single_get(post_meta=None, post_id=None):
        post_id = post_id if post_id else post_meta['id']
        post_url = Post.build_url(post_id)
        return {
            'content': Post.get_content(post_url),
            'links': Post.get_links(post_url),
            'comments': Post.get_comments(post_url)
        }


    @staticmethod
    def get(post_meta=None, post_id=None):
        if isinstance(post_meta, list):
            return [Post.single_get(m) for m in post_meta]
        elif isinstance(post_id, list):
            return [Post.single_get(i) for i in post_id]
        else:
            return Post.single_get(post_meta=post_meta, post_id=post_id)
