from __future__ import absolute_import, unicode_literals

import os
import re

from dcard.utils import client


reg_images    = re.compile('http[s]?://\S+\.(?:jpg|png|gif)')
reg_imgur     = re.compile('http[s]?://imgur.com/(\w+)')
reg_imgur_file = re.compile('http[s]?://i.imgur.com/\w+\.(?:jpg|png|gif)')
pattern_imgur_file = 'http://i.imgur.com/{img_hash}.jpg'



def download(task):
    src, folder = task
    filepath = '{folder_name}/{file_name}'.format(
        folder_name=folder,
        file_name=os.path.basename(src)
    )
    if os.path.exists(filepath):
        return True
    response = client.get_stream(src)
    if response.ok:
        with open(filepath, 'wb') as stream:
            for chunk in response.iter_content(chunk_size=1024):
                stream.write(chunk)
    else:
        print('%s can not download.' % src)
    return response.ok


class Downloader:

    def __init__(self, resource_bundles, download_folder=None):
        self.resource_bundles = resource_bundles
        self.resources_folder = download_folder or './downloads'

    def download(self):
        tasks = []
        for bundle in self.resource_bundles:
            meta, urls = bundle
            if len(urls) == 0:
                continue
            folder = self.gen_full_folder(meta)
            tasks += [(url, folder) for url in urls]
            Downloader.mkdir(folder)

        results = client.parallel_tasks(download, tasks)
        return results.get()

    def gen_full_folder(self, meta):            
        post_id, post_title = meta
        safe_title = re.sub('[\?\\/><:"|\*.]', '', post_title).strip()
        folder = '({id}) {folder_name}'.format(
            id=post_id, folder_name=safe_title
        )
        return self.resources_folder + '/' + folder

    @staticmethod
    def mkdir(path):
        if not os.path.exists(path):
            os.makedirs(path)


class ContentParser:

    def __init__(self, results, constraints):
        self.results = results
        self.constraints = constraints

    def parse(self):

        def validate(post):
            ''' crazy impl. XD '''
            if not self.constraints:
                return True

            _post = post['content']
            for key, rule in self.constraints.items():
                expression = "_post['%s']%s" % (key, rule)
                if eval(expression) is False:
                    return False
            return True

        def parse(post):
            article = post['content']
            content = article['content']
            imgur_files = ContentParser._parse_images(content)
            return ((article['id'], article['title']), imgur_files)

        if isinstance(self.results, dict):
            return [parse(self.results)] if validate(self.results) else []

        resoures = [parse(post) for post in self.results if validate(post)]
        return resoures

    @staticmethod
    def _parse_images(raw_data):
        imgurs = reg_imgur.findall(raw_data)
        imgur_files = reg_imgur_file.findall(raw_data)
        imgur_files += [pattern_imgur_file.format(img_hash=r) for r in imgurs]
        return imgur_files
