import time

from pymongo import MongoClient

from dcard import Dcard, logger


client = MongoClient()
db = client['dcard']
collct = None


def should_it_update(metas, forum):
    results = []
    for meta in metas:
        found = db[forum].find_one({'id': meta['id']})
        if not found:# or found['updatedAt'] < meta['updatedAt']:
            results.append(meta['id'])
    return results


def store_to_db(posts, forum):
    result = db[forum].insert_many([p for p in posts])
    logger.info('[database] #Forum {}: insert {} items'.format(forum, len(result.inserted_ids)))


def main():
    dcard = Dcard()
    forums = dcard.forums.get(no_school=True)

    for forum in forums:
        name = forum['alias']

        bound = 30  # let it be infinity later!
        metas = dcard.forums(name).get_metas(
                    num=bound, callback=lambda metas, forum=name: \
                        should_it_update(metas, forum)
                )
        if metas:
            dcard.posts(metas).get(
                callback=lambda posts, forum=name: store_to_db(posts, forum))

        # db[name].drop()

if __name__ == '__main__':
    s = time.time()
    main()
    print('{:.05} sec'.format(time.time() - s))
