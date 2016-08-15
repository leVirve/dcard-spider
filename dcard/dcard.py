from __future__ import absolute_import

from dcard.forums import Forum
from dcard.posts import Post
from dcard.manager import Downloader
from dcard.utils import Client


__all__ = ['Dcard']


class Dcard:

    def __init__(self, workers=8):
        self.client = Client(workers=workers)

        self.forums = Forum(client=self.client)
        self.posts = Post(client=self.client)

        Downloader.client = self.client
