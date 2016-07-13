from functools import partial

try:
    from dcard import api
    from dcard.forums import DcardForum
    from dcard.utils import get
except ImportError:
    from . import api
    from .forums import DcardForum
    from .utils import get

__all__ = ['Dcard']


class Dcard:

    forums = DcardForum

    get_newest_post_metas = partial(DcardForum.get_post_metas, params={'popular': False})
    get_most_popular_post_metas = partial(DcardForum.get_post_metas, params={'popular': True})

    @staticmethod
    def get_post_content(post_meta):
        post_url = '{api_root}/{api_posts}/{post_id}'.format(
            api_root=api.API_ROOT,
            api_posts=api.POSTS,
            post_id=post_meta['id']
        )
        links_url = '{post_url}/links'.format(post_url=post_url)
        comments_url = '{post_url}/comments'.format(post_url=post_url)

        params = {}

        content = get(post_url)
        links = get(links_url)
        comments = []
        while True:
            _comments = get(comments_url, params=params, verbose=True)
            if len(_comments) == 0:
                break
            comments += _comments
            params['after'] = comments[-1]['floor']

        return {
            'content': content,
            'links': links,
            'comments': comments
        }
