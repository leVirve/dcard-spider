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
        self.fut_session = FuturesSession(max_workers=workers)
        self.req_session = requests.Session()
        self.retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504])
        self.req_session.mount('https://', HTTPAdapter(max_retries=self.retries))

    def _get(self, url, **kwargs):
        try:
            response = self.req_session.get(url, **kwargs)
            data = response.json()
            if isinstance(data, dict) and data.get('error'):
                raise ServerResponsedError
            return data
        except ValueError as e:
            man_retry = kwargs.get('man_retry', 1)
            if man_retry > 5:
                return {}
            logger.error(
                'when get {}, error {}; and retry#{}...'
                .format(url, e, man_retry))
            kwargs['man_retry'] = man_retry + 1
            return self._get(url, **kwargs)
        except ServerResponsedError:
            logger.error(
                'when get {}, error {}; status_code {}'
                .format(url, data, response.status_code))
            return {}
        except httplib.IncompleteRead as e:
            logger.error(
                'when get {}, error {}; partial: {}'.format(url, e, e.partial))
            return {}  # or should we return `e.partial` ?
        except RetryError as e:
            logger.error(
                'when get {}, retry error from requests {}'.format(url, e))

    def get_stream(self, url, **kwargs):
        return self.req_session.get(url, stream=True, **kwargs)

    def fut_get(self, url, **kwargs):
        return FutureRequest(self, self.fut_session.get(url, **kwargs))

    def get_json(self, url, **kwargs):
        request = self.fut_get(url, **kwargs)
        return request.json()


class FutureRequest:

    def __init__(self, caller, future):
        self.future = future
        self.caller = caller
        self.manual_retry = 0

    def json(self):
        response = None
        try:
            response = self.future.result()
            return response.json()
        except ValueError as e:
            logger.error('when get <{}> {}, error {}'
                         .format(response.status_code, response.url, e))
            return {}
        except Exception as e:
            logger.error('when get {}, error {}'.format(response.url, e))
            return {}


def flatten_lists(meta_lists):
    return list(itertools.chain.from_iterable(meta_lists))


class ServerResponsedError(Exception):
    pass
