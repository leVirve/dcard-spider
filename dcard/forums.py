# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import logging
import itertools

from dcard import api
from dcard.utils import Client

logger = logging.getLogger('dcard')


class Forum:

    def __init__(self, forum):
        self.forum = forum
        self.posts_meta_url = api.posts_meta_url_pattern.format(forum=forum)

    @staticmethod
    def get(no_school=False):
        forums = Client.get(api.forums_url)
        if no_school:
            return [forum for forum in Forum._extract_general(forums)]
        return forums

    def get_metas(self, pages=1, sort='new', callback=None):
        logger.info('開始取得看板 [%s] 內文章資訊' % self.forum)

        results = [
            callback(metas) if callback else metas
            for metas in self._get_metas(pages, sort)
        ]

        if len(results) and isinstance(results[0], list):
            results = Forum._flatten_result_lists(results)

        logger.info('資訊蒐集完成，共%d筆' % len(results))
        return results

    def _get_metas(self, pages, sort):
        params = {'popular': False} if sort == 'new' else {}
        for _ in range(pages):
            data = Client.get(self.posts_meta_url, params=params)
            try:
                params['before'] = data[-1]['id']
                yield data
            except IndexError:
                logger.warning('已到最末頁，第%d頁!' % _)
                return

    @staticmethod
    def _flatten_result_lists(meta_lists):
        return list(itertools.chain.from_iterable(meta_lists))

    @staticmethod
    def _extract_general(forums):
        return (forum for forum in forums if not forum['isSchool'])
