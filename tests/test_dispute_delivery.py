"""Tests for the real-not-simulated dispute delivery path.

Pinned behavior:
- Sends via Postmark with the configured per-payer submission email
- Attaches the evidence packet PDF
- Refuses to file for unknown payers (no guessing submission addresses)
- Returns a structured result with message_id from Postmark
- Metadata propagates so the inbound webhook can correlate replies
- Stub mode (no API token) doesn't make HTTP calls

We mock the Postmark HTTP layer rather than the wrapper itself so we
exercise the wrapper's payload construction (attachment encoding, etc.).
"""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from XR7.recovery.dispute_delivery import deliver_dispute
from XR7.services.postmark_client import reset_default_client


@pytest.fixture(autouse=True)
def _reset_client():
    reset_default_client()
    yield
    reset_default_client()


def _common_inputs(payer_id="BMI"):
    return {
        "claim": {"id": "claim-test-1", "payer_name": payer_id},
        "artist": {"id": "artist-test-1", "name": "Test Artist"},
        "anomaly": {
            "subtype": "HIGH_RETROACTIVE_PAYMENT_RATIO",
            "description": "74% of MLC royalties are retroactive catch-ups...",
            "estimated_recoverable": 24.22,
            "confidence_score": 0.84,
        },
        "pdf_bytes": b"%PDF-fake-pdf-content",
        "payer_id": payer_id,
    }


def test_unknown_payer_refuses_to_file(monkeypatch):
    """Auto-filing to a guessed email damages our deliverability reputation. Refuse."""
    monkeypatch.setenv("POSTMARK_API_TOKEN", "test-token")
    result = deliver_dispute(**_common_inputs(payer_id="NotAPayerWeKnow"))
    assert result["success"] is False
    assert result["submission_address"] is None
    assert "Unknown payer" in result["error_message"]


def test_stub_mode_does_not_call_postmark(monkeypatch):
    monkeypatch.delenv("POSTMARK_API_TOKEN", raising=False)
    with patch("XR7.services.postmark_client.httpx.post") as mock_post:
        result = deliver_dispute(**_common_inputs(payer_id="BMI"))
    assert result["stubbed"] is True
    assert result["success"] is True
    mock_post.assert_not_called()


class TestRealSend:
    @staticmethod
    def _ok_response() -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={"ErrorCode": 0, "Message": "OK", "MessageID": "msg-real-123"},
        )

    def test_bmi_dispute_uses_configured_submission_email(self, monkeypatch):
        monkeypatch.setenv("POSTMARK_API_TOKEN", "test-token")
        with patch(
            "XR7.services.postmark_client.httpx.post", return_value=self._ok_response()
        ) as mock_post:
            result = deliver_dispute(**_common_inputs(payer_id="BMI"))

        assert result["success"] is True
        assert result["message_id"] == "msg-real-123"
        assert result["payer_id"] == "BMI"
        # Confirms the submission address came from PAYER_CONFIGS, not the artist or claim dict
        assert "@bmi.com" in result["submission_address"]

        sent_payload = mock_post.call_args.kwargs["json"]
        assert sent_payload["To"] == result["submission_address"]
        assert "BMI" in sent_payload["Subject"] or "Royalty audit" in sent_payload["Subject"]

    def test_pdf_attached_with_correct_content_type_and_name(self, monkeypatch):
        monkeypatch.setenv("POSTMARK_API_TOKEN", "test-token")
        with patch(
            "XR7.services.postmark_client.httpx.post", return_value=self._ok_response()
        ) as mock_post:
            deliver_dispute(**_common_inputs(payer_id="BMI"))

        sent_payload = mock_post.call_args.kwargs["json"]
        attachments = sent_payload.get("Attachments")
        assert attachments and len(attachments) == 1
        att = attachments[0]
        assert att["ContentType"] == "application/pdf"
        assert att["Name"].endswith(".pdf")
        assert "claim-test-1" in att["Name"]
        # Content is base64-encoded; decode and verify roundtrip
        import base64

        assert base64.b64decode(att["Content"]) == b"%PDF-fake-pdf-content"

    def test_metadata_includes_claim_artist_payer_for_reply_correlation(self, monkeypatch):
        """Postmark inbound webhook reads these to match BMI's reply to the right Claim row."""
        monkeypatch.setenv("POSTMARK_API_TOKEN", "test-token")
        with patch(
            "XR7.services.postmark_client.httpx.post", return_value=self._ok_response()
        ) as mock_post:
            deliver_dispute(**_common_inputs(payer_id="BMI"))

        sent_payload = mock_post.call_args.kwargs["json"]
        meta = sent_payload.get("Metadata") or {}
        assert meta["claim_id"] == "claim-test-1"
        assert meta["artist_id"] == "artist-test-1"
        assert meta["payer_id"] == "BMI"

    def test_failure_returns_structured_error_does_not_raise(self, monkeypatch):
        monkeypatch.setenv("POSTMARK_API_TOKEN", "test-token")
        bad = httpx.Response(
            status_code=200,
            json={"ErrorCode": 406, "Message": "Recipient suppressed"},
        )
        with patch("XR7.services.postmark_client.httpx.post", return_value=bad):
            result = deliver_dispute(**_common_inputs(payer_id="BMI"))
        assert result["success"] is False
        assert result["error_code"] == 406
        assert "suppressed" in (result["error_message"] or "").lower()


def test_payer_id_is_substring_match(monkeypatch):
    """`payer_id` can come from `Payment.source` like 'MLC / Spotify / regular'."""
    monkeypatch.setenv("POSTMARK_API_TOKEN", "test-token")
    inputs = _common_inputs(payer_id="MLC / Spotify / reprocessing")
    with patch(
        "XR7.services.postmark_client.httpx.post",
        return_value=httpx.Response(
            status_code=200, json={"ErrorCode": 0, "MessageID": "x", "Message": "OK"}
        ),
    ):
        result = deliver_dispute(**inputs)
    assert result["success"] is True
    assert result["payer_id"] == "MLC"
    assert "themlc.com" in result["submission_address"]
