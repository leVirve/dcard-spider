import re
import os
import requests
from multiprocessing.dummy import Pool
try:
    from dcard.forums import Forum
    from dcard.posts import Post
except ImportError:
    from .forums import Forum
    from .posts import Post


__all__ = ['Dcard']


reg_images    = re.compile('http[s]?://\S+\.(?:jpg|png|gif)')
reg_imgur     = re.compile('http[s]?://imgur.com/(\w+)')
reg_imgur_file = re.compile('http[s]?://i.imgur.com/\w+\.(?:jpg|png|gif)')


def download(task):
    src, folder = task
    file_name = os.path.basename(src)

    response = requests.get(src, stream=True)
    if response.ok:
        with open('%s/%s' % (folder, file_name), 'wb') as stream:
            for chunk in response.iter_content(chunk_size=1024):
                stream.write(chunk)
        print('File: %s is downloaded.' % file_name)


threadPool = Pool(processes=8)


class Dcard:

    forums = Forum
    posts = Post

    @staticmethod
    def download(bundles):
        tasks = []

        for bundle in bundles:
            post_id, folder, urls = bundle
            full_folder = 'downloads/%s (#%d)' % (folder, post_id)
            os.makedirs(full_folder, exist_ok=True)
            tasks += [(url, full_folder) for url in urls]

        results = threadPool.map_async(download, tasks)
        results.get()

    @staticmethod
    def parse_resources(articles, constraints=None):
        resoures = []
        for a in articles:
            res = Dcard._parse_resources(a, constraints=constraints)
            if res:
                resoures.append(res)
        return resoures

    @staticmethod
    def _parse_resources(article, constraints):
        article_content = article['content']

        ''' crazy impl. XD '''
        for key, rule in constraints.items():
            expression = "article_content['%s']%s" % (key, rule)
            if eval(expression) is False:
                return

        content = article_content['content']
        imgur_files = Dcard.find_images(content)
        return (article_content['id'], article_content['title'], imgur_files)

    @staticmethod
    def find_images(raw_data):
        imgurs = reg_imgur.findall(raw_data)
        imgur_files = reg_imgur_file.findall(raw_data)
        imgur_files += ['http://i.imgur.com/%s.jpg' % r for r in imgurs]
        return imgur_files
