from dcard.utils import get, filter_general

__all__ = ['Dcard']


class Dcard:

    API_ROOT = 'http://dcard.tw/_api'
    FORUMS = 'forums'
    POSTS = 'posts'

    def __init__(self):
        pass

    @staticmethod
    def get_forums(**kwargs):
        url = '{api_root}/{api_forums}'.format(
            api_root=Dcard.API_ROOT, api_forums=Dcard.FORUMS)
        forums = get(url)

        if kwargs.get('no_school'):
            return [forum for forum in filter_general(forums)]

        return forums

    @staticmethod
    def get_post_metas(forum, params):
        url = '{api_root}/{api_forums}/{forum}/{api_posts}'.format(
            api_root=Dcard.API_ROOT,
            api_forums=Dcard.FORUMS,
            api_posts=Dcard.POSTS,
            forum=forum
        )
        article_metas = get(url, params=params)
        return article_metas

    @staticmethod
    def get_post_ids(forum, pages=3):
        params = {'popular': False}
        ids = []
        for _ in range(pages):
            metas = Dcard.get_post_metas(forum, params)
            ids += [e['id'] for e in metas]
            params['before'] = ids[-1]
        return ids

    @staticmethod
    def get_post_content(post_id):
        post_url = '{api_root}/{api_posts}/{post_id}'.format(
            api_root=Dcard.API_ROOT,
            api_posts=Dcard.POSTS,
            post_id=post_id
        )
        links_url = '{post_url}/links'.format(post_url=post_url)
        params = {}
        content = get(post_url)
        links = get(links_url)
        comments = []
        while True:
            comments_url = '{post_url}/comments'.format(post_url=post_url)
            _comments = get(comments_url, params=params, verbose=True)
            if len(_comments) == 0:
                break
            comments += _comments
            params['after'] = comments[-1]['floor']
        return {
            'content': content,
            'links': links,
            'comments': comments
        }

'''
https://www.dcard.tw/_api/posts/224337929/comments?popular=true
'''