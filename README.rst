Dcard 爬蟲: dcard-spider
========================

|Build Status| |Coverage Status| |PyPI| |Land Health|

快如閃電的爬蟲，迅速獲得 Dcard 上所有看板的文章!
**Spider needs for speed.**

    *Related to my side project dcard-lumberjack <https://github.com/leVirve/dcard-lumberjack>.*


特色
-------
* 一行指令下載看板內的所有文章及圖片
* 可程式化的 API 提供更靈活的操作
* 使用非同步 (asynchronous) 及 多執行序 (multithreading) 來平行完成併發任務達到最大校效率


安裝
------------
::

    $ pip install dcard-spider

必要需求
------------
* Python 2.7+ or Python 3.4+

使用範例
--------
下載指定看板中文章內的圖片

.. image:: https://raw.githubusercontent.com/leVirve/dcard-spider/master/docs/img/snapshot.png
    :width: 600px

直接使用 command line
~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    dcard download -f photography -n 100

* 下載指令詳解
::

    dcard download -f [forums 看板名稱] -n [數量]

    (額外參數:)
            -likes      [likes 過濾門檻]
            -b          [指定起始文章 ID]
            -o          [輸出至...資料夾]
            -F          [平面化子資料夾 (各文章圖片在同一資料夾)]

透過程式 API
~~~~~~~~~~~~

.. code:: python

    from dcard import Dcard


    def 先過濾出標題含有作品關鍵字(metas):
        return [meta for meta in metas if '#作品' in meta['title']]


    if __name__ == '__main__':

        dcard = Dcard()

        metas = dcard.forums('photography').get_metas(num=100, callback=先過濾出標題含有作品關鍵字)
        posts = dcard.posts(metas).get(comments=False, links=False)

        resources = posts.parse_resources()

        status, fails = posts.download(resources)
        print('成功下載！' if len(fails) == 0 else '出了點錯下載不完全喔')


詳細方法
--------

Command-line 可用參數
~~~~~~~~~~~~~~~~~~~~~
.. code:: bash

    $ dcard -h

    usage: dcard [-h] [-f FORUM] [-n NUMBER] [-b BEFORE] [-likes LIKES_THRESHOLD]
                 [-o OUTPUT] [-F] [-v] [-V] [-c] [-l] [-p]
                 mode

    positional arguments:
    mode                        download / meta mode

    optional arguments:
    -h, --help                  show this help message and exit
    -f FORUM, --forum FORUM     Specific which forum
    -n NUMBER, --number NUMBER  Scan through how many posts
    -b BEFORE, --before BEFORE  Scan through before specified post ID
    -likes LIKES_THRESHOLD, --likes_threshold LIKES_THRESHOLD
                                Specific minimum like counts
    -o OUTPUT, --output OUTPUT  Specific folder to store the resources
    -F, --flatten               Option for flattening folders
    -v, --verbose               Logging verbose information
    -V, --version               show program's version number and exit
    -c, --comment               Option for scrape comments
    -l, --link                  Option for scrape links
    -p, --popular               Sort post by popularity

Basic
~~~~~

-  取得看板資訊 (metadata)

   -  可用參數\ ``no_school``\ 調整是否取得學校看版內容。

.. code:: python

    forums = dcard.forums.get()
    forums = dcard.forums.get(no_school=True)

-  取得看板文章資訊 (metadata)

   -  可用 ``num`` 指定文章數量
   -  文章排序有兩種選擇: ``new`` / ``popular``

.. code:: python

    ariticle_metas = dcard.forums('funny').get_metas(num=150, sort='new')
    ariticle_metas = dcard.forums('funny').get_metas(num=100, sort='popular')

    # get all the metas from forum
    ariticle_metas = dcard.forums('funny').get_metas(num=Forum.infinite_page, sort='popular')

-  提供一次取得多篇文章詳細資訊(全文、引用連結、所有留言)

.. code:: python

    # 可放入 文章編號/單一meta資訊 => return 單篇文章 in list

    article = dcard.posts(224341009).get()
    article = dcard.posts(ariticle_metas[0]).get()

    # 放入 複數文章編號/多個meta資訊 => return 多篇文章 in list

    ids = [meta['id'] for meta in ariticle_metas]
    articles = dcard.posts(ids).get()
    articles = dcard.posts(ariticle_metas).get()

-  操作文章結果 `PostsResult` 物件

.. code:: python

   # 存取 articles 中的內容
   # 1. articles.results -> get a `generator()`

   for article in articles.results:
       # `article` is a Python dict() object

   # 2. articles.result() -> get a `list()`
   for article in articles.result():
       # `article` is a Python dict() object

   # 3. Dumps all articles data into file directly
   import json

   with open('output.json', 'w', encoding='utf-8') as f:
       json.dump(articles.result(), f, ensure_ascii=False)

-  下載文章中的資源 (目前支援文中 imgur 連結的圖片)

   -  預設每篇圖片儲存至 ``(#文章編號) 文章標題`` 為名的新資料夾
   -  ``.download()`` 會回傳每個資源下載成功與否
   -  ``fails`` 是一串下載失敗的 URL

.. code:: python

    resources = articles.parse_resources()
    status, fails = articles.download(resources)


Advanced
~~~~~~~~

-  提供自定義 callback function，可在接收回傳值前做處理 (filter / reduce
   data)。

.. code:: python


    # In `dcard.forums().get_metas()`

    def collect_ids(metas):
        return [meta['id'] for meta in metas]


    def likes_count_greater(metas):
        return [meta['id'] for meta in metas if meta['likeCount'] >= 20]


    def 標題含有圖片關鍵字(metas):
        return [meta['id'] for meta in metas if '#圖' in meta['title']]


    ids = dcard.forums('funny').get_metas(num=50, callback=collect_ids)
    ids = dcard.forums('funny').get_metas(num=50, callback=標題含有圖片關鍵字)



    # In `dcard.posts().get()`, take `MongoDB` as backend database for example

    def store_to_db(posts):
        result = db[forum_name].insert_many([p for p in posts])
        print('#Forum {}: insert {} items'.format(forum_name, len(result.inserted_ids)))

    none_return_value = dcard.posts(metas).get(callback=store_to_db)


-  爬取文章時提供 content, links, comments
   三個參數，能選擇略過不需要的資訊以加快爬蟲速度。

.. code:: python

    posts = dcard.posts(ids).get(comments=False, links=False)

-  class ``Posts`` 下的 ``downloader`` 提供 hacking 選項

   - ``subfolder_pattern`` 可自定義子資料夾命名規則
   - ``flatten`` 選項可選擇將所有資源(圖片)放在一層資料夾下，而不要按照文章分子資料夾

.. code:: python

    articles.downloader.subfolder_pattern = '[{likeCount}推] {id}-{folder_name}'
    articles.downloader.flatten = True


What's next
-----------
This will be a library project for dcard continously crawling spider. And also provides end-user friendly features.


Licence
-------

**MIT**


Inspirations
------------
`SLMT's <https://github.com/SLMT>`_
`dcard-crawler <https://github.com/SLMT/dcard-crawler>`_

`Aragorn's <https://github.com/Elessar116>`_ downloader funtional request


.. |PyPI| image:: https://img.shields.io/pypi/v/dcard-spider.svg?style=flat-square
    :target: https://pypi.python.org/pypi/dcard-spider
.. |Build Status| image:: https://img.shields.io/travis/leVirve/dcard-spider/master.svg?style=flat-square
   :target: https://travis-ci.org/leVirve/dcard-spider
.. |Coverage Status| image:: https://img.shields.io/coveralls/leVirve/dcard-spider/master.svg?style=flat-square
   :target: https://coveralls.io/github/leVirve/dcard-spider
.. |Land Health| image:: https://landscape.io/github/leVirve/dcard-spider/master/landscape.svg?style=flat-square
   :target: https://landscape.io/github/leVirve/dcard-spider/master
   :alt: Code Health
