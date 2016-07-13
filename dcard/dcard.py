from functools import partialmethod

from dcard.utils import get, filter_general


__all__ = ['Dcard']


class Dcard:

    API_ROOT = 'http://dcard.tw/_api'
    FORUMS = 'forums'
    POSTS = 'posts'

    @staticmethod
    def get_forums(**kwargs):
        url = '{api_root}/{api_forums}'.format(
            api_root=Dcard.API_ROOT,
            api_forums=Dcard.FORUMS
        )
        forums = get(url)

        if kwargs.get('no_school'):
            return [forum for forum in filter_general(forums)]

        return forums

    @staticmethod
    def _get_single_page(forum, params):
        url = '{api_root}/{api_forums}/{forum}/{api_posts}'.format(
            api_root=Dcard.API_ROOT,
            api_forums=Dcard.FORUMS,
            api_posts=Dcard.POSTS,
            forum=forum
        )
        return get(url, params=params)

    @staticmethod
    def get_post_metas(forum, pages=1, params=None):
        metas = []
        for _ in range(pages):
            metas += Dcard._get_single_page(forum, params)
            try:
                params['before'] = metas[-1]['id']
            except IndexError:
                break
        return metas

    get_newest_post_metas = partialmethod(get_post_metas, params={'popular': False})
    get_most_popular_post_metas = partialmethod(get_post_metas, params={'popular': True})

    @staticmethod
    def get_post_content(post_meta):
        post_url = '{api_root}/{api_posts}/{post_id}'.format(
            api_root=Dcard.API_ROOT,
            api_posts=Dcard.POSTS,
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
