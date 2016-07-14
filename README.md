# dcard-spider
[![Build Status](https://travis-ci.org/leVirve/dcard-spider.svg?branch=master)](https://travis-ci.org/leVirve/dcard-spider)
[![Coverage Status](https://coveralls.io/repos/github/leVirve/dcard-spider/badge.svg?branch=master)](https://coveralls.io/github/leVirve/dcard-spider?branch=master)

# Usage
## Basic

```python
# demo.py

from dcard import Dcard


if __name__ == '__main__':
    dcard = Dcard()

    ''' 取得看板資訊 (metadata)，可用參數`no_school`調整是否取得學校看版內容 '''
    forums = dcard.forums.get()
    forums = dcard.forums.get(no_school=True)

    print(len(forums))

    ''' 取得看板文章資訊 (metadata)，一頁有30篇文章，可用`pages`指定頁數數量
        文章排序有兩種選擇: 'new' / 'popular'
    '''
    ariticle_metas = dcard.forums('funny').get_metas(pages=5, sort='new')
    ariticle_metas = dcard.forums('funny').get_metas(pages=1, sort='popular')

    print(len(ariticle_metas))

    ''' 取得文章詳細資訊 (全文、引用連結、所有留言)
        提供一次取得 單篇/多篇文章
    '''
    # 放入 文章編號/單一meta資訊 => return 單篇文章
    article = dcard.posts(224341009).get()
    article = dcard.posts(ariticle_metas[0]).get()

    # 放入 複數文章編號/多個meta資訊 => return 一串文章
    ids = [meta['id'] for meta in ariticle_metas]
    articles = dcard.posts(ids).get()
    articles = dcard.posts(ariticle_metas).get()

```

## Advanced

```python
from dcard import Dcard


def collect_ids(metas):
    return [meta['id'] for meta in metas]


if __name__ == '__main__':
    dcard = Dcard()

    ''' 提供自定義 callback function 做在接收回傳值前做處理 '''
    ids = dcard.forums('funny').get_metas(pages=5, callback=collect_ids)
    print(len(ids))

    ''' 文章提供 content, links, comments 三個參數
        可選擇略過部分不需要的資訊，加快爬蟲速度
    '''
    articles = dcard.posts(ids).get(comments=False, links=False)
    print(len(articles))

```
