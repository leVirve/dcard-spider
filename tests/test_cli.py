import argparse
from dcard.cli import parser, download


def test_download_cli():
    argv = 'download -f funny -n 15 -likes 1 -o ./downloads/fk'.split()
    args = parser.parse_args(argv)
    print(args)
    assert download(args)
