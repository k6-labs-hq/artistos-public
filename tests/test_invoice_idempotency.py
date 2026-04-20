"""
Tests for billing invoice idempotency and revenue integrity.

Validates that invoices cannot be duplicate-created for the same claim,
preventing double-billing and revenue reconciliation failures.

Closes: XR7-406
Domain: billing-accuracy
Scale-target: Revenue integrity for 10x claim volume
Compliance: SOC 2 CC6.8 — System operations (billing controls)
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.billing.engine import BillingEngine
from XR7.models.artist import Artist
from XR7.models.base import Base
from XR7.models.claim import Claim, ClaimStatus


@pytest.fixture
def db_session():
    """Create in-memory test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def test_artist(db_session):
    """Create test artist with contingency fee."""
    artist = Artist(
        id="test-artist-1",
        email="artist@example.com",
        name="Test Artist",
        contingency_fee_percent=12.0,
    )
    db_session.add(artist)
    db_session.commit()
    db_session.refresh(artist)
    yield artist


@pytest.fixture
def test_claim(db_session, test_artist):
    """Create test claim for invoice creation."""
    claim = Claim(
        id="claim-test-1",
        artist_id=test_artist.id,
        anomaly_id="anomaly-1",
        claim_type="ROYALTY_DISPUTE",
        status=ClaimStatus.IDENTIFIED,
        currency="USD",
    )
    db_session.add(claim)
    db_session.commit()
    db_session.refresh(claim)
    yield claim


def test_create_invoice_standard_case(db_session, test_artist):
    """Creating an invoice should calculate correct contingency fee."""
    # Create claim first (required by database-level implementation)
    claim = Claim(
        id="claim-1",
        artist_id=test_artist.id,
        anomaly_id="anomaly-1",
        claim_type="ROYALTY_DISPUTE",
        status=ClaimStatus.IDENTIFIED,
        currency="USD",
    )
    db_session.add(claim)
    db_session.commit()

    engine = BillingEngine(db_session)

    invoice = engine.create_invoice(
        claim_id="claim-1",
        recovered_amount=10000.0,
        currency="USD",
        artist_id=test_artist.id,
    )

    assert invoice["claim_id"] == "claim-1"
    assert invoice["recovered_amount"] == 10000.0
    assert invoice["contingency_fee"] == 1200.0  # 12% of 10000
    assert invoice["currency"] == "USD"
    assert invoice["status"] == "PENDING"
    assert "invoice_id" in invoice


def test_create_invoice_idempotency_same_claim_returns_existing(db_session, test_artist):
    """Creating invoice for same claim_id twice should return same invoice."""
    engine = BillingEngine(db_session)

    # Create first invoice
    invoice1 = engine.create_invoice(
        claim_id="claim-2",
        recovered_amount=5000.0,
        currency="USD",
        artist_id=test_artist.id,
    )

    # Attempt to create second invoice for same claim
    invoice2 = engine.create_invoice(
        claim_id="claim-2",
        recovered_amount=5000.0,
        currency="USD",
        artist_id=test_artist.id,
    )

    # Should return the same invoice
    assert invoice1["invoice_id"] == invoice2["invoice_id"]
    assert invoice1["claim_id"] == invoice2["claim_id"]
    assert invoice1["created_at"] == invoice2["created_at"]


def test_create_invoice_idempotency_prevents_double_billing(db_session, test_artist):
    """Idempotency prevents double-billing even with different amounts."""
    engine = BillingEngine(db_session)

    # Create invoice with recovered amount $10,000
    invoice1 = engine.create_invoice(
        claim_id="claim-3",
        recovered_amount=10000.0,
        currency="USD",
        artist_id=test_artist.id,
    )

    # Attempt to create invoice with different amount (e.g., correction attempt)
    invoice2 = engine.create_invoice(
        claim_id="claim-3",
        recovered_amount=12000.0,  # Different amount
        currency="USD",
        artist_id=test_artist.id,
    )

    # Should return ORIGINAL invoice, ignoring new amount
    assert invoice1["invoice_id"] == invoice2["invoice_id"]
    assert invoice2["recovered_amount"] == 10000.0  # Original amount preserved
    assert invoice2["contingency_fee"] == 1200.0  # Original fee preserved


def test_multiple_claims_get_separate_invoices(db_session, test_artist):
    """Different claims should get different invoices."""
    engine = BillingEngine(db_session)

    invoice1 = engine.create_invoice(
        claim_id="claim-4",
        recovered_amount=5000.0,
        currency="USD",
        artist_id=test_artist.id,
    )

    invoice2 = engine.create_invoice(
        claim_id="claim-5",
        recovered_amount=7000.0,
        currency="USD",
        artist_id=test_artist.id,
    )

    # Should be different invoices
    assert invoice1["invoice_id"] != invoice2["invoice_id"]
    assert invoice1["claim_id"] == "claim-4"
    assert invoice2["claim_id"] == "claim-5"


def test_negative_amount_raises_error(db_session, test_artist):
    """Negative recovered amount should be rejected."""
    engine = BillingEngine(db_session)

    with pytest.raises(ValueError, match="must be non-negative"):
        engine.create_invoice(
            claim_id="claim-6",
            recovered_amount=-1000.0,
            currency="USD",
            artist_id=test_artist.id,
        )


def test_zero_amount_allowed(db_session, test_artist):
    """Zero amount invoices should be allowed (e.g., no-recovery claims)."""
    engine = BillingEngine(db_session)

    invoice = engine.create_invoice(
        claim_id="claim-7",
        recovered_amount=0.0,
        currency="USD",
        artist_id=test_artist.id,
    )

    assert invoice["recovered_amount"] == 0.0
    assert invoice["contingency_fee"] == 0.0


def test_invoice_contingency_fee_uses_artist_specific_rate(db_session):
    """Invoice should use artist-specific contingency fee rate."""
    # Create artist with custom fee rate (15% instead of default 12%)
    artist_vip = Artist(
        id="artist-vip",
        email="vip@example.com",
        name="VIP Artist",
        contingency_fee_percent=15.0,  # Custom rate
    )
    db_session.add(artist_vip)
    db_session.commit()

    engine = BillingEngine(db_session)

    invoice = engine.create_invoice(
        claim_id="claim-8",
        recovered_amount=10000.0,
        currency="USD",
        artist_id=artist_vip.id,
    )

    # Should use 15% rate
    assert invoice["contingency_fee"] == 1500.0


def test_invoice_creation_preserves_currency(db_session, test_artist):
    """Invoice should preserve currency across idempotent calls."""
    engine = BillingEngine(db_session)

    invoice1 = engine.create_invoice(
        claim_id="claim-9",
        recovered_amount=5000.0,
        currency="EUR",
        artist_id=test_artist.id,
    )

    invoice2 = engine.create_invoice(
        claim_id="claim-9",
        recovered_amount=5000.0,
        currency="USD",  # Different currency attempt
        artist_id=test_artist.id,
    )

    # Should preserve original currency
    assert invoice1["currency"] == "EUR"
    assert invoice2["currency"] == "EUR"  # Original preserved


def test_concurrent_invoice_creation_idempotency():
    """Simulate concurrent invoice creation for same claim."""
    from concurrent.futures import ThreadPoolExecutor

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    artist = Artist(
        id="artist-concurrent",
        email="concurrent@example.com",
        name="Concurrent Test",
        contingency_fee_percent=12.0,
    )
    session.add(artist)
    session.commit()

    billing_engine = BillingEngine(session)

    def create_invoice_wrapper():
        return billing_engine.create_invoice(
            claim_id="claim-concurrent",
            recovered_amount=10000.0,
            currency="USD",
            artist_id=artist.id,
        )

    # Simulate 10 concurrent requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_invoice_wrapper) for _ in range(10)]
        invoices = [f.result() for f in futures]

    # All should return the same invoice
    invoice_ids = [inv["invoice_id"] for inv in invoices]
    assert len(set(invoice_ids)) == 1  # Only one unique invoice ID

    session.close()
    Base.metadata.drop_all(engine)


def test_invoice_status_lifecycle(db_session, test_artist):
    """Invoice status should transition correctly."""
    # Create claim first
    claim = Claim(
        id="claim-10",
        artist_id=test_artist.id,
        anomaly_id="anomaly-10",
        claim_type="ROYALTY_DISPUTE",
        status=ClaimStatus.IDENTIFIED,
        currency="USD",
    )
    db_session.add(claim)
    db_session.commit()

    engine = BillingEngine(db_session)

    invoice = engine.create_invoice(
        claim_id="claim-10",
        recovered_amount=8000.0,
        currency="USD",
        artist_id=test_artist.id,
    )

    assert invoice["status"] == "PENDING"

    # Process payment
    paid_invoice = engine.process_payment(invoice["invoice_id"])

    assert paid_invoice["status"] == "PAID"
    assert paid_invoice["invoice_id"] == invoice["invoice_id"]


def test_database_level_idempotency_survives_process_crash():
    """
    TDD-BILL-001: Database-level idempotency constraint prevents double-billing
    after process crash + Celery retry.

    Critical Scenario: Under Celery retry with process crash between invoice creation
    and acknowledgment, in-memory idempotency dict is lost. Without database-level
    constraint, duplicate invoices would be created → double-billing.

    This test simulates process crash by creating a new BillingEngine instance
    (losing all in-memory state) and verifies that database unique constraint
    prevents duplicate invoice creation.

    Compliance: SOC 2 CC6.1 - Logical access controls (revenue integrity)
    Severity: CRITICAL - Revenue correctness failure risk
    """
    # Setup: Create database and commit artist + claim
    engine_db = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine_db)
    Session = sessionmaker(bind=engine_db)

    # Create artist and claim in initial session
    session1 = Session()
    artist = Artist(
        id="artist-crash-test",
        email="crash@example.com",
        name="Crash Test Artist",
        contingency_fee_percent=12.0,
    )
    claim = Claim(
        id="claim-crash-test",
        artist_id=artist.id,
        anomaly_id="anomaly-crash",
        claim_type="ROYALTY_DISPUTE",
        status=ClaimStatus.IDENTIFIED,
        currency="USD",
    )
    session1.add(artist)
    session1.add(claim)
    session1.commit()
    artist_id = artist.id  # Store ID before closing session
    session1.close()

    # STEP 1: Create invoice with first BillingEngine instance
    session2 = Session()
    billing_engine_1 = BillingEngine(session2)

    invoice1 = billing_engine_1.create_invoice(
        claim_id="claim-crash-test",
        recovered_amount=10000.0,
        currency="USD",
        artist_id=artist_id,
    )

    assert invoice1["invoice_id"]
    assert invoice1["recovered_amount"] == 10000.0
    assert invoice1["contingency_fee"] == 1200.0

    # Commit invoice to database
    session2.commit()
    invoice1_id = invoice1["invoice_id"]
    session2.close()

    # SIMULATE PROCESS CRASH: New session, new BillingEngine instance
    # All in-memory state (_invoices dict) is lost
    session3 = Session()
    billing_engine_2 = BillingEngine(session3)

    # STEP 2: Celery retry attempts to create invoice again
    # Without database constraint, this would create DUPLICATE invoice
    invoice2 = billing_engine_2.create_invoice(
        claim_id="claim-crash-test",  # SAME claim_id
        recovered_amount=10000.0,
        currency="USD",
        artist_id=artist_id,
    )

    # ASSERT: Database constraint prevented duplicate, returned existing invoice
    assert invoice2["invoice_id"] == invoice1_id  # SAME invoice ID
    assert invoice2["recovered_amount"] == 10000.0
    assert invoice2["contingency_fee"] == 1200.0

    # VERIFY: Only ONE invoice exists in database for this claim
    from XR7.models.invoice import Invoice

    invoices_in_db = session3.query(Invoice).filter(Invoice.claim_id == "claim-crash-test").all()
    assert len(invoices_in_db) == 1  # Only one invoice persisted
    assert invoices_in_db[0].id == invoice1_id

    session3.close()
    Base.metadata.drop_all(engine_db)

    # SUCCESS: TDD-BILL-001 remediation works correctly
    # Database constraint (uq_invoices_claim_id) prevented double-billing
    # even after simulated process crash + in-memory state loss
