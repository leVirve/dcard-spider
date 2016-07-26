# -*- coding: utf-8 -*-

import os
import itertools
from multiprocessing.dummy import Pool

import requests
from requests_futures.sessions import FuturesSession


class Client:

    def __init__(self):
        self.fut_session = FuturesSession(max_workers=8)
        self.req_session = requests.Session()
        self.thread_pool = Pool(processes=8)

    def get(self, url, **kwargs):
        response = self.req_session.get(url, **kwargs)
        return response.json()

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
