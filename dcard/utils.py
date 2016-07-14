import logging

import requests
from requests_futures.sessions import FuturesSession


class Client:

    def __init__(self):
        self.session = FuturesSession(max_workers=10)

    @staticmethod
    def get(url, verbose=False, **kwargs):
        response = requests.get(url, **kwargs)
        if verbose:
            logging.info(response.url)
        return response.json()

    def sget(self, url, **kwargs):
        return self.session.get(url, **kwargs)


def filter_general(forums):
    for forum in forums:
        if not forum['isSchool']:
            yield forum
