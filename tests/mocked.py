import re
import json
import codecs


post_metas_requests = 0


class MockedRequest:

    mapping = [
        (re.compile('forums$'), 'forums_all.json'),
        (re.compile('forums/\w+/posts$'), 'post_metas.json'),
        (re.compile('posts/\d+$'), 'single_post_content.json'),
        (re.compile('posts/\d+/links$'), 'single_post_links.json'),
        (re.compile('posts/\d+/comments$'), 'single_post_comments.json'),
    ]

    @staticmethod
    def request(*args, **kwargs):

        url = kwargs.get('url') or \
            (args[0] if isinstance(args[0], str) else args[2])
        params = kwargs.get('params')

        if kwargs.get('stream'):
            return StreamResponse('./tests/data/' + 'sample.jpg')

        for i, bundle in enumerate(MockedRequest.mapping):

            regex, path = bundle

            if regex.search(url) is not None:
                json = JsonResponse('./tests/data/' + path)
                if i == 1 and kwargs.get('params').get('before'):
                    global post_metas_requests
                    post_metas_requests += 1
                    if post_metas_requests >= 50:  # cheating hacks Orz
                        return JsonResponse()
                elif i == 4:
                    json.comments_case = True
                    json.start = params.get('after', 0) if params else 0
                return json


class JsonResponse:

    def __init__(self, path=None, ok=True):
        self.f = codecs.open(path, 'r', 'utf-8') if path else path
        self.ok = ok
        self.comments_case = False

    def result(self):
        return self

    def json(self):
        result = json.load(self.f) if self.f else []
        self.f.close() if self.f else None

        if self.comments_case:
            start = self.start
            end = start + 30 if start + 30 < len(result) else len(result)
            result = result[start:end]

        return result


class StreamResponse:

    def __init__(self, path=None):
        self.ok = True
        self.f = open(path, 'rb')

    def iter_content(self, chunk_size):
        while True:
            data = self.f.read(chunk_size)
            if not data:
                break
            yield data
