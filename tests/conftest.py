import pytest
from dcard import Dcard


@pytest.fixture(scope='module')
def forums():
    all_forums = Dcard.forums.get()
    no_school_forums = Dcard.forums.get(no_school=True)
    return {
        'all': all_forums,
        'no_school': no_school_forums,
        'test': no_school_forums[-1]
    }


@pytest.fixture(scope='module')
def article_id():
    return 224341009
