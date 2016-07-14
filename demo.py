from dcard import Dcard


if __name__ == '__main__':
    dcard = Dcard()

    forums = dcard.forums.get(no_school=True)
    print(len(forums))

    ariticle_metas = dcard.forums('funny').get_metas(pages=1, sort='new')
    print(len(ariticle_metas))

    article = dcard.posts(224341009).get()
    print(article)
