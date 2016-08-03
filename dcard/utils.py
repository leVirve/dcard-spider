# -*- coding: utf-8 -*-

import logging
import itertools
from six.moves import http_client as httplib

import requests
import grequests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import RetryError

logger = logging.getLogger(__name__)


class Client:

    def __init__(self, workers=8):
        '''
        session = grequests.AsyncRequest(session=session)
        '''
        self.req_session = requests.Session()
        self.retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504])
        self.req_session.mount('https://', HTTPAdapter(max_retries=self.retries))

    def get(self, url, **kwargs):
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
            logger.error('when get {}, error {}; and retry#{}...'.format(url, e, man_retry))
            kwargs['man_retry'] = man_retry + 1
            return self.get(url, **kwargs)
        except ServerResponsedError:
            logger.error('when get {}, error {}; status_code {}'.format(
                url, data, response.status_code))
            return {}
        except httplib.IncompleteRead as e:
            logger.error('when get {}, error {}; partial: {}'.format(url, e, e.partial))
            return {}  # or should we return `e.partial` ?
        except RetryError as e:
            logger.error('when get {}, retry error from requests {}'.format(url, e))

    def get_stream(self, url, **kwargs):
        return self.req_session.get(url, stream=True, **kwargs)

    def grequest(self, url, **kwargs):
        return grequests.get(url, **kwargs)


def flatten_lists(meta_lists):
    return list(itertools.chain.from_iterable(meta_lists))


def gmap(greqs):
    return grequests.map(greqs)


class ServerResponsedError(Exception):
    pass
