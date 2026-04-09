from __future__ import annotations

from datetime import datetime, timedelta, timezone

from XR7.recovery.black_box_expiration import (
    evaluate_black_box_expiration,
    evaluate_black_box_expiration_for_anomaly,
)


def test_mlc_three_year_rule_expires_old_event():
    old_event = datetime.now(timezone.utc) - timedelta(days=365 * 4)
    result = evaluate_black_box_expiration(
        payer_or_society="MLC",
        royalty_type="digital_mechanicals",
        event_date=old_event,
    )
    assert result["is_expired"] is True
    assert result["expiration_date"] is not None
    assert "MLC" in result["rule_applied"]


def test_contract_governed_backend_has_no_black_box_expiration():
    event_date = datetime.now(timezone.utc) - timedelta(days=365 * 8)
    result = evaluate_black_box_expiration(
        payer_or_society="STUDIO_BACKEND",
        royalty_type="backend_participation",
        event_date=event_date,
    )
    assert result["is_expired"] is False
    assert result["expiration_date"] is None
    assert result["days_remaining"] is None


def test_anomaly_helper_infers_union_rule():
    anomaly = {
        "subtype": "MISSING_STREAMING_RESIDUALS",
        "description": "SAG-AFTRA residual mismatch",
        "event_date": (datetime.now(timezone.utc) - timedelta(days=100)).isoformat(),
        "feature_snapshot": {"union": "SAG-AFTRA"},
    }
    result = evaluate_black_box_expiration_for_anomaly(anomaly)
    assert result["payer_or_society"] == "SAG-AFTRA"
    assert "SAG-AFTRA" in result["rule_applied"]
