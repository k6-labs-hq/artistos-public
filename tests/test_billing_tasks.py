"""Tests for billing Celery tasks (disbursement retry with exponential backoff)."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.base import Base
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.immutable_ledger_entry import ImmutableLedgerEntry
from XR7.tasks.billing_tasks import (
    DISBURSEMENT_RETRY_DELAYS,
    _calculate_retry_countdown,
    retry_failed_disbursement,
    scan_stuck_disbursements,
)


@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_calculate_retry_countdown():
    """Test exponential backoff delay calculation."""
    assert _calculate_retry_countdown(0) == 300  # 5 minutes
    assert _calculate_retry_countdown(1) == 1800  # 30 minutes
    assert _calculate_retry_countdown(2) == 7200  # 2 hours
    assert _calculate_retry_countdown(3) == 86400  # 24 hours
    # Beyond defined delays, use last one
    assert _calculate_retry_countdown(4) == 86400
    assert _calculate_retry_countdown(10) == 86400


def test_retry_delays_configuration():
    """Verify the retry delay schedule matches requirements."""
    assert DISBURSEMENT_RETRY_DELAYS == [300, 1800, 7200, 86400]
    assert DISBURSEMENT_RETRY_DELAYS[0] == 5 * 60  # 5 minutes
    assert DISBURSEMENT_RETRY_DELAYS[1] == 30 * 60  # 30 minutes
    assert DISBURSEMENT_RETRY_DELAYS[2] == 2 * 60 * 60  # 2 hours
    assert DISBURSEMENT_RETRY_DELAYS[3] == 24 * 60 * 60  # 24 hours


@patch("XR7.tasks.billing_tasks.SessionLocal")
@patch("XR7.tasks.billing_tasks.BillingEngine")
def test_retry_failed_disbursement_success(mock_billing_engine, mock_session_local, db_session):
    """Test successful disbursement retry."""
    # Setup
    artist = Artist(
        id="artist-retry-1",
        name="Retry Artist",
        trolley_recipient_id="recipient-123",
        payout_account_status="verified",
        tax_form_status="verified",
    )
    db_session.add(artist)
    anomaly = Anomaly(
        id="anomaly-retry-1",
        artist_id="artist-retry-1",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)
    claim = Claim(
        id="claim-retry-1",
        artist_id="artist-retry-1",
        anomaly_id="anomaly-retry-1",
        claim_type="ROYALTY",
        status=ClaimStatus.DISBURSEMENT_FAILED,
        recovered_amount=1000.0,
        platform_fee_percent=12.0,
        platform_fee_amount=120.0,
        artist_net_amount=880.0,
        payout_retry_count=1,
        payout_failure_reason="Temporary API error",
    )
    db_session.add(claim)
    db_session.commit()

    # Mock SessionLocal to return our test session
    mock_session_local.return_value = db_session

    # Mock BillingEngine.disburse_via_trolley to succeed
    mock_engine = MagicMock()
    mock_tx = MagicMock()
    mock_tx.trolley_payment_id = "trolley-success-123"
    mock_engine.disburse_via_trolley.return_value = mock_tx
    mock_billing_engine.return_value = mock_engine

    # Execute
    result = retry_failed_disbursement("claim-retry-1")

    # Verify
    assert result["status"] == "success"
    assert result["claim_id"] == "claim-retry-1"
    assert result["trolley_payment_id"] == "trolley-success-123"
    mock_engine.disburse_via_trolley.assert_called_once_with(claim_id="claim-retry-1")


@patch("XR7.tasks.billing_tasks.SessionLocal")
def test_retry_failed_disbursement_claim_not_found(mock_session_local, db_session):
    """Test retry with non-existent claim."""
    mock_session_local.return_value = db_session

    result = retry_failed_disbursement("nonexistent-claim")

    assert result["status"] == "error"
    assert result["reason"] == "claim_not_found"


@patch("XR7.tasks.billing_tasks.SessionLocal")
def test_retry_failed_disbursement_not_in_failed_status(mock_session_local, db_session):
    """Test retry skips claims not in DISBURSEMENT_FAILED status."""
    artist = Artist(id="artist-skip-1", name="Skip Artist")
    db_session.add(artist)
    anomaly = Anomaly(
        id="anomaly-skip-1",
        artist_id="artist-skip-1",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)
    claim = Claim(
        id="claim-skip-1",
        artist_id="artist-skip-1",
        anomaly_id="anomaly-skip-1",
        claim_type="ROYALTY",
        status=ClaimStatus.PAID,  # Not failed
        recovered_amount=1000.0,
    )
    db_session.add(claim)
    db_session.commit()

    mock_session_local.return_value = db_session

    result = retry_failed_disbursement("claim-skip-1")

    assert result["status"] == "skipped"
    assert result["reason"] == "not_in_failed_status"


@patch("XR7.tasks.billing_tasks.SessionLocal")
def test_retry_failed_disbursement_max_retries_exceeded(mock_session_local, db_session):
    """Test retry stops after max retries at claim level."""
    artist = Artist(id="artist-max-1", name="Max Artist")
    db_session.add(artist)
    anomaly = Anomaly(
        id="anomaly-max-1",
        artist_id="artist-max-1",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)
    claim = Claim(
        id="claim-max-1",
        artist_id="artist-max-1",
        anomaly_id="anomaly-max-1",
        claim_type="ROYALTY",
        status=ClaimStatus.DISBURSEMENT_FAILED,
        recovered_amount=1000.0,
        payout_retry_count=5,  # Already at max
    )
    db_session.add(claim)
    db_session.commit()

    mock_session_local.return_value = db_session

    result = retry_failed_disbursement("claim-max-1")

    assert result["status"] == "permanently_failed"
    assert result["retry_count"] == 5

    # Verify ledger entry created
    ledger_entries = (
        db_session.query(ImmutableLedgerEntry)
        .filter(
            ImmutableLedgerEntry.artist_id == "artist-max-1",
            ImmutableLedgerEntry.entry_type == "disbursement_permanently_failed",
        )
        .all()
    )
    assert len(ledger_entries) == 1


@patch("XR7.tasks.billing_tasks.SessionLocal")
def test_scan_stuck_disbursements_finds_eligible_claims(mock_session_local, db_session):
    """Test periodic scan finds and queues eligible failed disbursements."""
    # Create test claims
    artist1 = Artist(id="artist-scan-1", name="Scan Artist 1")
    artist2 = Artist(id="artist-scan-2", name="Scan Artist 2")
    artist3 = Artist(id="artist-scan-3", name="Scan Artist 3")
    db_session.add_all([artist1, artist2, artist3])

    anomaly1 = Anomaly(
        id="anomaly-scan-1",
        artist_id="artist-scan-1",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    anomaly2 = Anomaly(
        id="anomaly-scan-2",
        artist_id="artist-scan-2",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    anomaly3 = Anomaly(
        id="anomaly-scan-3",
        artist_id="artist-scan-3",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add_all([anomaly1, anomaly2, anomaly3])

    # Eligible: failed, retry_count < 5, updated > 5 min ago
    claim1 = Claim(
        id="claim-scan-eligible-1",
        artist_id="artist-scan-1",
        anomaly_id="anomaly-scan-1",
        claim_type="ROYALTY",
        status=ClaimStatus.DISBURSEMENT_FAILED,
        recovered_amount=1000.0,
        payout_retry_count=2,
        updated_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )

    # Not eligible: retry_count >= 5
    claim2 = Claim(
        id="claim-scan-maxed",
        artist_id="artist-scan-2",
        anomaly_id="anomaly-scan-2",
        claim_type="ROYALTY",
        status=ClaimStatus.DISBURSEMENT_FAILED,
        recovered_amount=1000.0,
        payout_retry_count=5,
        updated_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )

    # Not eligible: updated too recently
    claim3 = Claim(
        id="claim-scan-recent",
        artist_id="artist-scan-3",
        anomaly_id="anomaly-scan-3",
        claim_type="ROYALTY",
        status=ClaimStatus.DISBURSEMENT_FAILED,
        recovered_amount=1000.0,
        payout_retry_count=1,
        updated_at=datetime.now(timezone.utc) - timedelta(minutes=2),
    )

    db_session.add_all([claim1, claim2, claim3])
    db_session.commit()

    mock_session_local.return_value = db_session

    # Mock the retry task
    with patch("XR7.tasks.billing_tasks.retry_failed_disbursement") as mock_retry:
        mock_retry.delay = MagicMock()

        result = scan_stuck_disbursements()

        # Should only queue claim1
        assert result["status"] == "success"
        assert result["failed_claims_found"] == 1
        assert result["claims_queued"] == 1
        mock_retry.delay.assert_called_once_with("claim-scan-eligible-1")


@patch("XR7.tasks.billing_tasks.SessionLocal")
def test_scan_stuck_disbursements_empty_queue(mock_session_local, db_session):
    """Test scan with no eligible claims."""
    mock_session_local.return_value = db_session

    with patch("XR7.tasks.billing_tasks.retry_failed_disbursement") as mock_retry:
        result = scan_stuck_disbursements()

        assert result["status"] == "success"
        assert result["failed_claims_found"] == 0
        assert result["claims_queued"] == 0
        mock_retry.delay.assert_not_called()
