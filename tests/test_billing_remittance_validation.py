"""
Test validation guards in record_manual_remittance() to prevent negative payouts.

CRITICAL FINANCIAL VALIDATION: These tests verify that manual remittance
recording has proper validation to prevent fee overcharges and negative payouts.

Without validation:
- Fee percentage could exceed 100%, causing negative artist payout
- Platform fee could exceed gross amount (artist owes money)
- Accounting errors cause artist disputes
- Financial reconciliation fails

With validation:
- Fee must be less than gross amount
- Artist net must be positive
- Clear error messages for misconfigured fees
- Financial integrity maintained
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.billing.engine import BillingEngine
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.base import Base
from XR7.models.claim import Claim, ClaimStatus


@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample_claim(db_session):
    """Create sample artist, anomaly, and claim for testing."""
    artist = Artist(id="artist-remit", name="Test Artist")
    db_session.add(artist)

    anomaly = Anomaly(
        id="anomaly-remit",
        artist_id="artist-remit",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)

    claim = Claim(
        id="claim-remit",
        artist_id="artist-remit",
        anomaly_id="anomaly-remit",
        claim_type="ROYALTY",
        status=ClaimStatus.FILED,
        currency="USD",
        platform_fee_percent=20.0,  # Set fee at claim level
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(claim)
    db_session.commit()
    return claim


def test_record_manual_remittance_valid_calculation(db_session, sample_claim):
    """
    Verify manual remittance calculates fee and net correctly.

    With $1000 gross and 20% fee:
    - Platform fee: $200
    - Artist net: $800
    - Net is positive ✓
    - Fee is less than gross ✓
    """
    engine = BillingEngine(db_session)

    updated_claim = engine.record_manual_remittance(
        claim_id="claim-remit",
        gross_amount=1000.0,
        remittance_method="ACH",
        received_date=datetime.now(timezone.utc),
        reference_number="REF123",
    )

    assert updated_claim.recovered_amount == 1000.0
    assert updated_claim.platform_fee_amount == 200.0  # 20% of $1000
    assert updated_claim.artist_net_amount == 800.0  # $1000 - $200
    assert updated_claim.status == ClaimStatus.FUNDS_RECEIVED
    assert updated_claim.artist_net_amount > 0  # Positive payout


def test_record_manual_remittance_rejects_100_percent_fee(db_session):
    """
    Verify remittance is rejected when fee equals gross amount.

    Scenario: Misconfigured claim has 100% fee
    - Gross: $1000
    - Fee: $1000 (100%)
    - Net: $0
    - Result: ValueError (artist gets nothing)
    """
    artist = Artist(id="artist-100fee", name="100% Fee Artist")
    db_session.add(artist)

    anomaly = Anomaly(
        id="anomaly-100fee",
        artist_id="artist-100fee",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)

    claim = Claim(
        id="claim-100fee",
        artist_id="artist-100fee",
        anomaly_id="anomaly-100fee",
        claim_type="ROYALTY",
        status=ClaimStatus.FILED,
        currency="USD",
        platform_fee_percent=100.0,  # 100% fee at claim level
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(claim)
    db_session.commit()

    engine = BillingEngine(db_session)

    with pytest.raises(ValueError) as exc_info:
        engine.record_manual_remittance(
            claim_id="claim-100fee",
            gross_amount=1000.0,
            remittance_method="ACH",
            received_date=datetime.now(timezone.utc),
            reference_number="REF456",
        )

    assert "Platform fee" in str(exc_info.value)
    assert "cannot be >= gross amount" in str(exc_info.value)


def test_record_manual_remittance_rejects_over_100_percent_fee(db_session):
    """
    Verify remittance is rejected when fee exceeds gross amount.

    Scenario: Corrupted data has 150% fee
    - Gross: $1000
    - Fee: $1500 (150%)
    - Net: -$500 (NEGATIVE!)
    - Result: ValueError (prevents negative payout)
    """
    artist = Artist(id="artist-150fee", name="150% Fee Artist")
    db_session.add(artist)

    anomaly = Anomaly(
        id="anomaly-150fee",
        artist_id="artist-150fee",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)

    claim = Claim(
        id="claim-150fee",
        artist_id="artist-150fee",
        anomaly_id="anomaly-150fee",
        claim_type="ROYALTY",
        status=ClaimStatus.FILED,
        currency="USD",
        platform_fee_percent=150.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(claim)
    db_session.commit()

    engine = BillingEngine(db_session)

    with pytest.raises(ValueError) as exc_info:
        engine.record_manual_remittance(
            claim_id="claim-150fee",
            gross_amount=1000.0,
            remittance_method="ACH",
            received_date=datetime.now(timezone.utc),
            reference_number="REF789",
        )

    # Should catch it at the first guard (fee >= gross)
    assert "Platform fee" in str(exc_info.value)
    assert "cannot be >= gross amount" in str(exc_info.value)


def test_record_manual_remittance_prevents_negative_net_from_rounding(db_session):
    """
    Verify remittance catches negative net even from edge case rounding.

    Scenario: Fee calculation rounds up to consume full gross amount
    - Gross: $0.01
    - Fee: $0.01 (99.5% rounds up)
    - Net: $0.00 (rounds to 0.00)
    - Result: ValueError (net must be positive)
    """
    artist = Artist(id="artist-99fee", name="99% Fee Artist")
    db_session.add(artist)

    anomaly = Anomaly(
        id="anomaly-99fee",
        artist_id="artist-99fee",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)

    claim = Claim(
        id="claim-99fee",
        artist_id="artist-99fee",
        anomaly_id="anomaly-99fee",
        claim_type="ROYALTY",
        status=ClaimStatus.FILED,
        currency="USD",
        platform_fee_percent=99.5,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(claim)
    db_session.commit()

    engine = BillingEngine(db_session)

    # Tiny gross amount triggers rounding-to-zero edge case
    with pytest.raises(ValueError) as exc_info:
        engine.record_manual_remittance(
            claim_id="claim-99fee",
            gross_amount=0.01,
            remittance_method="ACH",
            received_date=datetime.now(timezone.utc),
            reference_number="REF999",
        )

    # Should be caught by one of the guards
    assert "Platform fee" in str(exc_info.value) or "Artist net amount" in str(exc_info.value)


def test_record_manual_remittance_edge_case_exactly_equal(db_session):
    """
    Verify fee exactly equal to gross is rejected.

    Due to rounding, fee might calculate to exactly gross:
    - Gross: $100.00
    - Fee: $100.00 (100% after rounding)
    - Net: $0.00
    - Result: ValueError
    """
    artist = Artist(id="artist-exact", name="Exact Fee Artist")
    db_session.add(artist)

    anomaly = Anomaly(
        id="anomaly-exact",
        artist_id="artist-exact",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)

    claim = Claim(
        id="claim-exact",
        artist_id="artist-exact",
        anomaly_id="anomaly-exact",
        claim_type="ROYALTY",
        status=ClaimStatus.FILED,
        currency="USD",
        platform_fee_percent=100.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(claim)
    db_session.commit()

    engine = BillingEngine(db_session)

    with pytest.raises(ValueError) as exc_info:
        engine.record_manual_remittance(
            claim_id="claim-exact",
            gross_amount=100.0,
            remittance_method="ACH",
            received_date=datetime.now(timezone.utc),
            reference_number="EXACT123",
        )

    assert "cannot be >= gross amount" in str(exc_info.value)


def test_record_manual_remittance_reasonable_fee_succeeds(db_session, sample_claim):
    """
    Verify reasonable fee percentages work correctly.

    Standard industry fee ranges: 10-30%
    - 12%: Standard XR7 contingency
    - 20%: VIP artist rate
    - 30%: High-touch service rate

    All should produce positive net amounts.
    """
    engine = BillingEngine(db_session)

    # Update fee to 30% (high but reasonable)
    claim = db_session.query(Claim).filter(Claim.id == "claim-remit").first()
    claim.platform_fee_percent = 30.0
    db_session.commit()

    updated_claim = engine.record_manual_remittance(
        claim_id="claim-remit",
        gross_amount=5000.0,
        remittance_method="WIRE",
        received_date=datetime.now(timezone.utc),
        reference_number="WIRE789",
    )

    assert updated_claim.platform_fee_amount == 1500.0  # 30% of $5000
    assert updated_claim.artist_net_amount == 3500.0  # $5000 - $1500
    assert updated_claim.artist_net_amount > 0  # Still positive


def test_record_manual_remittance_error_messages_include_amounts(db_session):
    """
    Verify error messages include actual amounts for debugging.

    When validation fails, engineers need to see:
    - Calculated platform fee
    - Gross amount
    - Fee percentage
    - Artist net (if calculated)
    """
    artist = Artist(id="artist-msg", name="Message Artist")
    db_session.add(artist)

    anomaly = Anomaly(
        id="anomaly-msg",
        artist_id="artist-msg",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)

    claim = Claim(
        id="claim-msg",
        artist_id="artist-msg",
        anomaly_id="anomaly-msg",
        claim_type="ROYALTY",
        status=ClaimStatus.FILED,
        currency="USD",
        platform_fee_percent=120.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(claim)
    db_session.commit()

    engine = BillingEngine(db_session)

    with pytest.raises(ValueError) as exc_info:
        engine.record_manual_remittance(
            claim_id="claim-msg",
            gross_amount=1000.0,
            remittance_method="CHECK",
            received_date=datetime.now(timezone.utc),
            reference_number="CHECK999",
        )

    error_msg = str(exc_info.value)
    # Error should include dollar amounts for debugging
    assert "$" in error_msg
    assert "1000" in error_msg or "1200" in error_msg  # Gross or fee amount
    assert "120%" in error_msg or "Platform fee" in error_msg


def test_validation_prevents_accounting_disputes():
    """
    Scenario test: Validation prevents artist disputes over negative payouts.

    Real-world scenario (without validation):
    1. Artist recovers $5,000 from Spotify
    2. System configured with 150% fee (data corruption)
    3. Platform fee: $7,500
    4. Artist net: -$2,500 (ARTIST OWES PLATFORM!)
    5. Payout attempted: Artist billed $2,500
    6. Artist disputes: "I won money, why do I owe you?"
    7. Support escalation, refund, legal review = $10,000+ cost

    With validation:
    1. Artist recovers $5,000
    2. System tries to calculate with 150% fee
    3. Validation catches: "Platform fee ($7,500) cannot be >= gross ($5,000)"
    4. Transaction rejected immediately
    5. Alert sent to billing team
    6. Fee corrected before artist sees negative balance
    7. No dispute, no escalation
    """
    # This is a documentation test - the actual validation is tested above
    # Just verify the validation exists
    from XR7.billing.engine import BillingEngine

    # Validation should be in place
    assert hasattr(BillingEngine, "record_manual_remittance")

    # The function should validate fee < gross and net > 0
    # (proven by the tests above that raise ValueError)
