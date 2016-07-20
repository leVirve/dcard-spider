import re
import json
import codecs


class MockedRequest:

    mapping = [
        (re.compile('forums$'), 'forums-all.json'),
        (re.compile('forums/\w+/posts$'), 'post_metas.json'),
        (re.compile('posts/\d+$'), 'single_post.json'),
        (re.compile('posts/\d+/links$'), 'single_post.json'),
        (re.compile('posts/\d+/comments$'), 'single_post_single_comments.json'),
    ]

    @staticmethod
    def request(*args, **kwargs):

        url = kwargs.get('url') or \
            (args[0] if isinstance(args[0], str) else args[2])
        params = kwargs.get('params')

        for i, bundle in enumerate(MockedRequest.mapping):

            regex, path = bundle
    
            if regex.search(url) is not None:
                if i == 0 and kwargs.get('no_school'):
                   path = 'forums.json'
                elif i == 4 and params and params.get('after', 0) == 30:
                    path = 'single_post_comments.json'
                elif i == 4 and params and params.get('after', 0) > 30:
                    return JsonResponse()
                return JsonResponse('./tests/data/' + path)


class JsonResponse:

    def __init__(self, path=None, ok=True):
        self.f = codecs.open(path, 'r', 'utf-8') if path else path
        self.ok = ok

    def result(self):
        print('ffffffffffff')
        return self

    def json(self):
        result = json.load(self.f) if self.f else []
        self.f.close() if self.f else None
        return result
