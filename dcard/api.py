# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
from itertools import takewhile, count
try:
    from functools import partialmethod
except ImportError:
    from functools import partial

    class partialmethod(partial):
        def __get__(self, instance, owner):
            if instance is None:
                return self
            return partial(
                self.func, instance,
                *(self.args or ()), **(self.keywords or {}))

from six.moves import zip

from dcard.utils import Client

logger = logging.getLogger(__name__)


class Api():

    metas_per_page = 30
    comments_per_page = 30

    def __init__(self, workers=8):
        self.client = Client(workers=workers)

    def get_all_forums(self):
        return self.client.get_json(route.forums())

    def get_general_forums(self):
        forums = self.client.get_json(route.forums())
        return [forum for forum in forums if not forum['isSchool']]

    def get_metas(self, name, sort, num, before, timebound=''):

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
                logger.warning('[%s] 已到最末頁，第%d頁!', name, page)
            return len(metas) != 0

        def get_single_page_metas():
            while True:
                yield self.client.get_json(url, params=params)

        url = route.posts_meta(name)
        params = {'popular': 'true' if sort == 'popular' else 'false'}
        if before:
            params['before'] = before

        pages = -(-num // self.metas_per_page)

        paged_metas = zip(count(start=1), get_single_page_metas())

        for page, metas in takewhile(eager_for_metas, paged_metas):
            params['before'] = metas[-1]['id']
            metas = filter_metas(metas)
            if len(metas) == 0:
                return
            yield metas

    def get_post(self, post_id, addition=None, params=None):
        req = self.client.get(route.post(post_id, addition=addition), params=params)
        return req

    get_post_links = partialmethod(get_post, addition='links')

    def imap(self, *args, **kwargs):
        return self.client.imap(*args, **kwargs)

    def get_json(self, *args, **kwargs):
        return self.client.get_json(*args, **kwargs)


class Route():

    host = 'https://www.dcard.tw/'

    def forums(self):
        return Route.host + '_api/forums'

    def posts_meta(self, forum):
        return Route.host + '_api/forums/{forum}/posts'.format(forum=forum)

    def post(self, post_id, addition=None):
        base = Route.host + '_api/posts/{id}'.format(id=post_id)
        if addition:
            return base + '/' + addition
        return base

    post_links = partialmethod(post, addition='links')
    post_comments = partialmethod(post, addition='comments')


route = Route()
api = Api()
