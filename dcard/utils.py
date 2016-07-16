# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
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


def download(task):
    src, folder = task
    filepath = '{folder_name}/{file_name}'.format(
        folder_name=folder,
        file_name=os.path.basename(src)
    )
    response = requests.get(src, stream=True)
    if response.ok:
        with open(filepath, 'wb') as stream:
            for chunk in response.iter_content(chunk_size=1024):
                stream.write(chunk)
    else:
        print('%s can not download.' % src)
    return response.ok
