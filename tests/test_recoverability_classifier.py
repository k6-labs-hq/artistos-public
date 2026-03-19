from __future__ import annotations

from XR7.recovery.recoverability_classifier import (
    COPYRIGHT_DAMAGES,
    EXPIRED_REDIS,
    FUTURE_PREVENTION,
    POTENTIALLY_CONTRACT,
    RECOVERABLE,
    build_recoverability_payload,
    claim_draft_allowed_for_class,
)


def test_classifier_marks_metadata_non_monetary_as_prevention_only():
    payload = build_recoverability_payload(
        {
            "subtype": "METADATA_DRIFT_IDENTIFIER_GAP",
            "estimated_recoverable": 0.0,
            "confidence_score": 0.76,
        }
    )
    assert payload["recoverability"]["recoverability_class"] == FUTURE_PREVENTION
    assert payload["claim_draft_allowed"] is False


def test_classifier_marks_contract_based_underpayment():
    payload = build_recoverability_payload(
        {
            "subtype": "RATE_DRIFT_UNDERPAYMENT",
            "estimated_recoverable": 2500.0,
            "confidence_score": 0.9,
            "event_date": "2025-02-01T00:00:00+00:00",
        }
    )
    assert payload["recoverability"]["recoverability_class"] == POTENTIALLY_CONTRACT
    assert payload["claim_draft_allowed"] is True


def test_classifier_marks_copyright_damages_path():
    payload = build_recoverability_payload(
        {
            "subtype": "MISREPORTED_USAGE_FOREIGN_MISROUTING",
            "estimated_recoverable": 1800.0,
            "confidence_score": 0.86,
            "event_date": "2022-08-01T00:00:00+00:00",
        }
    )
    assert payload["recoverability"]["recoverability_class"] == COPYRIGHT_DAMAGES
    assert payload["claim_draft_allowed"] is True


def test_classifier_marks_expired_black_box_path():
    payload = build_recoverability_payload(
        {
            "subtype": "ASCAP_UNMATCHED_ROYALTY",
            "estimated_recoverable": 900.0,
            "confidence_score": 0.83,
            "event_date": "2018-01-01T00:00:00+00:00",
        }
    )
    assert payload["recoverability"]["recoverability_class"] == EXPIRED_REDIS
    assert payload["claim_draft_allowed"] is False


def test_claim_draft_allowlist_matches_spec():
    assert claim_draft_allowed_for_class(RECOVERABLE) is True
    assert claim_draft_allowed_for_class(POTENTIALLY_CONTRACT) is True
    assert claim_draft_allowed_for_class(COPYRIGHT_DAMAGES) is True
    assert claim_draft_allowed_for_class(EXPIRED_REDIS) is False
    assert claim_draft_allowed_for_class(FUTURE_PREVENTION) is False
