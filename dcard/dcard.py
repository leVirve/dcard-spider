try:
    from dcard.forums import Forum
    from dcard.posts import Post
except ImportError:
    from .forums import Forum
    from .posts import Post

__all__ = ['Dcard']


class Dcard:

    forums = Forum
    posts = Post
