# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import logging
from itertools import takewhile, count

from six.moves import zip

from dcard import api
from dcard.utils import flatten_lists

logger = logging.getLogger(__name__)


class Forum:

    metas_per_page = 30
    infinite_page = -1

    def __init__(self, name=None, client=None):
        self.name = None
        self.posts_meta_url = None
        self.client = client
        self._initial_forum(name)

    def __call__(self, name):
        self._initial_forum(name)
        return self

    def get(self, no_school=False):
        forums = self.client.get_json(api.forums_url)
        if no_school:
            return [forum for forum in self._extract_general(forums)]
        return forums

    def get_metas(
            self, num=30, sort='new', timebound=None,
            callback=None):
        logger.info('<%s> 開始取得看板內文章資訊', self.name)

        paged_metas = self.get_paged_metas(sort, num, timebound)

        buff = flatten_lists(metas for metas in paged_metas)
        results = callback(buff) if callback else buff

        logger.info('<%s> 資訊蒐集完成，共%d筆', self.name, len(buff))
        return results

    def get_paged_metas(self, sort, num, timebound=''):
        params = {'popular': False} if sort == 'new' else {}
        pages = -(-num // self.metas_per_page)

        def filter_metas(metas):
            if num >= 0 and page == pages:
                metas = metas[:num - (pages - 1) * self.metas_per_page]
            if timebound:
                metas = [m for m in metas if m['updatedAt'] > timebound]
            return metas

        def eager_for_metas(bundle):
            page, metas = bundle
            if num >= 0 and page == pages + 1:
                return False
            if len(metas) == 0:
                logger.warning('[%s] 已到最末頁，第%d頁!', self.name, page)
            return len(metas) != 0

        def get_single_page_metas():
            while True:
                yield self.client.get_json(self.posts_meta_url, params=params)

        paged_metas = zip(count(start=1), get_single_page_metas())

        for page, metas in takewhile(eager_for_metas, paged_metas):
            params['before'] = metas[-1]['id']
            metas = filter_metas(metas)
            if len(metas) == 0:
                return
            yield metas

    def _initial_forum(self, name):
        self.name = name
        self.posts_meta_url = api.posts_meta_url_pattern.format(forum=name)

    def _extract_general(self, forums):
        return (forum for forum in forums if not forum['isSchool'])
