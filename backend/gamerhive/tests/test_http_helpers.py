from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from requests.exceptions import ConnectionError, HTTPError

from gamerhive.http_helpers import igdb_request_with_retry


def _http_error(status_code, headers=None):
    response = MagicMock()
    response.status_code = status_code
    response.headers = headers or {}
    return HTTPError(response=response)


class IgdbRequestWithRetryTests(SimpleTestCase):
    def setUp(self):
        patcher = patch("gamerhive.http_helpers._ensure_request_timeout")
        patcher.start()
        self.addCleanup(patcher.stop)

    def _logger(self):
        return MagicMock()

    @patch("gamerhive.http_helpers.sleep")
    def test_transient_failure_is_retried_then_succeeds(self, mock_sleep):
        request_func = MagicMock(side_effect=[ConnectionError("boom"), b"ok"])
        result = igdb_request_with_retry(
            request_func, "games", "query", logger=self._logger(), retries=3
        )
        self.assertEqual(result, b"ok")
        self.assertEqual(request_func.call_count, 2)
        mock_sleep.assert_called_once()

    @patch("gamerhive.http_helpers.sleep")
    def test_backoff_delay_doubles_and_is_capped(self, mock_sleep):
        request_func = MagicMock(
            side_effect=[
                ConnectionError("a"),
                ConnectionError("b"),
                ConnectionError("c"),
                b"ok",
            ]
        )
        igdb_request_with_retry(
            request_func,
            "games",
            "query",
            logger=self._logger(),
            retries=4,
            max_backoff=3,
        )
        # delay sequence: 1, 2, then capped at 3
        self.assertEqual(
            [call.args[0] for call in mock_sleep.call_args_list], [1, 2, 3]
        )

    @patch("gamerhive.http_helpers.sleep")
    def test_retry_limit_is_respected_and_raises(self, mock_sleep):
        request_func = MagicMock(side_effect=ConnectionError("always fails"))
        with self.assertRaises(ConnectionError):
            igdb_request_with_retry(
                request_func, "games", "query", logger=self._logger(), retries=3
            )
        self.assertEqual(request_func.call_count, 3)

    @patch("gamerhive.http_helpers.sleep")
    def test_rate_limit_is_retried_respecting_retry_after(self, mock_sleep):
        request_func = MagicMock(
            side_effect=[_http_error(429, {"Retry-After": "5"}), b"ok"]
        )
        igdb_request_with_retry(
            request_func, "games", "query", logger=self._logger(), retries=3
        )
        mock_sleep.assert_called_once_with(5)

    @patch("gamerhive.http_helpers.sleep")
    def test_server_error_is_retryable(self, mock_sleep):
        request_func = MagicMock(side_effect=[_http_error(503), b"ok"])
        result = igdb_request_with_retry(
            request_func, "games", "query", logger=self._logger(), retries=3
        )
        self.assertEqual(result, b"ok")
        self.assertEqual(request_func.call_count, 2)

    @patch("gamerhive.http_helpers.sleep")
    def test_client_error_is_not_retried(self, mock_sleep):
        request_func = MagicMock(side_effect=_http_error(400))
        with self.assertRaises(HTTPError):
            igdb_request_with_retry(
                request_func, "games", "query", logger=self._logger(), retries=5
            )
        self.assertEqual(request_func.call_count, 1)
        mock_sleep.assert_not_called()

    @patch("gamerhive.http_helpers.sleep")
    def test_unauthorized_is_not_retried(self, mock_sleep):
        request_func = MagicMock(side_effect=_http_error(401))
        with self.assertRaises(HTTPError):
            igdb_request_with_retry(
                request_func, "games", "query", logger=self._logger(), retries=5
            )
        self.assertEqual(request_func.call_count, 1)
        mock_sleep.assert_not_called()


class EnsureRequestTimeoutTests(SimpleTestCase):
    def test_timeout_patch_applied_to_igdb_wrapper(self):
        import igdb.wrapper as igdb_wrapper

        from gamerhive.http_helpers import _ensure_request_timeout

        original_post = igdb_wrapper.post
        try:
            igdb_wrapper.post = original_post
            _ensure_request_timeout()
            self.assertTrue(
                getattr(igdb_wrapper.post, "_gamerhive_timeout_patched", False)
            )
            self.assertEqual(igdb_wrapper.post.keywords.get("timeout"), (5, 30))
        finally:
            igdb_wrapper.post = original_post
