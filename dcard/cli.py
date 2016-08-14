# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import time
import argparse

import dcard
from dcard.dcard import Dcard

parser = argparse.ArgumentParser()
parser.add_argument(
    'mode', help='download / meta mode')
parser.add_argument(
    '-f', '--forum', help='Specific which forum')
parser.add_argument(
    '-n', '--number', type=int, help='Scan through how many posts')
parser.add_argument(
    '-b', '--before', type=int, help='Scan through before specified post ID')
parser.add_argument(
    '-likes', '--likes_threshold', type=int, help='Specific minimum like counts')
parser.add_argument(
    '-o', '--output', type=str, help='Specific folder to store the resources')
parser.add_argument(
    '-F', '--flatten', action='store_true', help='Option for flattening folders')
parser.add_argument(
    '-v', '--verbose', action='store_true', help='Logging verbose information')
parser.add_argument(
    '-V', '--version', action='version', version=dcard.__version__)


def main(args=None):
    args = args or parser.parse_args()
    if args.verbose:
        dcard.add_handles_on_logger()
    if args.mode == 'download':
        if not (args.forum or args.number):
            parser.error('No action requested, add --forum or --number')
        download(args)


def download(args):

    def metas_filter(metas):
        return [meta for meta in metas if meta['likeCount'] >= likes_thesh]

    likes_thesh = args.likes_threshold if args.likes_threshold else 0

    dcard = Dcard()

    start_time = time.time()

    metas = dcard \
        .forums(args.forum) \
        .get_metas(num=args.number, before=args.before, callback=metas_filter)
    posts = dcard.posts(metas).get(comments=False, links=False)

    if args.flatten:
        posts.downloader.subfolder_pattern = '[{likeCount}推] {id}-{folder_name}'
        posts.downloader.flatten = True
    if args.output:
        posts.downloader.resources_folder = args.output

    resources = posts.parse_resources()
    cnt, fails = posts.download(resources)

    print('成功下載 %d items！' % cnt
          if not fails else '出了點錯下載不完全喔')
    print('Finish in {0:.5f} sec(s).'.format(time.time() - start_time))

    return cnt, fails
