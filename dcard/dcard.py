from __future__ import absolute_import

from dcard.forums import Forum
from dcard.posts import Post


__all__ = ['Dcard']


class Dcard:

    forums = Forum
    posts = Post
