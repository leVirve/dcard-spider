import pytest
from dcard import Dcard


@pytest.fixture()
def forums():
    all_forums = Dcard.get_forums()
    no_school_forums = Dcard.get_forums(no_school=True)
    return {'all': all_forums, 'no_school': no_school_forums}


def test_forums(forums):
    all_forums = forums.get('all')
    no_school_forums = forums.get('no_school')
    assert len(all_forums) > len(no_school_forums)


def test_post_metas(forums):
    params = {'popular': False}
    for f in forums.get('no_school'):
        forum = f['alias']
        metas = Dcard.get_post_metas(forum, params=params)
        assert 0 <= len(metas) <= 30


def test_post_ids(forums):
    for f in forums.get('no_school'):
        forum = f['alias']
        ids0 = Dcard.get_post_ids(forum, pages=0)
        ids1 = Dcard.get_post_ids(forum, pages=1)
        ids = Dcard.get_post_ids(forum)
        assert len(ids0) == 0
        assert 0 <= len(ids1) <= 30
        assert 0 <= len(ids) <= 90

        assert len(ids1) == 30
        assert len(ids) == 90
        break


def test_post_bundle():
    post = Dcard.get_post_content(224341009)
    comment_count = post['content']['commentCount']
    assert comment_count == len(post['comments'])
