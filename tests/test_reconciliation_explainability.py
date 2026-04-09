"""Tests for Epic 4: Reconciliation Explainability and Case Automation.

Covers:
- Gap explanation service (LLM and fallback)
- Explain-my-gap endpoints
- Idempotency key support
- Confidence-band routing
- AI decision audit logging
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.xr7_idempotency import IdempotencyService, XR7IdempotencyRecord
from XR7.models.xr7_royalty import XR7AIDecisionAuditLog
from XR7.recovery.confidence_band_router import ConfidenceBandRouter
from XR7.recovery.gap_explainer import GapExplainerService
from tests.conftest import TestSession


client = TestClient(app)


def _create_artist(db, name: str | None = None) -> Artist:
    artist = Artist(id=str(uuid4()), name=name or f"Test Artist {uuid4().hex[:8]}", created_at=datetime.now(timezone.utc))
    db.add(artist)
    db.commit()
    db.refresh(artist)
    return artist


def _create_anomaly(
    db,
    artist_id: str,
    category: AnomalyCategory = AnomalyCategory.ROYALTY,
    subtype: str = "PAYMENT_SHORTFALL",
    confidence: float = 0.85,
    expected: float = 1000.0,
    actual: float = 800.0,
) -> Anomaly:
    anomaly = Anomaly(
        id=str(uuid4()),
        artist_id=artist_id,
        category=category,
        subtype=subtype,
        severity=AnomalySeverity.HIGH,
        confidence_score=confidence,
        expected_amount=expected,
        actual_amount=actual,
        estimated_recoverable=max(0, expected - actual),
        status=AnomalyStatus.OPEN,
        description=f"Test {subtype}",
        created_at=datetime.now(timezone.utc),
    )
    db.add(anomaly)
    db.commit()
    db.refresh(anomaly)
    return anomaly


# ============================================================================
# Gap Explainer Service Tests
# ============================================================================


def test_gap_explainer_service_fallback_explanation() -> None:
    """Test gap explainer with fallback (no LLM)."""
    anomaly_payload = {
        "id": "test-anomaly-123",
        "category": "ROYALTY",
        "subtype": "PAYMENT_SHORTFALL",
        "expected_amount": 1000.0,
        "actual_amount": 700.0,
        "confidence_score": 0.88,
        "territory": "US",
    }

    service = GapExplainerService()
    result = service.explain_gap_sync(anomaly_payload)

    assert "summary" in result
    assert "top_drivers" in result
    assert isinstance(result.get("top_drivers"), list)
    assert "confidence" in result
    assert "recommended_actions" in result
    assert isinstance(result.get("recommended_actions"), list)
    assert result["anomaly_id"] == "test-anomaly-123"
    assert result["model_version"] == "fallback-v1"


def test_gap_explainer_service_handles_missing_fields() -> None:
    """Test gap explainer with minimal payload."""
    anomaly_payload = {
        "id": "min-anomaly-789",
        "category": "ROYALTY",
        "subtype": "unknown",
    }

    service = GapExplainerService()
    result = service.explain_gap_sync(anomaly_payload)

    assert result["anomaly_id"] == "min-anomaly-789"
    assert "summary" in result
    assert result["model_version"] == "fallback-v1"


# ============================================================================
# Explain-My-Gap Endpoint Tests
# ============================================================================


def test_explain_anomaly_endpoint() -> None:
    """Test global explain-anomaly endpoint."""
    db = TestSession()
    try:
        artist = _create_artist(db)
        anomaly = _create_anomaly(db, artist.id, confidence=0.85)
        anomaly_id = anomaly.id
    finally:
        db.close()

    response = client.get(f"/anomalies/{anomaly_id}/explain")
    assert response.status_code == 200
    body = response.json()
    assert "anomaly_id" in body
    assert "explanation" in body
    assert body["anomaly_id"] == anomaly_id

    # Verify audit log was created
    db = TestSession()
    try:
        audit_logs = (
            db.query(XR7AIDecisionAuditLog)
            .filter(
                XR7AIDecisionAuditLog.input_ref == f"anomaly:{anomaly_id}",
                XR7AIDecisionAuditLog.decision_type == "gap_explanation",
            )
            .all()
        )
        assert len(audit_logs) >= 1
    finally:
        db.close()


def test_explain_artist_anomaly_endpoint() -> None:
    """Test artist-scoped explain endpoint."""
    db = TestSession()
    try:
        artist = _create_artist(db)
        artist_id = artist.id
        anomaly = _create_anomaly(db, artist.id)
        anomaly_id = anomaly.id
    finally:
        db.close()

    response = client.get(f"/artists/{artist_id}/anomalies/{anomaly_id}/explain")
    assert response.status_code == 200
    body = response.json()
    assert body["artist_id"] == artist_id
    assert body["anomaly_id"] == anomaly_id


def test_explain_endpoint_not_found() -> None:
    """Test explain endpoint with non-existent anomaly."""
    response = client.get(f"/anomalies/nonexistent-id-12345/explain")
    assert response.status_code == 404


def test_explain_endpoint_artist_boundary() -> None:
    """Test that artist-scoped explain respects artist boundaries."""
    db = TestSession()
    try:
        artist1 = _create_artist(db)
        artist1_id = artist1.id
        artist2 = _create_artist(db)
        artist2_id = artist2.id
        anomaly = _create_anomaly(db, artist1.id)
        anomaly_id = anomaly.id
    finally:
        db.close()

    # Try to access artist1's anomaly as artist2 - should fail
    response = client.get(f"/artists/{artist2_id}/anomalies/{anomaly_id}/explain")
    assert response.status_code == 404


# ============================================================================
# Idempotency Tests
# ============================================================================


def test_idempotency_service_first_request() -> None:
    """Test first request with new idempotency key."""
    db = TestSession()
    try:
        service = IdempotencyService(db)
        response_body = {"status": "created", "id": "test-123"}

        is_duplicate, cached = service.check_and_record(
            idempotency_key="test-key-001",
            tenant_id="default",
            artist_id="artist-001",
            request_path="/api/test",
            request_method="POST",
            response_status=201,
            response_body=response_body,
        )

        assert is_duplicate is False
        assert cached is None

        # Verify record was created
        record = db.query(XR7IdempotencyRecord).filter_by(idempotency_key="test-key-001").first()
        assert record is not None
        assert record.response_status == 201
    finally:
        db.close()


def test_idempotency_service_duplicate_request() -> None:
    """Test second request with same idempotency key."""
    db = TestSession()
    try:
        service = IdempotencyService(db)
        response_body = {"status": "created", "id": "test-456"}

        # First request
        service.check_and_record(
            idempotency_key="test-key-002",
            tenant_id="default",
            artist_id="artist-002",
            request_path="/api/test",
            request_method="POST",
            response_status=201,
            response_body=response_body,
        )

        # Second request with same key
        is_duplicate, cached = service.check_and_record(
            idempotency_key="test-key-002",
            tenant_id="default",
            artist_id="artist-002",
            request_path="/api/test",
            request_method="POST",
            response_status=201,
            response_body={"different": "payload"},  # Different payload - should return cached
        )

        assert is_duplicate is True
        assert cached == response_body  # Should return first response
    finally:
        db.close()


def test_idempotency_service_get_by_key() -> None:
    """Test retrieving idempotency record by key."""
    db = TestSession()
    try:
        service = IdempotencyService(db)
        response_body = {"result": "success"}

        service.check_and_record(
            idempotency_key="test-key-retrieval",
            tenant_id="default",
            artist_id="artist-003",
            request_path="/api/retrieve",
            request_method="PUT",
            response_status=200,
            response_body=response_body,
        )

        retrieved = service.get_by_key("test-key-retrieval")
        assert retrieved is not None
        assert retrieved["idempotency_key"] == "test-key-retrieval"
        assert retrieved["tenant_id"] == "default"
        assert retrieved["response_body"] == response_body
    finally:
        db.close()


# ============================================================================
# Confidence Band Router Tests
# ============================================================================


def test_confidence_band_router_classify_high() -> None:
    """Test classification of high confidence score."""
    band = ConfidenceBandRouter.classify_band(0.95)
    assert band == "high"

    band = ConfidenceBandRouter.classify_band(0.90)
    assert band == "high"


def test_confidence_band_router_classify_medium() -> None:
    """Test classification of medium confidence score."""
    band = ConfidenceBandRouter.classify_band(0.80)
    assert band == "medium"

    band = ConfidenceBandRouter.classify_band(0.70)
    assert band == "medium"


def test_confidence_band_router_classify_low() -> None:
    """Test classification of low confidence score."""
    band = ConfidenceBandRouter.classify_band(0.65)
    assert band == "low"

    band = ConfidenceBandRouter.classify_band(0.0)
    assert band == "low"


def test_confidence_band_router_route_high_confidence() -> None:
    """Test routing of high-confidence anomaly."""
    db = TestSession()
    try:
        artist = _create_artist(db)
        anomaly = _create_anomaly(db, artist.id, confidence=0.95)

        router = ConfidenceBandRouter(db)
        result = router.route_anomaly(
            anomaly_id=anomaly.id,
            artist_id=artist.id,
            confidence=0.95,
            estimated_recoverable=200.0,
            anomaly_payload={
                "id": anomaly.id,
                "category": "ROYALTY",
                "estimated_recoverable": 200.0,
            },
        )

        assert result["band"] == "high"
        assert "auto_case_create" in result["actions"]
    finally:
        db.close()


def test_confidence_band_router_route_medium_confidence() -> None:
    """Test routing of medium-confidence anomaly."""
    db = TestSession()
    try:
        artist = _create_artist(db)

        router = ConfidenceBandRouter(db)
        result = router.route_anomaly(
            anomaly_id="test-medium-anomaly",
            artist_id=artist.id,
            confidence=0.75,
            estimated_recoverable=150.0,
            anomaly_payload={"category": "ROYALTY"},
        )

        assert result["band"] == "medium"
        assert "enqueue_analyst_review" in result["actions"]
    finally:
        db.close()


def test_confidence_band_router_route_low_confidence() -> None:
    """Test routing of low-confidence anomaly."""
    db = TestSession()
    try:
        artist = _create_artist(db)

        router = ConfidenceBandRouter(db)
        result = router.route_anomaly(
            anomaly_id="test-low-anomaly",
            artist_id=artist.id,
            confidence=0.5,
            estimated_recoverable=100.0,
            anomaly_payload={"category": "ROYALTY"},
        )

        assert result["band"] == "low"
        assert "enqueue_watchlist" in result["actions"]
    finally:
        db.close()


def test_confidence_band_router_batch_routing() -> None:
    """Test batch routing of multiple anomalies."""
    db = TestSession()
    try:
        artist = _create_artist(db)

        router = ConfidenceBandRouter(db)
        anomalies = [
            {"id": "anom1", "artist_id": artist.id, "confidence_score": 0.95, "estimated_recoverable": 300},
            {"id": "anom2", "artist_id": artist.id, "confidence_score": 0.75, "estimated_recoverable": 200},
            {"id": "anom3", "artist_id": artist.id, "confidence_score": 0.50, "estimated_recoverable": 100},
        ]

        result = router.route_batch(anomalies)

        assert result["total"] == 3
        assert result["high_count"] == 1
        assert result["medium_count"] == 1
        assert result["low_count"] == 1
    finally:
        db.close()


# ============================================================================
# Integration Tests
# ============================================================================


def test_explain_endpoint_integration_full_flow() -> None:
    """Integration test: create anomaly, explain it, verify audit log."""
    db = TestSession()
    try:
        artist = _create_artist(db)
        anomaly = _create_anomaly(
            db,
            artist.id,
            category=AnomalyCategory.ROYALTY,
            subtype="PLATFORM_UNDERREPORT",
            confidence=0.88,
            expected=5000.0,
            actual=3500.0,
        )
    finally:
        db.close()

    # Call explain endpoint
    response = client.get(f"/artists/{artist.id}/anomalies/{anomaly.id}/explain")
    assert response.status_code == 200
    body = response.json()

    # Check response structure
    explanation = body.get("explanation", {})
    assert explanation.get("anomaly_id") == anomaly.id
    assert "summary" in explanation
    assert "top_drivers" in explanation
    assert "confidence" in explanation

    # Verify audit log
    db = TestSession()
    try:
        audit_log = (
            db.query(XR7AIDecisionAuditLog)
            .filter(
                XR7AIDecisionAuditLog.input_ref == f"anomaly:{anomaly.id}",
                XR7AIDecisionAuditLog.decision_type == "gap_explanation",
            )
            .order_by(XR7AIDecisionAuditLog.created_at.desc())
            .first()
        )

        assert audit_log is not None
        assert audit_log.artist_id == artist.id
        assert audit_log.decision_type == "gap_explanation"
    finally:
        db.close()
