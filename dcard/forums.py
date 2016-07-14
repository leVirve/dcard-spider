# -*- coding: utf-8 -*-

import logging
try:
    from dcard import api
    from dcard.utils import Client, filter_general
except ImportError:
    from . import api
    from .utils import Client, filter_general


logger = logging.getLogger('dcard')


class Forum:

    def __init__(self, forum):
        self.forum = forum

    def get_metas(self, pages=1, sort='new', callback=None):
        params = {'popular': True if sort == 'popular' else False}
        results = []
        for metas in Forum.get_post_metas(self.forum, pages=pages, params=params):
            result = callback(metas) if callback else metas
            if isinstance(result, list):
                results += result
            else:
                results.append(result)
        logger.info('資訊蒐集完成，共%d筆' % len(results))
        return results

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
        logger.info('開始取得看板 [%s] 內文章資訊' % forum)
        for _ in range(pages):
            data = Client.get(Forum.build_url(forum), params=params)
            try:
                params['before'] = data[-1]['id']
                yield data
            except IndexError:
                logger.warning('已到最末頁，第%d頁!' % _)
                break
