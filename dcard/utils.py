# -*- coding: utf-8 -*-

import os
import itertools
from multiprocessing.dummy import Pool

import requests
from requests_futures.sessions import FuturesSession


class Client:

    def __init__(self):
        self.session = FuturesSession(max_workers=10)
        self.thread_pool = Pool(processes=8)

    @staticmethod
    def get(url, **kwargs):
        response = requests.get(url, **kwargs)
        return response.json()

    @staticmethod
    def get_stream(url, **kwargs):
        return requests.get(url, stream=True, **kwargs)

    def sget(self, url, **kwargs):
        return self.session.get(url, **kwargs)

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
