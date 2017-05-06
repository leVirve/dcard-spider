# -*- coding: utf-8 -*-

import logging
import itertools
from multiprocessing.dummy import Pool
from six.moves import http_client as httplib

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import RetryError

from . import prequests


logger = logging.getLogger(__name__)


class Client:

    max_retries = 5

    def __init__(self, workers=8):
        retries = Retry(
            total=self.max_retries,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504])
        session = requests.Session()
        session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session = session
        self.pool = Pool(workers)

    def get_json(self, url, **kwargs):
        response = None
        try:
            response = self.session.get(url, **kwargs)
            data = response.json()
            if type(data) is dict and data.get('error'):
                raise ServerResponsedError
            return data
        except ValueError as e:
            retries = kwargs.get('retries', 0)
            logger.error('when get <%d> %s, error %s (retry#%d)',
                         response.status_code, url, e, retries)
            return {} if retries <= self.max_retries else \
                self.get_json(url, retries=retries + 1)
        except ServerResponsedError:
            logger.error('when get <%d> %s, response: %s',
                         response.status_code, url, data)
            return {}
        except httplib.IncompleteRead as e:
            logger.error('when get %s, error %s; partial: %s',
                         url, e, e.partial)
            return {}  # or shall we return `e.partial` ?
        except RetryError as e:
            logger.error('when get %s, retry error occurs. %s', url, e)
            return {}
        except Exception as e:
            logger.error('error %s', e)
            return {}

    def get_stream(self, url, **kwargs):
        request = self.session.get(url, stream=True, **kwargs)
        return request

    def get(self, url, **kwargs):
        return prequests.get(url, session=self.session, **kwargs)

    def imap(self, reqs):
        return prequests.imap(reqs, stream=False, pool=self.pool)


def flatten_lists(meta_lists):
    return list(itertools.chain.from_iterable(meta_lists))


class ServerResponsedError(Exception):
    pass
