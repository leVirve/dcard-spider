from __future__ import absolute_import

import logging
from dcard.dcard import Dcard  # noqa


__version__ = '0.2.9'


logger = logging.getLogger('dcard')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('dcard.log', encoding='utf8')
ch = logging.StreamHandler()
fh.setLevel(logging.DEBUG)
ch.setLevel(logging.WARNING)

fh_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch_formatter = logging.Formatter(
    '%(asctime)s - %(message)s')
fh.setFormatter(fh_formatter)
ch.setFormatter(ch_formatter)
logger.addHandler(fh)
logger.addHandler(ch)
