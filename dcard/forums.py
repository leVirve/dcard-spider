# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import logging
from dcard import api
from dcard.utils import Client


logger = logging.getLogger('dcard')


def filter_general(forums):
    for forum in forums:
        if not forum['isSchool']:
            yield forum


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
        forums = Client.get(api.forums_url)
        if kwargs.get('no_school'):
            return [forum for forum in filter_general(forums)]
        return forums

    @staticmethod
    def get_post_metas(forum, pages, params):
        logger.info('開始取得看板 [%s] 內文章資訊' % forum)
        posts_meta_url = api.posts_meta_url_pattern.format(forum=forum)
        for _ in range(pages):
            data = Client.get(posts_meta_url, params=params)
            try:
                params['before'] = data[-1]['id']
                yield data
            except IndexError:
                logger.warning('已到最末頁，第%d頁!' % _)
                break
