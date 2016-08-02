import datetime

import pytest

from dcard import Dcard
from dcard.utils import Client

from tests.mocked import MockedRequest


@pytest.fixture(autouse=True)
def mock_all_requests(monkeypatch):
    monkeypatch.setattr('requests.sessions.Session.request', MockedRequest.request)


@pytest.fixture(scope='module')
def dcard():
    return Dcard()


@pytest.fixture(scope='module')
def boundary_date():
    return datetime.datetime.utcnow() - datetime.timedelta(days=1)


@pytest.fixture(scope='module')
def metas(dcard):
    return dcard.forums('testfixure').get_metas()


@pytest.fixture(scope='module')
def client():
    return Client()
