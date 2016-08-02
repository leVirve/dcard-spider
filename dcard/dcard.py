from __future__ import absolute_import

from dcard.forums import Forum
from dcard.posts import Post
from dcard.utils import Client


__all__ = ['Dcard']


class Dcard:

    def __init__(self):
        self.client = Client()
        self.forums = Forum(client=self.client)
        self.posts = Post(client=self.client)
