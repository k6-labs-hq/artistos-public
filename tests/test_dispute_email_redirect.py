"""XR7_DISPUTE_REDIRECT_EMAIL routes outbound disputes to a test address.

Used while the packet/email body is under attorney review — fly the
full Postmark pipeline to ourselves before flying real disputes.
"""

from __future__ import annotations

import pytest

from XR7.recovery.dispute_delivery import deliver_dispute


@pytest.fixture(autouse=True)
def _no_postmark_token(monkeypatch):
    """Force stub mode so tests don't try to actually call Postmark."""
    monkeypatch.delenv("POSTMARK_API_TOKEN", raising=False)


def test_redirect_overrides_submission_address(monkeypatch):
    monkeypatch.setenv("XR7_DISPUTE_REDIRECT_EMAIL", "ops-review@k6-labs.com")
    result = deliver_dispute(
        claim={"id": "clm_test", "payer_name": "BMI"},
        artist={"id": "art_test", "name": "Test Writer"},
        anomaly={
            "subtype": "HIGH_RETROACTIVE_PAYMENT_RATIO",
            "description": "Test finding",
            "estimated_recoverable": 1000.0,
            "confidence_score": 0.85,
        },
        pdf_bytes=b"%PDF-1.4 stub",
        payer_id="BMI",
        office={
            "name": "Nashville",
            "submission_email": "nashville@bmi.com",
            "mailing_address": "10 Music Square East",
            "phone": "1-844-BMI-4255",
        },
    )
    assert result["redirected"] is True
    assert result["submission_address"] == "ops-review@k6-labs.com"
    assert result["intended_recipient"] == "nashville@bmi.com"


def test_no_redirect_when_env_unset(monkeypatch):
    monkeypatch.delenv("XR7_DISPUTE_REDIRECT_EMAIL", raising=False)
    result = deliver_dispute(
        claim={"id": "clm_test", "payer_name": "BMI"},
        artist={"id": "art_test", "name": "Test Writer"},
        anomaly={
            "subtype": "HIGH_RETROACTIVE_PAYMENT_RATIO",
            "description": "Test finding",
            "estimated_recoverable": 1000.0,
            "confidence_score": 0.85,
        },
        pdf_bytes=b"%PDF-1.4 stub",
        payer_id="BMI",
        office={
            "name": "Nashville",
            "submission_email": "nashville@bmi.com",
            "mailing_address": "10 Music Square East",
            "phone": "1-844-BMI-4255",
        },
    )
    assert result["redirected"] is False
    assert result["submission_address"] == "nashville@bmi.com"
    assert result["intended_recipient"] == "nashville@bmi.com"


def test_redirect_empty_string_treated_as_unset(monkeypatch):
    monkeypatch.setenv("XR7_DISPUTE_REDIRECT_EMAIL", "   ")
    result = deliver_dispute(
        claim={"id": "clm_test", "payer_name": "BMI"},
        artist={"id": "art_test", "name": "Test"},
        anomaly={"subtype": "HIGH_RETROACTIVE_PAYMENT_RATIO", "description": "x"},
        pdf_bytes=b"%PDF-1.4",
        payer_id="BMI",
        office={"name": "Nashville", "submission_email": "nashville@bmi.com"},
    )
    assert result["redirected"] is False
