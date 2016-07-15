import time
from dcard import Dcard


def collect_ids(metas):
    return [meta['id'] for meta in metas]


def 標題含有圖片關鍵字(metas):
    return [meta['id'] for meta in metas if '#圖' in meta['title']]


if __name__ == '__main__':
    dcard = Dcard()


    ids = dcard.forums('funny').get_metas(pages=5, callback=collect_ids)

    t = time.time()
    articles = dcard.posts(ids).get(comments=False, links=False)
    print('{:.5f}'.format(time.time() - t))


    ids = dcard.forums('funny').get_metas(pages=5, callback=標題含有圖片關鍵字)
    posts = dcard.posts(ids).get(comments=False, links=False)

    resources = dcard.parse_resources(posts, constraints={'likeCount': '>=20', 'commentCount': '>10'})
    status = dcard.download(resources)
    print(status)
