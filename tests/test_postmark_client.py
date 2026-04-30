"""Tests for the Postmark client wrapper.

Pinned behavior:
- Stub mode (no token): logs and returns delivered=True, stubbed=True. No HTTP call.
- Real mode: posts to Postmark, parses ErrorCode + MessageID correctly.
- HTTP failure: returns delivered=False with error info; doesn't raise.
- Postmark-200-but-ErrorCode-nonzero: still treated as failure (e.g., suppressed recipient).

We don't ship a real-network test — that would need a live API token and is the
kind of thing the manual-recovery runbook covers as a one-time validation.
"""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from XR7.services.postmark_client import (
    PostmarkClient,
    PostmarkSendResult,
    reset_default_client,
)


@pytest.fixture(autouse=True)
def _reset_client():
    """Don't let the module-level singleton leak settings across tests."""
    reset_default_client()
    yield
    reset_default_client()


class TestStubMode:
    def test_unconfigured_client_returns_stubbed_success(self):
        client = PostmarkClient(api_token=None)
        assert client.configured is False
        result = client.send_email(
            to="user@example.com",
            subject="hello",
            text_body="hi",
        )
        assert result == PostmarkSendResult(delivered=True, message_id=None, stubbed=True)

    def test_stub_mode_does_not_make_http_calls(self):
        """The whole point of stub mode is no network IO. Catch any regression."""
        client = PostmarkClient(api_token=None)
        with patch("XR7.services.postmark_client.httpx.post") as mock_post:
            client.send_email(to="user@example.com", subject="x", text_body="y")
            mock_post.assert_not_called()


class TestRealSend:
    def _ok_response(self, message_id: str = "abc-123") -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={"ErrorCode": 0, "Message": "OK", "MessageID": message_id},
        )

    def test_successful_send_returns_message_id(self):
        client = PostmarkClient(api_token="test-token", default_from="from@example.com")
        with patch(
            "XR7.services.postmark_client.httpx.post", return_value=self._ok_response("xyz-789")
        ) as mock_post:
            result = client.send_email(
                to="recipient@example.com",
                subject="Test subject",
                text_body="Body",
            )
            assert result.delivered is True
            assert result.message_id == "xyz-789"
            assert result.stubbed is False
            assert result.error_code is None

            # Verify the HTTP call shape: bearer header + correct payload
            call = mock_post.call_args
            assert call.kwargs["headers"]["X-Postmark-Server-Token"] == "test-token"
            payload = call.kwargs["json"]
            assert payload["To"] == "recipient@example.com"
            assert payload["From"] == "from@example.com"
            assert payload["Subject"] == "Test subject"
            assert payload["TextBody"] == "Body"
            assert payload["MessageStream"] == "outbound"

    def test_metadata_propagates_to_postmark(self):
        """Metadata is how we correlate inbound replies back to a Claim."""
        client = PostmarkClient(api_token="test-token")
        with patch(
            "XR7.services.postmark_client.httpx.post", return_value=self._ok_response()
        ) as mock_post:
            client.send_email(
                to="bmi@example.com",
                subject="Dispute",
                text_body="...",
                metadata={"claim_id": "claim-42", "artist_id": "artist-7"},
                tag="dispute-bmi",
            )
            payload = mock_post.call_args.kwargs["json"]
            assert payload["Metadata"] == {"claim_id": "claim-42", "artist_id": "artist-7"}
            assert payload["Tag"] == "dispute-bmi"

    def test_html_body_and_reply_to_optional(self):
        client = PostmarkClient(api_token="test-token")
        with patch(
            "XR7.services.postmark_client.httpx.post", return_value=self._ok_response()
        ) as mock_post:
            client.send_email(
                to="x@example.com",
                subject="x",
                text_body="t",
                html_body="<p>t</p>",
                reply_to="reply@example.com",
            )
            payload = mock_post.call_args.kwargs["json"]
            assert payload["HtmlBody"] == "<p>t</p>"
            assert payload["ReplyTo"] == "reply@example.com"


class TestErrorPaths:
    def test_postmark_200_with_nonzero_error_code_is_failure(self):
        """Postmark uses HTTP 200 + ErrorCode != 0 for some failures (e.g., suppressed recipient)."""
        client = PostmarkClient(api_token="test-token")
        bad_response = httpx.Response(
            status_code=200,
            json={"ErrorCode": 406, "Message": "Recipient suppressed"},
        )
        with patch("XR7.services.postmark_client.httpx.post", return_value=bad_response):
            result = client.send_email(to="x@example.com", subject="x", text_body="y")
            assert result.delivered is False
            assert result.error_code == 406
            assert "suppressed" in (result.error_message or "").lower()

    def test_http_4xx_returns_error_result_does_not_raise(self):
        client = PostmarkClient(api_token="test-token")
        bad_response = httpx.Response(
            status_code=401, json={"ErrorCode": 10, "Message": "Invalid token"}
        )
        with patch("XR7.services.postmark_client.httpx.post", return_value=bad_response):
            result = client.send_email(to="x@example.com", subject="x", text_body="y")
            assert result.delivered is False
            assert result.error_code == 10

    def test_transport_error_returns_error_result_does_not_raise(self):
        """A network error must not bubble out — caller relies on result.delivered."""
        client = PostmarkClient(api_token="test-token")
        with patch(
            "XR7.services.postmark_client.httpx.post",
            side_effect=httpx.ConnectError("network down"),
        ):
            result = client.send_email(to="x@example.com", subject="x", text_body="y")
            assert result.delivered is False
            assert result.error_code == -1
            assert "transport" in (result.error_message or "").lower()
