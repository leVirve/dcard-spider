from dcard.manager import Downloader


class TestDownloader:

    def test_dwonload_with_bundles_but_no_urls(self):
        downloader = Downloader()
        metas = dict(test='some data')
        urls = []
        bundles = [(metas, urls)]

        downloader.resource_bundles = bundles
        cnt, _ = downloader.download()

        assert cnt == 0
