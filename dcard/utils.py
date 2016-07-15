import requests
from requests_futures.sessions import FuturesSession


class Client:

    def __init__(self):
        self.session = FuturesSession(max_workers=10)

    @staticmethod
    def get(url, **kwargs):
        response = requests.get(url, **kwargs)
        return response.json()

    def sget(self, url, **kwargs):
        return self.session.get(url, **kwargs)
