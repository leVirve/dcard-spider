import time
from multiprocessing import Pool

from pymongo import MongoClient

from dcard import Dcard, logger


client = MongoClient()
db = client['dcard-metas']
collct = None


def store_metas(metas, forum):

    bulk = db['forum'].initialize_ordered_bulk_op()
    [bulk.find({'id': meta['id']}).upsert().update({"$set": meta}) for meta in metas]
    result = bulk.execute()

    result['upserted'] = len(result['upserted'])
    logger.info('[database] #Forum {}: {}'.format(forum, result))


def collect_metas(name):
    bound = 999  # let it be infinity later!
    s = time.time()
    Dcard.forums(name).get_metas(
            num=bound,
            callback=lambda metas, forum=name: store_metas(metas, forum)
        )
    logger.info('Spent {:.05} sec for [{}]'.format(time.time() - s, name))


def main():
    dcard = Dcard()
    forums = dcard.forums.get(no_school=True)

    thread_pool = Pool(processes=8)
    result = thread_pool.map_async(collect_metas, [forum['alias'] for forum in forums])
    result.get()


if __name__ == '__main__':
    s = time.time()
    main()
    logger.info('Total Work: {:.05} sec'.format(time.time() - s))
