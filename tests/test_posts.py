from dcard import Dcard


def test_post_bundle():
    post = Dcard.posts(224341009).get()
    comment_count = post['content']['commentCount']
    assert comment_count == len(post['comments'])


def test_post_bundles(forums):
    forum = forums.get('test')['alias']
    
    metas = Dcard.forums(forum).get_metas(pages=1)
    ids   = [m['id'] for m in metas]

    posts1 = Dcard.posts(metas).get(comments=False)
    posts2 = Dcard.posts(ids).get(comments=False)
    assert len(posts1) == len(posts2)
