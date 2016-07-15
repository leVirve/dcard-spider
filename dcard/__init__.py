from __future__ import absolute_import

import logging
from dcard.dcard import *


logger = logging.getLogger('dcard')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler('dcard.log', encoding='utf8')
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
simple_formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(simple_formatter)
logger.addHandler(fh)
logger.addHandler(ch)
