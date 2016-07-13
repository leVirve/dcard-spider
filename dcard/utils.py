import requests
import logging


class Client:

    @staticmethod
    def get(url, verbose=False, **kwargs):
        response = requests.get(url, **kwargs)
        if verbose:
            logging.info(response.url)
        return response.json()


def filter_general(forums):
    for forum in forums:
        if not forum['isSchool']:
            yield forum
