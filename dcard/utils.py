# -*- coding: utf-8 -*-

import os
import logging
import itertools
from multiprocessing.dummy import Pool

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import RetryError
from requests_futures.sessions import FuturesSession

logger = logging.getLogger('dcard')


class Client:

    def __init__(self, workers=8):
        self.fut_session = FuturesSession(max_workers=workers)
        self.req_session = requests.Session()
        self.thread_pool = Pool(processes=workers)
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
                logger.error('when get {}, error {}'.format(url, data))
                return {}
            return data
        except RetryError as e:
            logger.error('when get {}, error {}'.format(url, e))

    def get_stream(self, url, **kwargs):
        return self.req_session.get(url, stream=True, **kwargs)

    def fut_get(self, url, **kwargs):
        return self.fut_session.get(url, **kwargs)

    def parallel_tasks(self, function, tasks):
        return self.thread_pool.map_async(function, tasks)

    @staticmethod
    def flatten_result_lists(meta_lists):
        return list(itertools.chain.from_iterable(meta_lists))

    @staticmethod
    def chunks(elements, chunck_size=30):
        for i in range(0, len(elements), chunck_size):
            yield elements[i:i+chunck_size]

client = Client()
