import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from arcos7.models.base import Base
from arcos7.models.artist import Artist
from arcos7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from arcos7.models.claim import Claim, ClaimStatus
from arcos7.billing.engine import BillingEngine
from datetime import datetime


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_contingency_rate_is_10_percent():
    assert BillingEngine.CONTINGENCY_RATE == 0.10


def test_calculate_contingency_fee(db_session):
    engine = BillingEngine(db_session)
    fee = engine.calculate_contingency_fee(1000.0)
    assert fee == pytest.approx(100.0)


def test_create_invoice(db_session):
    engine = BillingEngine(db_session)
    invoice = engine.create_invoice("claim-1", 500.0, "USD")
    assert invoice["claim_id"] == "claim-1"
    assert invoice["recovered_amount"] == 500.0
    assert invoice["contingency_fee"] == pytest.approx(50.0)
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
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(claim)
    db_session.commit()
    engine = BillingEngine(db_session)
    summary = engine.get_artist_billing_summary("artist-billing")
    assert summary["artist_id"] == "artist-billing"
    assert summary["total_recovered"] == pytest.approx(2000.0)
    assert summary["total_fees"] == pytest.approx(200.0)
    assert summary["net_to_artist"] == pytest.approx(1800.0)
    assert summary["claim_count"] == 1
