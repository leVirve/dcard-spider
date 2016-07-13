try:
    from dcard import api
    from dcard.utils import get, filter_general
except ImportError:
    from . import api
    from .utils import get, filter_general

class DcardForum:

    @staticmethod
    def get(**kwargs):
        url = '{api_root}/{api_forums}'.format(
            api_root=api.API_ROOT,
            api_forums=api.FORUMS
        )
        forums = get(url)

        if kwargs.get('no_school'):
            return [forum for forum in filter_general(forums)]

        return forums

    @staticmethod
    def _get_single_page(forum, params):
        url = '{api_root}/{api_forums}/{forum}/{api_posts}'.format(
            api_root=api.API_ROOT,
            api_forums=api.FORUMS,
            api_posts=api.POSTS,
            forum=forum
        )
        return get(url, params=params)

    @staticmethod
    def get_post_metas(forum, pages=1, params=None):
        metas = []
        for _ in range(pages):
            metas += DcardForum._get_single_page(forum, params)
            try:
                params['before'] = metas[-1]['id']
            except IndexError:
                break
        return metas
