# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging

from dcard.api import api
from dcard.posts import Post
from dcard.utils import flatten_lists

__all__ = ['Dcard']

logger = logging.getLogger(__name__)


class Dcard:

    def __init__(self):
        self.forums = Forum()
        self.posts = Post()


class Forum:

    infinite_page = -1

    def __init__(self, name=None):
        self.name = name
        self.api = api

    def __call__(self, name):
        self.name = name
        return self

    def get_metas(
            self, num=30, sort='new', before=None, timebound=None,
            callback=None):
        logger.info('<%s> 開始取得看板內文章資訊', self.name)

        paged_metas = self.api.get_metas(
            self.name, sort, num, before, timebound)

        buff = flatten_lists(metas for metas in paged_metas)
        results = callback(buff) if callback else buff

        logger.info('<%s> 資訊蒐集完成，共%d筆', self.name, len(buff))
        return results

    def get(self, no_school=False):
        if no_school:
            return self.api.get_general_forums()
        return self.api.get_all_forums()
