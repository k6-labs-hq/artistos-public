"""Tests for ISO 4217 currency code validation in claims."""

import uuid

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity
from XR7.models.artist import Artist
from XR7.models.base import Base, engine, get_db
from XR7.models.claim import VALID_CURRENCY_CODES, Claim, ClaimSchema, ClaimStatus


@pytest.fixture(autouse=True)
def setup_test_db():
    """Setup test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_artist_and_anomaly():
    """Create test artist and anomaly."""
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

        return artist, anomaly
    finally:
        db.close()


def test_claim_accepts_valid_currency_usd(test_artist_and_anomaly):
    """Test that claims accept USD (default currency)."""
    artist, anomaly = test_artist_and_anomaly
    db = next(get_db())
    try:
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
            currency="USD",
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)

        assert claim.currency == "USD"
    finally:
        db.close()


def test_claim_accepts_valid_currency_eur(test_artist_and_anomaly):
    """Test that claims accept EUR currency."""
    artist, anomaly = test_artist_and_anomaly
    db = next(get_db())
    try:
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
            currency="EUR",
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)

        assert claim.currency == "EUR"
    finally:
        db.close()


def test_claim_accepts_all_valid_currencies(test_artist_and_anomaly):
    """Test that all ISO 4217 codes in VALID_CURRENCY_CODES are accepted."""
    artist, anomaly = test_artist_and_anomaly
    db = next(get_db())
    try:
        # Test a sampling of currencies from the list
        test_currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "BRL", "INR"]

        for currency_code in test_currencies:
            assert currency_code in VALID_CURRENCY_CODES
            claim = Claim(
                id=str(uuid.uuid4()),
                artist_id=artist.id,
                anomaly_id=anomaly.id,
                claim_type="royalty_recovery",
                status=ClaimStatus.IDENTIFIED,
                currency=currency_code,
            )
            db.add(claim)
            db.commit()
            db.refresh(claim)

            assert claim.currency == currency_code
    finally:
        db.close()


def test_claim_rejects_invalid_currency_database_constraint(test_artist_and_anomaly):
    """Test that database constraint rejects invalid currency codes."""
    artist, anomaly = test_artist_and_anomaly
    db = next(get_db())
    try:
        # Try to create claim with invalid currency
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
        )
        # Bypass ORM validation by setting attribute directly
        claim.currency = "INVALID"
        db.add(claim)

        # Should raise IntegrityError from database constraint
        with pytest.raises(IntegrityError) as exc_info:
            db.commit()

        assert (
            "valid_currency_code" in str(exc_info.value).lower()
            or "check constraint" in str(exc_info.value).lower()
        )
    finally:
        db.rollback()
        db.close()


def test_claim_schema_rejects_invalid_currency_pydantic():
    """Test that Pydantic validator rejects invalid currency codes."""
    with pytest.raises(ValidationError) as exc_info:
        ClaimSchema(
            id=str(uuid.uuid4()),
            artist_id=str(uuid.uuid4()),
            anomaly_id=str(uuid.uuid4()),
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
            currency="INVALID",  # Invalid currency code
            created_at="2026-04-16T00:00:00Z",
            updated_at="2026-04-16T00:00:00Z",
        )

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("currency",)
    assert "invalid currency code" in errors[0]["msg"].lower()


def test_claim_schema_rejects_lowercase_currency():
    """Test that Pydantic validator rejects lowercase currency codes."""
    with pytest.raises(ValidationError) as exc_info:
        ClaimSchema(
            id=str(uuid.uuid4()),
            artist_id=str(uuid.uuid4()),
            anomaly_id=str(uuid.uuid4()),
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
            currency="usd",  # Should be "USD"
            created_at="2026-04-16T00:00:00Z",
            updated_at="2026-04-16T00:00:00Z",
        )

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "invalid currency code" in errors[0]["msg"].lower()


def test_claim_schema_rejects_cryptocurrency():
    """Test that cryptocurrency codes are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        ClaimSchema(
            id=str(uuid.uuid4()),
            artist_id=str(uuid.uuid4()),
            anomaly_id=str(uuid.uuid4()),
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
            currency="BTC",  # Bitcoin not supported
            created_at="2026-04-16T00:00:00Z",
            updated_at="2026-04-16T00:00:00Z",
        )

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "invalid currency code" in errors[0]["msg"].lower()
    assert "BTC" in errors[0]["msg"]


def test_trolley_local_currency_accepts_valid_codes(test_artist_and_anomaly):
    """Test that trolley_local_currency accepts valid ISO 4217 codes."""
    artist, anomaly = test_artist_and_anomaly
    db = next(get_db())
    try:
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
            currency="USD",
            trolley_local_currency="EUR",  # FX conversion to EUR
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)

        assert claim.trolley_local_currency == "EUR"
    finally:
        db.close()


def test_trolley_local_currency_accepts_null(test_artist_and_anomaly):
    """Test that trolley_local_currency can be NULL."""
    artist, anomaly = test_artist_and_anomaly
    db = next(get_db())
    try:
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
            currency="USD",
            trolley_local_currency=None,
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)

        assert claim.trolley_local_currency is None
    finally:
        db.close()


def test_trolley_local_currency_rejects_invalid_code_database(test_artist_and_anomaly):
    """Test that database constraint rejects invalid trolley_local_currency."""
    artist, anomaly = test_artist_and_anomaly
    db = next(get_db())
    try:
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
            currency="USD",
        )
        # Bypass ORM validation
        claim.trolley_local_currency = "INVALID"
        db.add(claim)

        with pytest.raises(IntegrityError) as exc_info:
            db.commit()

        assert (
            "valid_trolley_currency_code" in str(exc_info.value).lower()
            or "check constraint" in str(exc_info.value).lower()
        )
    finally:
        db.rollback()
        db.close()


def test_claim_schema_rejects_invalid_trolley_currency():
    """Test that Pydantic validator rejects invalid trolley_local_currency."""
    with pytest.raises(ValidationError) as exc_info:
        ClaimSchema(
            id=str(uuid.uuid4()),
            artist_id=str(uuid.uuid4()),
            anomaly_id=str(uuid.uuid4()),
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
            currency="USD",
            trolley_local_currency="INVALID",
            created_at="2026-04-16T00:00:00Z",
            updated_at="2026-04-16T00:00:00Z",
        )

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("trolley_local_currency",)
    assert "invalid trolley currency code" in errors[0]["msg"].lower()


def test_valid_currency_codes_constant_is_comprehensive():
    """Test that VALID_CURRENCY_CODES includes major international currencies."""
    # Major global currencies must be present
    required_currencies = [
        "USD",  # United States
        "EUR",  # Eurozone
        "GBP",  # United Kingdom
        "JPY",  # Japan
        "CNY",  # China
        "INR",  # India
        "BRL",  # Brazil
        "CAD",  # Canada
        "AUD",  # Australia
        "MXN",  # Mexico
    ]

    for currency in required_currencies:
        assert currency in VALID_CURRENCY_CODES, f"{currency} must be in VALID_CURRENCY_CODES"

    # Should have reasonable number of currencies (not too few)
    assert len(VALID_CURRENCY_CODES) >= 30, "Should support at least 30 currencies"


def test_currency_validation_prevents_trolley_api_errors(test_artist_and_anomaly):
    """
    Integration test: Verify currency validation prevents Trolley API errors.

    This simulates the scenario where invalid currency would cause Trolley
    payout to fail, requiring manual intervention.
    """
    artist, anomaly = test_artist_and_anomaly
    db = next(get_db())
    try:
        # Scenario 1: Typo in currency code
        claim1 = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
        )
        claim1.currency = "USd"  # Typo

        db.add(claim1)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        # Scenario 2: Non-existent currency code
        claim2 = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
        )
        claim2.currency = "XXX"

        db.add(claim2)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        # Scenario 3: Valid currency works fine
        claim3 = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="royalty_recovery",
            status=ClaimStatus.IDENTIFIED,
            currency="EUR",
        )
        db.add(claim3)
        db.commit()  # Should succeed

        assert claim3.currency == "EUR"
    finally:
        db.close()
