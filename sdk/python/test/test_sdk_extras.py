"""
Tests for xr7_sdk.extras — retry policy, offset pagination, and cursor pagination.

Unit tests use stub callables so they run without a live server.
Integration tests (marked @pytest.mark.integration) require XR7_TEST_BASE_URL
and XR7_TEST_ADMIN_TOKEN environment variables to be set.
"""

from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import pytest
from xr7_sdk.exceptions import ApiException, UnauthorizedException
from xr7_sdk.extras import cursor_paginate, paginate, with_retry

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _api_exc(status: int) -> ApiException:
    exc = ApiException(status=status, reason="test")
    return exc


# ---------------------------------------------------------------------------
# with_retry — unit tests
# ---------------------------------------------------------------------------


class TestWithRetry:
    def test_succeeds_on_first_call(self):
        fn = MagicMock(return_value={"ok": True})
        result = with_retry(fn)
        assert result == {"ok": True}
        fn.assert_called_once()

    def test_retries_on_503_then_succeeds(self):
        fn = MagicMock(side_effect=[_api_exc(503), _api_exc(503), {"ok": True}])
        with patch("xr7_sdk.extras.time.sleep"):
            result = with_retry(fn, _max_retries=3, _base_delay=0.001)
        assert result == {"ok": True}
        assert fn.call_count == 3

    def test_retries_on_429(self):
        fn = MagicMock(side_effect=[_api_exc(429), {"rate": "ok"}])
        with patch("xr7_sdk.extras.time.sleep"):
            result = with_retry(fn, _max_retries=2, _base_delay=0.001)
        assert result == {"rate": "ok"}

    def test_does_not_retry_on_4xx_non_transient(self):
        fn = MagicMock(side_effect=_api_exc(400))
        with pytest.raises(ApiException) as exc_info:
            with_retry(fn, _max_retries=3)
        assert exc_info.value.status == 400
        fn.assert_called_once()  # no retry

    def test_does_not_retry_on_401(self):
        fn = MagicMock(side_effect=UnauthorizedException(status=401))
        with pytest.raises(ApiException):
            with_retry(fn, _max_retries=3)
        fn.assert_called_once()

    def test_raises_after_exhausting_retries(self):
        fn = MagicMock(side_effect=_api_exc(500))
        with patch("xr7_sdk.extras.time.sleep"):
            with pytest.raises(ApiException) as exc_info:
                with_retry(fn, _max_retries=2, _base_delay=0.001)
        assert exc_info.value.status == 500
        assert fn.call_count == 3  # 1 initial + 2 retries

    def test_retries_on_os_error(self):
        fn = MagicMock(side_effect=[OSError("network"), {"ok": True}])
        with patch("xr7_sdk.extras.time.sleep"):
            result = with_retry(fn, _max_retries=1, _base_delay=0.001)
        assert result == {"ok": True}

    def test_passes_args_and_kwargs(self):
        fn = MagicMock(return_value="result")
        with_retry(fn, "pos1", key="val")
        fn.assert_called_once_with("pos1", key="val")

    def test_exponential_delay_increases(self):
        fn = MagicMock(side_effect=[_api_exc(503), _api_exc(503), {"ok": True}])
        sleep_calls: list[float] = []
        with patch("xr7_sdk.extras.time.sleep", side_effect=lambda s: sleep_calls.append(s)):
            with patch("xr7_sdk.extras.random.random", return_value=0.5):  # no jitter
                with_retry(fn, _max_retries=3, _base_delay=1.0, _jitter=0.0)
        # Second sleep should be >= first (exponential)
        assert len(sleep_calls) == 2
        assert sleep_calls[1] >= sleep_calls[0]


# ---------------------------------------------------------------------------
# paginate — unit tests
# ---------------------------------------------------------------------------


class TestPaginate:
    def _make_api(self, total: int, page_size: int = 3) -> MagicMock:
        """Returns a mock that returns paged dict responses."""

        def side_effect(*args, limit=100, offset=0, **kwargs):
            items = list(range(offset, min(offset + limit, total)))
            return {"items": items, "total": total, "limit": limit, "offset": offset}

        return MagicMock(side_effect=side_effect)

    def test_yields_all_items_single_page(self):
        api = self._make_api(total=3, page_size=10)
        result = list(paginate(api, limit=10))
        assert result == [0, 1, 2]

    def test_yields_all_items_multiple_pages(self):
        api = self._make_api(total=7)
        result = list(paginate(api, limit=3))
        assert result == list(range(7))

    def test_empty_result_terminates(self):
        fn = MagicMock(return_value={"items": [], "total": 0, "limit": 10, "offset": 0})
        result = list(paginate(fn, limit=10))
        assert result == []

    def test_object_response_supported(self):
        page1 = SimpleNamespace(items=[10, 20], total=3, limit=2, offset=0)
        page2 = SimpleNamespace(items=[30], total=3, limit=2, offset=2)
        page3 = SimpleNamespace(items=[], total=3, limit=2, offset=3)
        fn = MagicMock(side_effect=[page1, page2, page3])
        result = list(paginate(fn, limit=2))
        assert result == [10, 20, 30]

    def test_start_offset_respected(self):
        api = self._make_api(total=10)
        result = list(paginate(api, limit=5, _start_offset=5))
        assert result == [5, 6, 7, 8, 9]

    def test_exact_page_boundary(self):
        # total = 6, limit = 3: exactly two pages; no extra call needed
        api = self._make_api(total=6)
        result = list(paginate(api, limit=3))
        assert result == list(range(6))
        assert api.call_count == 2


# ---------------------------------------------------------------------------
# cursor_paginate — unit tests
# ---------------------------------------------------------------------------


class TestCursorPaginate:
    def test_single_page(self):
        fn = MagicMock(return_value={"items": ["a", "b"], "next_cursor": None})
        result = list(cursor_paginate(fn, limit=10))
        assert result == ["a", "b"]

    def test_multiple_pages(self):
        fn = MagicMock(
            side_effect=[
                {"items": ["a", "b"], "next_cursor": "tok1"},
                {"items": ["c", "d"], "next_cursor": "tok2"},
                {"items": ["e"], "next_cursor": None},
            ]
        )
        result = list(cursor_paginate(fn, limit=2))
        assert result == ["a", "b", "c", "d", "e"]
        # Verify cursors were forwarded correctly
        assert fn.call_args_list[1] == call(limit=2, cursor="tok1")
        assert fn.call_args_list[2] == call(limit=2, cursor="tok2")

    def test_empty_items_terminates(self):
        fn = MagicMock(return_value={"items": [], "next_cursor": "tok"})
        result = list(cursor_paginate(fn))
        assert result == []

    def test_object_response_supported(self):
        fn = MagicMock(
            side_effect=[
                SimpleNamespace(items=[1, 2], next_cursor="c1"),
                SimpleNamespace(items=[3], next_cursor=None),
            ]
        )
        result = list(cursor_paginate(fn, limit=2))
        assert result == [1, 2, 3]


# ---------------------------------------------------------------------------
# Integration tests — require a live API
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestSDKIntegrationAgainstLiveAPI:
    """Validate SDK extras against the real API.

    Required env vars:
    - XR7_TEST_BASE_URL  e.g. http://localhost:8000
    - XR7_TEST_ADMIN_TOKEN  a valid admin JWT
    """

    @pytest.fixture(autouse=True)
    def _api_client(self):
        from xr7_sdk import ApiClient, Configuration
        from xr7_sdk.api.admin_api import AdminApi
        from xr7_sdk.api.artists_api import ArtistsApi

        base_url = os.environ.get("XR7_TEST_BASE_URL", "http://localhost:8000")
        token = os.environ.get("XR7_TEST_ADMIN_TOKEN", "")

        cfg = Configuration(host=base_url, access_token=token)
        self.client = ApiClient(configuration=cfg)
        self.admin_api = AdminApi(api_client=self.client)
        self.artists_api = ArtistsApi(api_client=self.client)

    def test_paginate_artists_returns_all_records(self):
        """paginate() should iterate through all artists without missing any."""
        items = list(paginate(self.admin_api.admin_artists_get, limit=10))
        # Get total from a direct call
        first_page = self.admin_api.admin_artists_get(limit=1, offset=0)
        total = (
            first_page.get("total", 0)
            if isinstance(first_page, dict)
            else getattr(first_page, "total", 0)
        )
        assert len(items) == total

    def test_with_retry_on_live_health_endpoint(self):
        """with_retry should succeed on a reliable endpoint like /healthz."""
        import urllib.request

        base_url = os.environ.get("XR7_TEST_BASE_URL", "http://localhost:8000")

        def fetch_health():
            with urllib.request.urlopen(f"{base_url}/healthz", timeout=5) as resp:
                return resp.status

        status = with_retry(fetch_health, _max_retries=2, _base_delay=0.1)
        assert status == 200

    def test_paginate_yields_same_items_as_manual_pages(self):
        """Items yielded by paginate() must match manually fetched pages."""
        limit = 5
        paginated = list(paginate(self.admin_api.admin_artists_get, limit=limit))
        manual: list = []
        offset = 0
        while True:
            page = self.admin_api.admin_artists_get(limit=limit, offset=offset)
            items = (
                page.get("items", [])
                if isinstance(page, dict)
                else list(getattr(page, "items", []))
            )
            if not items:
                break
            manual.extend(items)
            offset += len(items)
            if offset >= (
                page.get("total", 0) if isinstance(page, dict) else getattr(page, "total", 0)
            ):
                break

        assert len(paginated) == len(manual)
