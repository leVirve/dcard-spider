"""
prequests
~~~~~~~~~

An easy copy of `https://github.com/leVirve/prequests` for convenient.

This module contains an asynchronous replica of ``requests.api``, powered
by futures. All API methods return a ``Request`` instance (as opposed to
``Response``). A list of requests can be sent with ``map()``.
"""

import traceback
import contextlib
from functools import partial
from multiprocessing.dummy import Pool

try:
    from requests import Session
    from fake_useragent import UserAgent
except ImportError:
    raise RuntimeError('`requests` and `fake_useragent` are required.')


__all__ = (
    'map', 'imap', 'imap_unordered',
    'get', 'options', 'head', 'post', 'put', 'patch', 'delete', 'request'
)

ua = UserAgent()


class AsyncRequest(object):
    """ Asynchronous request.

    Accept same parameters as ``Session.request`` and some additional:

    :param session: Session which will do request
    :param callback: Callback called on response.
    Same as passing ``hooks={'response': callback}``
    """
    def __init__(self, method, url, **kwargs):
        #: Request method
        self.method = method
        #: URL to request
        self.url = url
        #: Associated ``Session``
        self.session = kwargs.pop('session', None)
        if self.session is None:
            self.session = Session()
            self.session.headers['User-Agent'] = ua.random

        callback = kwargs.pop('callback', None)
        if callback:
            kwargs['hooks'] = {'response': callback}

        #: The rest arguments for ``Session.request``
        self.kwargs = kwargs
        #: Resulting ``Response``
        self.response = None

    def send(self, **kwargs):
        """
        Prepares request based on parameter passed to constructor and optional
        ``kwargs```. Then sends request and saves response to :attr:`response`.

        :returns: ``Response``
        """
        merged_kwargs = {}
        merged_kwargs.update(self.kwargs)
        merged_kwargs.update(kwargs)
        try:
            self.response = self.session.request(
                                self.method, self.url, **merged_kwargs)
        except Exception as e:
            self.exception = e
            self.traceback = traceback.format_exc()
        return self


def send(r, stream=False):
    """Just sends the request using its send method and returns its response.  """
    r.send(stream=stream)
    return r.response


# Shortcuts for creating AsyncRequest with appropriate HTTP method
get = partial(AsyncRequest, 'GET')
options = partial(AsyncRequest, 'OPTIONS')
head = partial(AsyncRequest, 'HEAD')
post = partial(AsyncRequest, 'POST')
put = partial(AsyncRequest, 'PUT')
patch = partial(AsyncRequest, 'PATCH')
delete = partial(AsyncRequest, 'DELETE')


# synonym
def request(method, url, **kwargs):
    return AsyncRequest(method, url, **kwargs)


def map(requests, stream=True, pool=None, size=1, exception_handler=None):
    """Concurrently converts a list of Requests to Responses.

    :param requests: a collection of Request objects.
    :param stream: If False, the content will not be downloaded immediately.
    :param size: Specifies the number of workers to run at a time. If 1, no parallel processing.
    :param exception_handler: Callback function, called when exception occured. Params: Request, Exception
    """

    pool = pool if pool else Pool(size)
    requests = list(requests)

    requests = pool.map(send, requests)

    ret = []
    for request in requests:
        if request.response is not None:
            ret.append(request.response)
        elif exception_handler and hasattr(request, 'exception'):
            ret.append(exception_handler(request, request.exception))
        else:
            ret.append(None)

    if not pool:
        pool.close()

    return ret


def imap(requests, stream=True, pool=None, size=2, exception_handler=None):
    """Concurrently converts a generator object of Requests to
    a generator of Responses.

    :param requests: a generator of Request objects.
    :param stream: If False, the content will not be downloaded immediately.
    :param size: Specifies the number of requests to make at a time. default is 2
    :param exception_handler: Callback function, called when exception occured. Params: Request, Exception
    """

    def send(r):
        return r.send(stream=stream)

    pool = pool if pool else Pool(size)

    for request in pool.imap(send, requests):
        if request.response is not None:
            yield request.response
        elif exception_handler:
            exception_handler(request, request.exception)

    if not pool:
        pool.close()


def imap_unordered(requests, stream=True, pool=None, size=2, exception_handler=None):
    """Concurrently converts a generator object of Requests to
    a generator of Responses.

    :param requests: a generator of Request objects.
    :param stream: If False, the content will not be downloaded immediately.
    :param size: Specifies the number of requests to make at a time. default is 2
    :param exception_handler: Callback function, called when exception occured. Params: Request, Exception
    """

    def send(r):
        return r.send(stream=stream)

    pool = pool if pool else Pool(size)

    with contextlib.closing(Pool(size)) as pool:
        for request in pool.imap_unordered(send, requests):
            if request.response is not None:
                yield request.response
            elif exception_handler:
                exception_handler(request, request.exception)

    if not pool:
        pool.close()
