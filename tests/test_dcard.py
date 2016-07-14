import pytest
from dcard import Dcard


@pytest.fixture()
def forums():
    all_forums = Dcard.forums.get()
    no_school_forums = Dcard.forums.get(no_school=True)
    return {
        'all': all_forums,
        'no_school': no_school_forums,
        'test': no_school_forums[5:6]
    }


def test_forums(forums):
    all_forums = forums.get('all')
    no_school_forums = forums.get('no_school')
    assert len(all_forums) > len(no_school_forums)


def test_post_metas(forums):
    for f in forums.get('test'):
        forum = f['alias']
        metas = Dcard.forums(forum).get_metas(sort='popular')
        assert 0 <= len(metas) <= 30


def test_post_ids(forums):
    for f in forums.get('test'):
        forum = f['alias']
        metas0 = Dcard.forums(forum).get_metas(pages=0)
        metas1 = Dcard.forums(forum).get_metas()
        metas = Dcard.forums(forum).get_metas(pages=3)
        assert len(metas0) == 0
        assert 0 <= len(metas1) <= 30
        assert 0 <= len(metas) <= 90

        assert len(metas1) == 30
        assert len(metas) == 90


def test_post_bundle():
    post = Dcard.posts(224341009).get()
    comment_count = post['content']['commentCount']
    assert comment_count == len(post['comments'])
