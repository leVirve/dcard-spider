try:
    from dcard.forums import DcardForum
    from dcard.posts import DcardPost
except ImportError:
    from .forums import DcardForum
    from .posts import DcardPost

__all__ = ['Dcard']


class Dcard:

    forums = DcardForum
    posts = DcardPost
