import time
from dcard import Dcard


def collect_ids(metas):
    return [meta['id'] for meta in metas]


if __name__ == '__main__':
    dcard = Dcard()

    t = time.time()
    ids = dcard.forums('funny').get_metas(pages=5, callback=collect_ids)
    print('{:.5f}'.format(time.time() - t))
    print(len(ids))

    t = time.time()
    articles = dcard.posts.get(post_id=ids[:10], comments=False)
    print('{:.5f}'.format(time.time() - t))
    print(len(articles))
