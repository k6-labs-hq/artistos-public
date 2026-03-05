import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.models.base import Base
from XR7.models.artist import Artist
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.claim import ClaimStatus
from XR7.recovery.orchestrator import ClaimsOrchestrator


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def artist_and_anomaly(db_session):
    artist = Artist(id="artist-recovery", name="Recovery Artist")
    db_session.add(artist)
    db_session.commit()
    anomaly = Anomaly(
        id="anomaly-1",
        artist_id="artist-recovery",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)
    db_session.commit()
    return artist, anomaly


def test_create_claim_identified_status(db_session, artist_and_anomaly):
    orchestrator = ClaimsOrchestrator(db_session)
    claim = orchestrator.create_claim("anomaly-1", "ROYALTY_DISPUTE", {"note": "missing payment"})
    assert claim.status == ClaimStatus.IDENTIFIED
    assert claim.anomaly_id == "anomaly-1"
    assert claim.artist_id == "artist-recovery"


def test_advance_claim_transitions(db_session, artist_and_anomaly):
    orchestrator = ClaimsOrchestrator(db_session)
    claim = orchestrator.create_claim("anomaly-1", "ROYALTY_DISPUTE")
    assert claim.status == ClaimStatus.IDENTIFIED
    claim = orchestrator.advance_claim(claim.id)
    assert claim.status == ClaimStatus.PREPARED
    claim = orchestrator.advance_claim(claim.id)
    assert claim.status == ClaimStatus.SUBMITTED


def test_advance_claim_raises_at_terminal_state(db_session, artist_and_anomaly):
    orchestrator = ClaimsOrchestrator(db_session)
    claim = orchestrator.create_claim("anomaly-1", "ROYALTY_DISPUTE")
    # Advance all the way to CLOSED
    for _ in range(6):
        claim = orchestrator.advance_claim(claim.id)
    assert claim.status == ClaimStatus.CLOSED
    with pytest.raises(ValueError):
        orchestrator.advance_claim(claim.id)


def test_reconcile_recovered_amount(db_session, artist_and_anomaly):
    orchestrator = ClaimsOrchestrator(db_session)
    claim = orchestrator.create_claim("anomaly-1", "ROYALTY_DISPUTE")
    updated = orchestrator.reconcile_recovered_amount(claim.id, 1000.0, "USD")
    assert updated.recovered_amount == 1000.0
    assert updated.contingency_fee == pytest.approx(100.0)
    assert updated.currency == "USD"
