"""Tests for structured validation of JSON-backed claim fields."""

import uuid

import pytest
from pydantic import ValidationError

from XR7.models.claim import ClaimSchema, ClaimStatus


def _base_claim_payload() -> dict:
    return {
        "id": str(uuid.uuid4()),
        "artist_id": str(uuid.uuid4()),
        "anomaly_id": str(uuid.uuid4()),
        "claim_type": "royalty_recovery",
        "status": ClaimStatus.IDENTIFIED,
        "currency": "USD",
        "created_at": "2026-04-16T00:00:00Z",
        "updated_at": "2026-04-16T00:00:00Z",
    }


def test_claim_schema_accepts_valid_structured_json_fields() -> None:
    payload = _base_claim_payload()
    payload["evidence"] = {
        "summary": "Catalog mismatch evidence collected.",
        "confidence_score": 0.92,
        "sources": ["spotify", "soundexchange"],
        "metadata": {"case_id": "abc-123"},
    }
    payload["communications"] = [
        {
            "channel": "email",
            "message": "Initial demand sent",
            "occurred_at": "2026-04-16T10:00:00Z",
            "counterparty": "payer-legal@label.com",
        }
    ]
    payload["supporting_documents"] = [
        {
            "name": "statement-march-2026.csv",
            "document_type": "statement",
            "url": "s3://bucket/path/file.csv",
        }
    ]
    payload["legal_defensibility_report"] = {
        "summary": "Strong contractual alignment",
        "defensibility_score": 0.88,
        "risk_level": "low",
        "findings": ["contract signed", "usage proven"],
        "recommended_actions": ["file formal notice"],
    }

    claim = ClaimSchema(**payload)

    assert claim.evidence is not None
    assert claim.evidence.confidence_score == pytest.approx(0.92)
    assert claim.communications is not None
    assert claim.communications[0].channel == "email"
    assert claim.supporting_documents is not None
    assert claim.supporting_documents[0].name == "statement-march-2026.csv"
    assert claim.legal_defensibility_report is not None
    assert claim.legal_defensibility_report.defensibility_score == pytest.approx(0.88)


def test_claim_schema_rejects_non_object_evidence() -> None:
    payload = _base_claim_payload()
    payload["evidence"] = ["not", "an", "object"]

    with pytest.raises(ValidationError) as exc:
        ClaimSchema(**payload)

    assert "evidence" in str(exc.value)


def test_claim_schema_rejects_invalid_communications_item_shape() -> None:
    payload = _base_claim_payload()
    payload["communications"] = [{"channel": "email"}]

    with pytest.raises(ValidationError) as exc:
        ClaimSchema(**payload)

    assert "communications" in str(exc.value)
    assert "message" in str(exc.value)


def test_claim_schema_rejects_invalid_supporting_documents_item_shape() -> None:
    payload = _base_claim_payload()
    payload["supporting_documents"] = [{"document_type": "statement"}]

    with pytest.raises(ValidationError) as exc:
        ClaimSchema(**payload)

    assert "supporting_documents" in str(exc.value)
    assert "name" in str(exc.value)


def test_claim_schema_rejects_out_of_range_defensibility_score() -> None:
    payload = _base_claim_payload()
    payload["legal_defensibility_report"] = {
        "summary": "Report",
        "defensibility_score": 1.5,
    }

    with pytest.raises(ValidationError) as exc:
        ClaimSchema(**payload)

    assert "legal_defensibility_report" in str(exc.value)
    assert "defensibility_score" in str(exc.value)
