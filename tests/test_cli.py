import os

import pytest

from dcard.cli import parser, main, download


class TestCli:

    def test_verbose_log(self):
        argv = 'TEST -v'.split()
        args = parser.parse_args(argv)

        main(args)
        assert os.path.exists('dcard.log')

    def test_download_but_no_params(self):
        argv = 'download'.split()
        args = parser.parse_args(argv)

        with pytest.raises(SystemExit):
            main(args)

    def test_download_from_main(self):
        argv = 'download -f funny -n 15'.split()
        args = parser.parse_args(argv)

        main(args)

    def test_download_basic(self):
        argv = 'download -f funny -n 15'.split()
        args = parser.parse_args(argv)
        assert args.forum == 'funny'
        assert args.number == 15

    def test_download_params_likes(self):
        argv = 'download -f funny -n 15 -likes 50'.split()
        args = parser.parse_args(argv)
        assert args.likes_threshold
        assert args.likes_threshold == 50

    def test_download_params_folder(self):
        argv = 'download -f funny -n 15 -o ./downloads/test -F'.split()
        args = parser.parse_args(argv)
        assert args.flatten
        assert download(args)
