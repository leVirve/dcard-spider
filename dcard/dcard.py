try:
    from dcard.forums import Forum
    from dcard.posts import DcardPost
except ImportError:
    from .forums import Forum
    from .posts import DcardPost

__all__ = ['Dcard']


class Dcard:

    forums = Forum
    posts = DcardPost
