import logging
try:
    from dcard import api
    from dcard.utils import Client, filter_general
except ImportError:
    from . import api
    from .utils import Client, filter_general


class Forum:

    def __init__(self, forum):
        self.forum = forum

    def get_metas(self, pages=1, sort='new'):
        params = {'popular': True if sort == 'popular' else False}
        return Forum.get_post_metas(self.forum, pages=pages, params=params)

    @staticmethod
    def get(**kwargs):
        url = '{api_root}/{api_forums}'.format(
            api_root=api.API_ROOT,
            api_forums=api.FORUMS
        )
        forums = Client.get(url)

        if kwargs.get('no_school'):
            return [forum for forum in filter_general(forums)]

        return forums

    @staticmethod
    def build_url(forum):
        url = '{api_root}/{api_forums}/{forum}/{api_posts}'.format(
            api_root=api.API_ROOT,
            api_forums=api.FORUMS,
            api_posts=api.POSTS,
            forum=forum
        )
        return url

    @staticmethod
    def get_post_metas(forum, pages, params):
        metas = []
        for _ in range(pages):
            data = Client.get(Forum.build_url(forum), params=params)
            try:
                params['before'] = data[-1]['id']
                metas += data
            except IndexError:
                logging.info('第%d頁，已經沒有文章囉!' % _)
                break
        return metas
