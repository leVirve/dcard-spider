from __future__ import absolute_import
from six.moves import zip_longest

import re
import os
from multiprocessing.dummy import Pool

from dcard import api
from dcard.utils import Client, download


client = Client()
thread_pool = Pool(processes=8)


reg_images    = re.compile('http[s]?://\S+\.(?:jpg|png|gif)')
reg_imgur     = re.compile('http[s]?://imgur.com/(\w+)')
reg_imgur_file = re.compile('http[s]?://i.imgur.com/\w+\.(?:jpg|png|gif)')
pattern_imgur_file = 'http://i.imgur.com/{img_hash}.jpg'


def parallel_tasks(function, tasks):
    return thread_pool.map_async(function, tasks)


class Post:

    def __init__(self, metas):
        '''
        :params `metas`: list of article_metas/ids, or one article_meta/id,
                        article_meta must contain `id` field
        '''
        if isinstance(metas, list):
            first = metas[0]
            ids = [meta['id'] for meta in metas] if isinstance(first, dict) else metas
        else:
            ids = [metas['id']] if isinstance(metas, dict) else [metas]
        self.ids = ids

    @staticmethod
    def get_comments(post_id):
        comments_url = api.post_comments_url_pattern.format(post_id=post_id)

        params = {}
        comments = []
        while True:
            _comments = Client.get(comments_url, params=params)
            if len(_comments) == 0:
                break
            comments += _comments
            params['after'] = _comments[-1]['floor']

        return comments

    def get(self, content=True, comments=True, links=True):
        bundle = {}
        if links:
            bundle['links_futures'] = [
                client.sget(api.post_links_url_pattern.format(post_id=post_id))
                for post_id in self.ids
            ]
        if content:
            bundle['content_futures'] = [
                client.sget(api.post_url_pattern.format(post_id=post_id))
                for post_id in self.ids
            ]
        if comments:
            bundle['comments_async'] = parallel_tasks(Post.get_comments, self.ids)

        return PostsResult(self.ids, bundle)


class PostsResult:

    def __init__(self, ids, bundle):
        self.ids = ids
        self.results = self.format(bundle)

    def __len__(self):
        return len(self.results)

    def __getitem__(self, key):
        ''' for single post result '''
        return self.results[key]

    def __iter__(self):
        return self.results.__iter__()

    def format(self, bundle):
        links = bundle.get('links_futures', [])
        content = bundle.get('content_futures', [])
        comments = bundle.get('comments_async')
        comments = comments.get() if comments else []

        results = [
            {
                'links': lnks.result().json() if lnks else None,
                'content': cont.result().json() if cont else None,
                'comments': cmts,
            } for lnks, cont, cmts in zip_longest(links, content, comments)
        ]

        return results[0] if len(results) == 1 else results

    def parse_resources(self, constraints=None):

        def validate(post):
            ''' crazy impl. XD '''
            if not constraints:
                return True

            _post = post['content']
            for key, rule in constraints.items():
                expression = "_post['%s']%s" % (key, rule)
                if eval(expression) is False:
                    return False
            return True

        def parse(post):
            article = post['content']
            content = article['content']
            imgur_files = PostsResult.find_images(content)
            return (article['id'], article['title'], imgur_files)

        if isinstance(self.results, dict):
            return [parse(self.results)] if validate(self.results) else []

        resoures = [parse(post) for post in self.results if validate(post)]
        return resoures

    @staticmethod
    def find_images(raw_data):
        imgurs = reg_imgur.findall(raw_data)
        imgur_files = reg_imgur_file.findall(raw_data)
        imgur_files += [pattern_imgur_file.format(img_hash=r) for r in imgurs]
        return imgur_files

    @staticmethod
    def download(bundles):
        tasks = []

        for bundle in bundles:
            post_id, folder, urls = bundle
            full_folder = 'downloads/%s (#%d)' % (folder, post_id)

            if len(urls) == 0:
                continue

            if not os.path.exists(full_folder):
                os.makedirs(full_folder)

            tasks += [(url, full_folder) for url in urls]

        results = parallel_tasks(download, tasks)
        return results.get()
