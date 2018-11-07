import datetime

import pytest

from dcard import Dcard
from dcard.utils import Client


@pytest.fixture(scope='module')
def dcard():
    return Dcard()


@pytest.fixture(scope='module')
def boundary_date():
    return datetime.datetime.utcnow() - datetime.timedelta(days=1)


@pytest.fixture(scope='module')
def metas(dcard):
    return dcard.forums('photography').get_metas()


@pytest.fixture(scope='module')
def client():
    return Client()
