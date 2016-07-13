from dcard import Dcard
# from pymongo import MongoClient


# client = MongoClient()
# db = client.dcard


if __name__ == '__main__':
    dcard = Dcard()

    forums = dcard.forums.get(no_school=True)
    print(len(forums))

    ariticle_metas = dcard.forums('funny').get_metas(pages=2, sort='new')
    print(len(ariticle_metas))

    article = dcard.posts(id=4535, metas[0])

    # result = db.forums.count()
    # print(result)
