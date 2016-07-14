import time
from dcard import Dcard


def collect_ids(metas):
    return [meta['id'] for meta in metas]


if __name__ == '__main__':
    dcard = Dcard()

    t = time.perf_counter()
    r = dcard.forums('funny').get_metas(pages=20, callback=collect_ids)
    print('{:.5f}'.format(time.perf_counter() - t))
