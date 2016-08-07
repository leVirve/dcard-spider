# -*- coding: utf-8 -*-

import logging
import itertools
from six.moves import http_client as httplib

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import RetryError
from requests_futures.sessions import FuturesSession

logger = logging.getLogger(__name__)


class Client:

    def __init__(self, workers=8):
        retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504])
        self.session = requests.Session()
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.fut_session = FuturesSession(max_workers=workers, session=self.session)

    def get_stream(self, url, **kwargs):
        return self.session.get(url, stream=True, **kwargs)

    def fut_get(self, url, **kwargs):
        return FutureRequest(
            self, self.fut_session.get(url, **kwargs), **kwargs)

    def get_json(self, url, **kwargs):
        request = self.fut_get(url, **kwargs)
        return request.json()


class FutureRequest:

    max_retries = 3

    def __init__(self, caller, future, **kwargs):
        self.future = future
        self.caller = caller
        self.url = kwargs.get('url')
        self.retries = kwargs.get('retries', 0)
        self.response = None

    def json(self):
        response = None
        try:
            response = self.response = self.future.result()
            data = response.json()
            if type(data) is dict and data.get('error'):
                raise ServerResponsedError
            return data
        except ValueError as e:
            logger.error('when get <%d> %s, error %s (retry#%d)',
                         response.status_code, response.url, e, self.retries)
            return {} if self.retries <= self.max_retries else \
                self.caller.get_json(response.url, retries=self.retries + 1)
        except ServerResponsedError:
            logger.error('when get <%d> %s, response: %s',
                         response.status_code, response.url, data)
            return {}
        except httplib.IncompleteRead as e:
            logger.error('when get %s, error %s; partial: %s',
                         self.url, e, e.partial)
            return {}  # or shall we return `e.partial` ?
        except RetryError as e:
            logger.error('when get %s, retry error occurs. %s', self.url, e)
            return {}
        except Exception as e:
            logger.error('when get %s, error %s', response.url, e)
            return {}


def flatten_lists(meta_lists):
    return list(itertools.chain.from_iterable(meta_lists))


class ServerResponsedError(Exception):
    pass
