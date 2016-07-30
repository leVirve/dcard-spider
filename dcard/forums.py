# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import logging

from dcard import api
from dcard.utils import Client, flatten_lists

logger = logging.getLogger('dcard')


class Forum:

    metas_per_page = 30
    infinite_page = -1

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

    def get_metas(
            self, num=30, sort='new', timebound=None,
            callback=None):
        logger.info('<%s> 開始取得看板內文章資訊' % self.forum)

        paged_metas = self._get_paged_metas(sort, num, timebound)

        buff = flatten_lists((metas for metas in paged_metas))
        results = callback(buff) if callback else buff

        logger.info('<%s> 資訊蒐集完成，共%d筆' % (self.forum, len(buff)))
        return results

    def _get_paged_metas(self, sort, num, timebound=''):
        params = {'popular': False} if sort == 'new' else {}
        pages = -(-num // self.metas_per_page) if num >= 0 else self.infinite_page

        def approved_metas(metas):
            if num and page == pages:
                metas = metas[:num - (pages - 1) * self.metas_per_page]

            if timebound:
                metas = [m for m in metas if m['updatedAt'] > timebound]

            return metas

        page = 0
        while page != pages:
            page += 1
            metas = self.client.get(self.posts_meta_url, params=params)

            if len(metas) == 0:
                logger.warning('[%s] 已到最末頁，第%d頁!' % (self.forum, page))
                return

            params['before'] = metas[-1]['id']

            metas = approved_metas(metas)
            if len(metas) == 0:
                return

            yield metas

    @staticmethod
    def _extract_general(forums):
        return (forum for forum in forums if not forum['isSchool'])
