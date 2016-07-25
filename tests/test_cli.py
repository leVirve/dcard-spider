import argparse
from dcard.cli import parser, download


def test_download_cli():
    argv = 'download -f Hahahahaha -n 15 -likes 1'.split()
    args = parser.parse_args(argv)
    print(args)
    assert download(args)
