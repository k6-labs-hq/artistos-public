"""Tests for claim status audit trigger and immutable ledger."""

import json
import uuid

import pytest

# Import to register event listener
import XR7.services.claim_status_audit  # noqa: F401
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity
from XR7.models.artist import Artist
from XR7.models.base import Base, engine, get_db
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.immutable_ledger_entry import ImmutableLedgerEntry, compute_entry_hash


@pytest.fixture(autouse=True)
def setup_test_db():
    """Setup test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_claim():
    """Create a test claim with artist and anomaly."""
    db = next(get_db())
    try:
        artist = Artist(
            id=str(uuid.uuid4()),
            name="Test Artist",
            email="artist@test.com",
        )
        db.add(artist)
        db.commit()

        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            category=AnomalyCategory.ROYALTY,
            subtype="MISSING_PAYMENT",
            severity=AnomalySeverity.HIGH,
        )
        db.add(anomaly)
        db.commit()

        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)

        return claim
    finally:
        db.close()


def test_claim_status_change_creates_ledger_entry(test_claim):
    """Test that updating claim status creates immutable ledger entry."""
    db = next(get_db())
    try:
        claim_id = test_claim.id
        artist_id = test_claim.artist_id

        # Count ledger entries before
        before_count = (
            db.query(ImmutableLedgerEntry)
            .filter(ImmutableLedgerEntry.artist_id == artist_id)
            .count()
        )

        # Update claim status
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        claim.status = ClaimStatus.FILED
        db.commit()

        # Verify ledger entry was created
        after_count = (
            db.query(ImmutableLedgerEntry)
            .filter(ImmutableLedgerEntry.artist_id == artist_id)
            .count()
        )

        assert after_count == before_count + 1, "Should create one ledger entry"

        # Get the ledger entry
        entry = (
            db.query(ImmutableLedgerEntry)
            .filter(ImmutableLedgerEntry.artist_id == artist_id)
            .order_by(ImmutableLedgerEntry.created_at.desc())
            .first()
        )

        assert entry is not None
        assert entry.entry_type == "CLAIM_STATUS_CHANGE"

        # Parse and verify payload
        payload = json.loads(entry.payload_json)
        assert payload["claim_id"] == claim_id
        assert payload["old_status"] == "IDENTIFIED"
        assert payload["new_status"] == "FILED"
        assert "timestamp" in payload

    finally:
        db.close()


def test_claim_status_no_change_no_ledger_entry(test_claim):
    """Test that updating claim without status change doesn't create ledger entry."""
    db = next(get_db())
    try:
        claim_id = test_claim.id
        artist_id = test_claim.artist_id

        # Count ledger entries before
        before_count = (
            db.query(ImmutableLedgerEntry)
            .filter(ImmutableLedgerEntry.artist_id == artist_id)
            .count()
        )

        # Update claim without changing status
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        claim.recovered_amount = 1000.0
        db.commit()

        # Verify no new ledger entry
        after_count = (
            db.query(ImmutableLedgerEntry)
            .filter(ImmutableLedgerEntry.artist_id == artist_id)
            .count()
        )

        assert after_count == before_count, "Should not create ledger entry for non-status updates"

    finally:
        db.close()


def test_claim_status_chain_integrity(test_claim):
    """Test that multiple status changes create valid hash chain."""
    db = next(get_db())
    try:
        claim_id = test_claim.id
        artist_id = test_claim.artist_id

        # Perform multiple status transitions
        transitions = [
            ClaimStatus.PREPARED,
            ClaimStatus.FILED,
            ClaimStatus.SUBMITTED,
            ClaimStatus.ACCEPTED,
            ClaimStatus.PAID,
        ]

        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        for new_status in transitions:
            claim.status = new_status
            db.commit()
            db.refresh(claim)

        # Get all ledger entries for this artist
        entries = (
            db.query(ImmutableLedgerEntry)
            .filter(ImmutableLedgerEntry.artist_id == artist_id)
            .order_by(ImmutableLedgerEntry.created_at.asc())
            .all()
        )

        assert len(entries) == len(transitions), f"Should have {len(transitions)} ledger entries"

        # Verify hash chain integrity
        for i, entry in enumerate(entries):
            if i == 0:
                # First entry has no prior hash
                assert entry.prior_hash is None or entry.prior_hash == ""
            else:
                # Each entry's prior_hash should match previous entry's entry_hash
                assert (
                    entry.prior_hash == entries[i - 1].entry_hash
                ), f"Entry {i} prior_hash should match entry {i-1} entry_hash"

            # Verify hash is correctly computed
            computed_hash = compute_entry_hash(
                artist_id=entry.artist_id,
                entry_type=entry.entry_type,
                payload_json=entry.payload_json,
                prior_hash=entry.prior_hash,
            )
            assert entry.entry_hash == computed_hash, f"Entry {i} hash should be valid"

    finally:
        db.close()


def test_claim_status_audit_proves_filing_date(test_claim):
    """Test that audit log proves when claim was filed (statute of limitations protection)."""
    db = next(get_db())
    try:
        claim_id = test_claim.id
        artist_id = test_claim.artist_id

        # Transition from IDENTIFIED -> FILED
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        claim.status = ClaimStatus.FILED
        db.commit()

        # Get the FILED transition from immutable ledger
        entry = (
            db.query(ImmutableLedgerEntry)
            .filter(
                ImmutableLedgerEntry.artist_id == artist_id,
                ImmutableLedgerEntry.entry_type == "CLAIM_STATUS_CHANGE",
            )
            .order_by(ImmutableLedgerEntry.created_at.desc())
            .first()
        )

        assert entry is not None
        payload = json.loads(entry.payload_json)

        # Verify we have proof of filing
        assert payload["new_status"] == "FILED"
        assert "timestamp" in payload

        # This timestamp is immutable proof that we filed the claim
        # Even if claim table is modified, this ledger entry cannot be changed
        filing_timestamp = payload["timestamp"]
        assert filing_timestamp is not None, "Must have filing timestamp for legal compliance"

        # Verify hash chain prevents tampering
        computed_hash = compute_entry_hash(
            artist_id=entry.artist_id,
            entry_type=entry.entry_type,
            payload_json=entry.payload_json,
            prior_hash=entry.prior_hash,
        )
        assert entry.entry_hash == computed_hash, "Hash proves entry hasn't been tampered with"

    finally:
        db.close()


def test_multiple_claims_same_artist_separate_chains(test_claim):
    """Test that multiple claims for same artist are logged in same hash chain."""
    db = next(get_db())
    try:
        artist_id = test_claim.artist_id

        # Create second claim for same artist
        anomaly2 = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=artist_id,
            category=AnomalyCategory.PLATFORM,
            subtype="UNAUTHORIZED_USE",
            severity=AnomalySeverity.CRITICAL,
        )
        db.add(anomaly2)
        db.commit()

        claim2 = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist_id,
            anomaly_id=anomaly2.id,
            claim_type="copyright_infringement",
            status=ClaimStatus.IDENTIFIED,
        )
        db.add(claim2)
        db.commit()

        # Update both claims
        claim1 = db.query(Claim).filter(Claim.id == test_claim.id).first()
        claim1.status = ClaimStatus.FILED
        db.commit()

        claim2_obj = db.query(Claim).filter(Claim.id == claim2.id).first()
        claim2_obj.status = ClaimStatus.PREPARED
        db.commit()

        # Get all ledger entries for this artist
        entries = (
            db.query(ImmutableLedgerEntry)
            .filter(ImmutableLedgerEntry.artist_id == artist_id)
            .order_by(ImmutableLedgerEntry.created_at.asc())
            .all()
        )

        assert len(entries) == 2

        # Second entry should chain to first
        assert entries[1].prior_hash == entries[0].entry_hash

        # Verify different claims are tracked
        payload1 = json.loads(entries[0].payload_json)
        payload2 = json.loads(entries[1].payload_json)

        claim_ids = {payload1["claim_id"], payload2["claim_id"]}
        assert len(claim_ids) == 2, "Should track different claims"

    finally:
        db.close()
