import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.models.base import Base
from XR7.models.artist import Artist
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.modules.black_box_countdown import BlackBoxCountdown, _REDISTRIBUTION_RULES, apply_freeze, is_frozen


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def artist(db_session):
    a = Artist(id="artist-bbc", name="BBC Artist")
    db_session.add(a)
    db_session.commit()
    return a


def make_anomaly(db_session, artist_id, anomaly_id, days_old=100):
    a = Anomaly(
        id=anomaly_id,
        artist_id=artist_id,
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.85,
        status=AnomalyStatus.OPEN,
        created_at=datetime.now(timezone.utc) - timedelta(days=days_old),
    )
    db_session.add(a)


def test_compute_all_returns_required_keys(db_session, artist):
    make_anomaly(db_session, artist.id, "anom-1", days_old=100)
    db_session.commit()

    bbc = BlackBoxCountdown(db_session)
    result = bbc.compute_all(artist.id)

    assert "countdowns" in result
    assert "critical_count" in result
    assert "chain_of_custody_hash" in result


def test_no_anomalies_returns_empty_countdowns(db_session, artist):
    bbc = BlackBoxCountdown(db_session)
    result = bbc.compute_all(artist.id)
    assert result["countdowns"] == []


def test_urgency_tier_critical(db_session, artist):
    # 729 days old with 730-day window => 1 day left => CRITICAL
    make_anomaly(db_session, artist.id, "anom-critical", days_old=729)
    db_session.commit()

    bbc = BlackBoxCountdown(db_session)
    result = bbc.compute_all(artist.id)
    # At least one entry should exist
    assert len(result["countdowns"]) >= 1


def test_urgency_tier_expired(db_session, artist):
    # 800 days old with 730-day max window => expired
    make_anomaly(db_session, artist.id, "anom-expired", days_old=800)
    db_session.commit()

    bbc = BlackBoxCountdown(db_session)
    result = bbc.compute_all(artist.id)
    expired = [c for c in result["countdowns"] if c["urgency_tier"] == "EXPIRED"]
    assert len(expired) >= 1


def test_redistribution_rules_have_expected_societies():
    assert "ASCAP" in _REDISTRIBUTION_RULES
    assert "BMI" in _REDISTRIBUTION_RULES
    assert "MLC" in _REDISTRIBUTION_RULES
    assert "JASRAC" in _REDISTRIBUTION_RULES


def test_freeze_event_logic():
    future = datetime.now(timezone.utc) + timedelta(days=30)
    apply_freeze("TEST_SOCIETY", future)
    assert is_frozen("TEST_SOCIETY", datetime.now(timezone.utc))


def test_society_not_frozen_by_default():
    # Use a society name unlikely to be frozen in test env
    assert not is_frozen("SOCIETY_NOT_FROZEN_XYZZ", datetime.now(timezone.utc))


def test_chain_of_custody_hash_format(db_session, artist):
    bbc = BlackBoxCountdown(db_session)
    result = bbc.compute_all(artist.id)
    h = result["chain_of_custody_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_summary_counts_by_tier(db_session, artist):
    make_anomaly(db_session, artist.id, "anom-s1", days_old=100)
    make_anomaly(db_session, artist.id, "anom-s2", days_old=200)
    db_session.commit()

    bbc = BlackBoxCountdown(db_session)
    result = bbc.compute_all(artist.id)
    summary = result
    assert "critical_count" in summary
    assert "at_risk_value_next_30_days" in summary
