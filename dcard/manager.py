from __future__ import absolute_import, unicode_literals

import os
import re
import logging
import contextlib
from multiprocessing.dummy import Pool

from dcard.utils import flatten_lists

logger = logging.getLogger(__name__)


class Downloader:

    client = None

    def __init__(
            self, download_folder=None, subfolder_pattern=None, flatten=False):
        self.resources_folder = download_folder or './downloads'
        self.subfolder_pattern = subfolder_pattern or '({id}) {folder_name}'
        self.flatten = flatten
        self.resource_bundles = None

    def download(self):
        logger.info('[Downloader] takes hand')

        self.mkdir(self.resources_folder)

        tasks = [
            (self.get_filepath(meta, url), url)
            for meta, urls in self.resource_bundles
            for url in urls
        ]

        with contextlib.closing(Pool(8)) as pool:
            results = pool.map(self.downloading, tasks)

        status = [ok for ok, _ in results]
        fails = [src for ok, src in results if not ok]

        logger.info('[Downloader] download %d items (Total: %d)!',
                    sum(status), len(status))

        return sum(status), fails

    def get_filepath(self, meta, url):
        folder = self.get_folder_fullname(meta)
        filepath = '{folder_name}{separator}{file_name}'.format(
            folder_name=folder,
            file_name=os.path.basename(url),
            separator='-' if self.flatten else '/'
        )

        if not self.flatten:
            self.mkdir(folder)

        return filepath

    def get_folder_fullname(self, meta):
        safe_title = ''.join([
            char
            for char in re.sub('[\?\\\\/><:"|\*\.]', '', meta['title']).strip()
            if ord(char) > 0x1f
        ])

        meta['folder_name'] = safe_title
        folder = self.subfolder_pattern.format(**meta)
        return self.resources_folder + '/' + folder

    @staticmethod
    def mkdir(path):
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def save_file(resp, path):
        with open(path, 'wb') as stream:
            for chunk in resp.iter_content(chunk_size=1024):
                stream.write(chunk)

    @classmethod
    def downloading(cls, task):
        filepath, src = task

        if os.path.exists(filepath):
            return True, src
        response = cls.client.get_stream(src)

        if response.ok:
            cls.save_file(response, filepath)
        return (response.ok, src)


class ContentParser:

    reg_images = re.compile('http[s]?://\S+\.(?:jpg|png|gif)')
    reg_imgur = re.compile('http[s]?://imgur.com/(\w+)')
    reg_imgur_file = re.compile('http[s]?://i.imgur.com/\w+\.(?:jpg|png|gif)')

    pattern_imgur_file = 'http://i.imgur.com/{img_hash}.jpg'

    def __init__(self):
        self.posts = None

    def parse(self):

        def parsed_post(posts):
            for post in posts:
                article = post.get('content') or ''
                comments = post.get('comments') or []

                imgs = self.parse_images(article) + flatten_lists([
                    self.parse_images(cmt.get('content', ''))
                    for cmt in comments
                ])

                if len(imgs):
                    yield post, imgs

        logger.info('[ContentParser] takes hand')

        results, resource_count = [], 0
        for post, imgs in parsed_post(self.posts):
            del post['content']
            resource_count += len(imgs)
            results.append((post, imgs))

        logger.info('[ContentParser] collects %d resources', resource_count)

        return results

    @classmethod
    def parse_images(cls, raw):
        imgur_files = []
        imgur_files += cls.reg_imgur_file.findall(raw)
        imgur_files += [
            cls.pattern_imgur_file.format(img_hash=r)
            for r in cls.reg_imgur.findall(raw)
        ]
        return imgur_files
