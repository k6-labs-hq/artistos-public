from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.billing.engine import BillingEngine
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.base import Base
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.immutable_ledger_entry import ImmutableLedgerEntry
from XR7.models.metadata_issue import MetadataIssue
from XR7.models.trolley_transaction import TrolleyTxnStatus, TrolleyTxnType


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_contingency_rate_is_12_percent():
    assert BillingEngine.CONTINGENCY_RATE == 0.12


def test_calculate_contingency_fee(db_session):
    engine = BillingEngine(db_session)
    fee = engine.calculate_contingency_fee(1000.0)
    assert fee == pytest.approx(120.0)


def test_create_invoice(db_session):
    engine = BillingEngine(db_session)
    invoice = engine.create_invoice("claim-1", 500.0, "USD")
    assert invoice["claim_id"] == "claim-1"
    assert invoice["recovered_amount"] == 500.0
    assert invoice["contingency_fee"] == pytest.approx(60.0)
    assert invoice["currency"] == "USD"
    assert invoice["status"] == "PENDING"
    assert "invoice_id" in invoice
    assert "created_at" in invoice


def test_get_artist_billing_summary_structure(db_session):
    artist = Artist(id="artist-billing", name="Billing Artist")
    db_session.add(artist)
    anomaly = Anomaly(
        id="anomaly-billing",
        artist_id="artist-billing",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)
    db_session.commit()
    claim = Claim(
        id="claim-billing",
        artist_id="artist-billing",
        anomaly_id="anomaly-billing",
        claim_type="ROYALTY",
        status=ClaimStatus.PAID,
        recovered_amount=2000.0,
        contingency_fee=200.0,
        currency="USD",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(claim)
    db_session.add(
        MetadataIssue(
            id="meta-billing-1",
            artist_id="artist-billing",
            issue_type="TITLE_VARIANT",
            severity="LOW",
            issue_key="billing:test",
            before_value_json="{}",
            after_value_json="{}",
            confidence_score=0.95,
            repair_status="AUTO_REPAIRED",
            projected_leakage_avoided=321.5,
        )
    )
    db_session.commit()
    engine = BillingEngine(db_session)
    summary = engine.get_artist_billing_summary("artist-billing")
    assert summary["artist_id"] == "artist-billing"
    assert summary["total_recovered"] == pytest.approx(2000.0)
    assert summary["total_fees"] == pytest.approx(200.0)
    assert summary["net_to_artist"] == pytest.approx(1800.0)
    assert summary["claim_count"] == 1
    assert summary["xr7_future_leakage_prevented"] == pytest.approx(321.5)
    assert summary["xr7_future_leakage_prevented_billable"] is False
    assert summary["billing_policy"]["repairs_are_free"] is True


def test_process_refund_creates_transaction_and_audit_trail(db_session):
    """Test that process_refund creates a negative transaction and ledger entry."""
    artist = Artist(id="artist-refund-1", name="Refund Artist")
    db_session.add(artist)
    anomaly = Anomaly(
        id="anomaly-refund-1",
        artist_id="artist-refund-1",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)
    claim = Claim(
        id="claim-refund-1",
        artist_id="artist-refund-1",
        anomaly_id="anomaly-refund-1",
        claim_type="ROYALTY",
        status=ClaimStatus.PAID,
        recovered_amount=1000.0,
        platform_fee_percent=12.0,
        platform_fee_amount=120.0,
        contingency_fee=120.0,
        artist_net_amount=880.0,
        currency="USD",
    )
    db_session.add(claim)
    db_session.commit()

    engine = BillingEngine(db_session)
    tx = engine.process_refund(
        claim_id="claim-refund-1",
        refund_amount=300.0,
        reason="Payer dispute",
        refund_type="REFUND",
        trolley_refund_id="trolley-ref-123",
        notes="Customer requested refund",
    )

    # Verify transaction created with negative amounts
    assert tx.type == TrolleyTxnType.REFUND
    assert tx.status == TrolleyTxnStatus.PAID
    assert tx.gross_amount == pytest.approx(-300.0)
    assert tx.platform_fee_amount == pytest.approx(-36.0)  # 12% of 300
    assert tx.net_amount == pytest.approx(-264.0)  # 300 - 36
    assert tx.claim_id == "claim-refund-1"
    assert tx.artist_id == "artist-refund-1"
    assert tx.trolley_payment_id == "trolley-ref-123"
    assert "Payer dispute" in tx.description
    assert "Customer requested refund" in tx.description

    # Verify claim amounts adjusted
    db_session.refresh(claim)
    assert claim.recovered_amount == pytest.approx(700.0)  # 1000 - 300
    assert claim.platform_fee_amount == pytest.approx(84.0)  # 12% of 700
    assert claim.artist_net_amount == pytest.approx(616.0)  # 700 - 84
    assert claim.status == ClaimStatus.PAID  # Still paid, partial refund

    # Verify immutable ledger entry created
    ledger_entries = (
        db_session.query(ImmutableLedgerEntry)
        .filter(
            ImmutableLedgerEntry.artist_id == "artist-refund-1",
            ImmutableLedgerEntry.entry_type == "refund_processed",
        )
        .all()
    )
    assert len(ledger_entries) == 1
    assert "claim-refund-1" in ledger_entries[0].payload_json
    assert "300.0" in ledger_entries[0].payload_json
    assert "Payer dispute" in ledger_entries[0].payload_json


def test_process_refund_full_refund_reverts_status(db_session):
    """Test that a full refund reverts claim status appropriately."""
    artist = Artist(id="artist-refund-2", name="Full Refund Artist")
    db_session.add(artist)
    anomaly = Anomaly(
        id="anomaly-refund-2",
        artist_id="artist-refund-2",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)
    claim = Claim(
        id="claim-refund-2",
        artist_id="artist-refund-2",
        anomaly_id="anomaly-refund-2",
        claim_type="ROYALTY",
        status=ClaimStatus.PAID,
        recovered_amount=500.0,
        platform_fee_percent=12.0,
        platform_fee_amount=60.0,
        contingency_fee=60.0,
        artist_net_amount=440.0,
        currency="USD",
        trolley_payment_id="original-payment-123",
    )
    db_session.add(claim)
    db_session.commit()

    engine = BillingEngine(db_session)
    engine.process_refund(
        claim_id="claim-refund-2",
        refund_amount=500.0,  # Full refund
        reason="Duplicate payment",
        refund_type="REFUND",
    )

    # Verify full refund
    db_session.refresh(claim)
    assert claim.recovered_amount == pytest.approx(0.0)
    assert claim.platform_fee_amount == pytest.approx(0.0)
    assert claim.artist_net_amount == pytest.approx(0.0)
    assert claim.status == ClaimStatus.FUNDS_RECEIVED  # Reverted from PAID
    assert claim.trolley_payment_id is None  # Cleared
    assert claim.trolley_payment_status is None


def test_process_refund_chargeback_type(db_session):
    """Test that chargeback type is recorded correctly."""
    artist = Artist(id="artist-chargeback", name="Chargeback Artist")
    db_session.add(artist)
    anomaly = Anomaly(
        id="anomaly-chargeback",
        artist_id="artist-chargeback",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)
    claim = Claim(
        id="claim-chargeback",
        artist_id="artist-chargeback",
        anomaly_id="anomaly-chargeback",
        claim_type="ROYALTY",
        status=ClaimStatus.FUNDS_RECEIVED,
        recovered_amount=2000.0,
        platform_fee_percent=12.0,
        platform_fee_amount=240.0,
        contingency_fee=240.0,
        artist_net_amount=1760.0,
        currency="USD",
    )
    db_session.add(claim)
    db_session.commit()

    engine = BillingEngine(db_session)
    tx = engine.process_refund(
        claim_id="claim-chargeback",
        refund_amount=800.0,
        reason="Bank chargeback - fraud claim",
        refund_type="CHARGEBACK",
    )

    # Verify chargeback type
    assert tx.type == TrolleyTxnType.CHARGEBACK
    assert tx.failure_reason == "Bank chargeback - fraud claim"
    assert "CHARGEBACK" in tx.description

    # Verify ledger entry type
    ledger_entries = (
        db_session.query(ImmutableLedgerEntry)
        .filter(
            ImmutableLedgerEntry.artist_id == "artist-chargeback",
            ImmutableLedgerEntry.entry_type == "chargeback_processed",
        )
        .all()
    )
    assert len(ledger_entries) == 1


def test_process_refund_rejects_invalid_amount(db_session):
    """Test that process_refund rejects invalid refund amounts."""
    artist = Artist(id="artist-invalid", name="Invalid Artist")
    db_session.add(artist)
    anomaly = Anomaly(
        id="anomaly-invalid",
        artist_id="artist-invalid",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)
    claim = Claim(
        id="claim-invalid",
        artist_id="artist-invalid",
        anomaly_id="anomaly-invalid",
        claim_type="ROYALTY",
        status=ClaimStatus.PAID,
        recovered_amount=100.0,
        platform_fee_percent=12.0,
        currency="USD",
    )
    db_session.add(claim)
    db_session.commit()

    engine = BillingEngine(db_session)

    # Test negative amount
    with pytest.raises(ValueError, match="refund_amount must be greater than 0"):
        engine.process_refund(
            claim_id="claim-invalid",
            refund_amount=-50.0,
            reason="Test",
            refund_type="REFUND",
        )

    # Test zero amount
    with pytest.raises(ValueError, match="refund_amount must be greater than 0"):
        engine.process_refund(
            claim_id="claim-invalid",
            refund_amount=0.0,
            reason="Test",
            refund_type="REFUND",
        )

    # Test amount exceeds recovered
    with pytest.raises(ValueError, match="exceeds recovered amount"):
        engine.process_refund(
            claim_id="claim-invalid",
            refund_amount=150.0,  # More than 100
            reason="Test",
            refund_type="REFUND",
        )


def test_process_refund_rejects_non_refundable_status(db_session):
    """Test that process_refund rejects claims in non-refundable statuses."""
    artist = Artist(id="artist-status", name="Status Artist")
    db_session.add(artist)
    anomaly = Anomaly(
        id="anomaly-status",
        artist_id="artist-status",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)
    claim = Claim(
        id="claim-status",
        artist_id="artist-status",
        anomaly_id="anomaly-status",
        claim_type="ROYALTY",
        status=ClaimStatus.IDENTIFIED,  # Not refundable
        recovered_amount=100.0,
        platform_fee_percent=12.0,
        currency="USD",
    )
    db_session.add(claim)
    db_session.commit()

    engine = BillingEngine(db_session)

    with pytest.raises(ValueError, match="not eligible for refund"):
        engine.process_refund(
            claim_id="claim-status",
            refund_amount=50.0,
            reason="Test",
            refund_type="REFUND",
        )


def test_process_refund_rejects_invalid_refund_type(db_session):
    """Test that process_refund rejects invalid refund types."""
    artist = Artist(id="artist-type", name="Type Artist")
    db_session.add(artist)
    anomaly = Anomaly(
        id="anomaly-type",
        artist_id="artist-type",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)
    claim = Claim(
        id="claim-type",
        artist_id="artist-type",
        anomaly_id="anomaly-type",
        claim_type="ROYALTY",
        status=ClaimStatus.PAID,
        recovered_amount=100.0,
        platform_fee_percent=12.0,
        currency="USD",
    )
    db_session.add(claim)
    db_session.commit()

    engine = BillingEngine(db_session)

    with pytest.raises(ValueError, match="refund_type must be 'REFUND' or 'CHARGEBACK'"):
        engine.process_refund(
            claim_id="claim-type",
            refund_amount=50.0,
            reason="Test",
            refund_type="INVALID_TYPE",
        )


def test_process_refund_claim_not_found(db_session):
    """Test that process_refund raises error for non-existent claim."""
    engine = BillingEngine(db_session)

    with pytest.raises(ValueError, match="Claim nonexistent not found"):
        engine.process_refund(
            claim_id="nonexistent",
            refund_amount=50.0,
            reason="Test",
            refund_type="REFUND",
        )
