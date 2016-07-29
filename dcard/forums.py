# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import logging

from dcard import api
from dcard.utils import Client, flatten_lists

logger = logging.getLogger('dcard')


class Forum:

    metas_per_page = 30
    client = Client()

    def __init__(self, forum):
        self.forum = forum
        self.posts_meta_url = api.posts_meta_url_pattern.format(forum=forum)

    @staticmethod
    def get(no_school=False):
        forums = Forum.client.get(api.forums_url)
        if no_school:
            return [forum for forum in Forum._extract_general(forums)]
        return forums

    def get_metas(self, num=30, sort='new', callback=None):
        logger.info('[%s] 開始取得看板內文章資訊' % self.forum)

        pages = -(-num // self.metas_per_page)
        paged_metas = self._get_paged_metas(pages, sort)

        # results = []
        # for page, metas in enumerate(paged_metas, start=1):
        #     if page == pages:
        #         metas = metas[:num - (pages - 1) * self.metas_per_page]
        #     results.append(callback(metas) if callback else metas) # buffer?
        #
        # if len(results) and isinstance(results[0], list):
        #     results = flatten_lists(results)

        buff = flatten_lists((metas for metas in paged_metas))[:num]
        results = callback(buff) if callback else buff

        logger.info('[%s] 資訊蒐集完成，共%d筆' % (self.forum, len(buff)))
        return results

    def _get_paged_metas(self, pages, sort):
        params = {'popular': False} if sort == 'new' else {}

        for page in range(pages):
            data = self.client.get(self.posts_meta_url, params=params)

            if len(data) == 0:
                logger.warning('[%s] 已到最末頁，第%d頁!' % (self.forum, page))
                return

            params['before'] = data[-1]['id']
            yield data

    @staticmethod
    def _extract_general(forums):
        return (forum for forum in forums if not forum['isSchool'])
