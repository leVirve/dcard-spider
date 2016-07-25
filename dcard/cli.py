# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import time
import argparse

from dcard.dcard import Dcard

parser = argparse.ArgumentParser()
parser.add_argument(
    "mode", help="download / meta mode")
parser.add_argument(
    "-f", "--forum", help="Specific which forum")
parser.add_argument(
    "-p", "--pages", type=int, help="Crawl how many pages")
parser.add_argument(
    "-likes", "--likes_threshold", type=int, help="Specific minimum like counts")


def main():
    args = parser.parse_args()
    if args.mode == 'download':
        if not (args.forum or args.pages):
            parser.error('No action requested, add --forum or --pages')
        download(args)


def download(args):

    global likes_thesh
    likes_thesh = 0

    def collect_ids(metas):
        return [meta['id'] for meta in metas if meta['likeCount'] >= likes_thesh]

    if args.likes_threshold:
        likes_thesh = args.likes_threshold

    dcard = Dcard()

    start_time = time.time()

    ids = dcard \
        .forums(args.forum) \
        .get_metas(pages=args.pages, callback=collect_ids)
    posts = dcard.posts(ids).get(comments=False, links=False)
    resources = posts.parse_resources()
    status = posts.download(resources)

    print('成功下載 %d items！' % len(resources) if all(status)  \
            else '出了點錯下載不完全喔')
    print('Finish in {0:.5f} sec(s).'.format(time.time() - start_time))

    return all(status)
