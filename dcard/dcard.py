from __future__ import absolute_import

from dcard.forums import Forum
from dcard.posts import Post


__all__ = ['Dcard']


class Dcard:

    def __init__(self):
        self.forums = Forum()
        self.posts = Post()
