from dcard import add_handles_on_logger
from dcard.utils import FutureRequest


class TestClient:

    def test_get_and_server_responsed_error(self, client):
        resp = client._get('https://test-for-error')
        assert resp == {}

    def test_get_and_value_error_with_man_retry(self, client):
        resp = client._get('https://test-for-error', error='ValueError')
        assert resp == {}

    def test_get_and_httplib_incomplete_read(self, client):
        resp = client._get('https://test-for-error', error='IncompleteRead')
        assert resp == {}

    def test_get_and_keep_retry_error(self, client):
        resp = client._get('https://test-for-error', error='RetryError')
        assert resp is None

    def test_get_stream(self, client):
        resp = client.get_stream('https://test-for-get-stream')
        assert resp.ok


class TestFutureRequest:

    def test_future_request_object(self, client):
        req = FutureRequest(
                client, client.fut_session.get('https://test-for-object'))
        assert req.future
        assert req.caller
        assert req.manual_retry == 0

    def test_future_request_json_decode_error(self, client):
        req = FutureRequest(
                client,
                client.fut_session.get(
                    'https://test-for-future-request',
                    resp_error='ValueError')
              )
        assert not req.json()

    def test_future_request_exceptions(self, client):
        req = FutureRequest(
                client,
                client.fut_session.get(
                    'https://test-for-future-request',
                    resp_error=True)
              )
        assert not req.json()


class TestDcard:

    def test_dcard_logger_handlers(self):
        add_handles_on_logger()
