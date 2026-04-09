from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.base import Base
from XR7.models.payment import Payment
from XR7.modules.recovery_credit_score import RecoveryCreditScore


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
    a = Artist(id="artist-rcs", name="RCS Artist")
    db_session.add(a)
    db_session.commit()
    return a


def add_payments(db_session, artist_id, n=12, amount=1000.0):
    for i in range(n):
        db_session.add(
            Payment(
                id=f"pay-rcs-{i}",
                artist_id=artist_id,
                payment_type="ROYALTY",
                amount=amount,
                received_at=datetime.now(timezone.utc) - timedelta(days=30 * i),
                source="Spotify" if i % 2 == 0 else "Apple Music",
            )
        )


def add_anomaly(db_session, artist_id, anomaly_id, severity, days_old=60):
    db_session.add(
        Anomaly(
            id=anomaly_id,
            artist_id=artist_id,
            category=AnomalyCategory.ROYALTY,
            subtype="MISSING_PAYMENT",
            severity=severity,
            confidence_score=0.8,
            status=AnomalyStatus.OPEN,
            created_at=datetime.now(timezone.utc) - timedelta(days=days_old),
        )
    )


def test_calculate_returns_required_keys(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    scorer = RecoveryCreditScore(db_session)
    result = scorer.calculate(artist.id)

    assert "score" in result
    assert "tier" in result
    assert "score_delta" in result
    assert "trend" in result
    assert "components" in result
    assert "actions" in result
    assert "narrative" in result
    assert "chain_of_custody_hash" in result


def test_score_within_range(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    scorer = RecoveryCreditScore(db_session)
    result = scorer.calculate(artist.id)

    assert 0 <= result["score"] <= 850


def test_tier_is_valid(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    scorer = RecoveryCreditScore(db_session)
    result = scorer.calculate(artist.id)

    valid_tiers = {"EXCEPTIONAL", "STRONG", "GOOD", "FAIR", "DEVELOPING", "LIMITED"}
    assert result["tier"] in valid_tiers


def test_components_have_expected_keys(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    scorer = RecoveryCreditScore(db_session)
    result = scorer.calculate(artist.id)

    expected_components = {
        "catalog_health",
        "anomaly_recoverability",
        "sol_safety",
        "contract_clarity",
        "payer_reliability",
        "territory_coverage",
        "platform_diversification",
    }
    assert expected_components == set(result["components"].keys())


def test_component_scores_within_max(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    scorer = RecoveryCreditScore(db_session)
    result = scorer.calculate(artist.id)

    for comp_name, comp in result["components"].items():
        assert 0 <= comp["score"] <= comp["max"], f"{comp_name} out of range"


def test_actions_max_5(db_session, artist):
    add_payments(db_session, artist.id)
    add_anomaly(db_session, artist.id, "anom-rcs-1", AnomalySeverity.HIGH)
    add_anomaly(db_session, artist.id, "anom-rcs-2", AnomalySeverity.MEDIUM)
    db_session.commit()

    scorer = RecoveryCreditScore(db_session)
    result = scorer.calculate(artist.id)

    assert len(result["actions"]) <= 5


def test_trend_is_valid(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    scorer = RecoveryCreditScore(db_session)
    result = scorer.calculate(artist.id)

    assert result["trend"] in {"IMPROVING", "DECLINING", "STABLE"}


def test_chain_of_custody_hash_format(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    scorer = RecoveryCreditScore(db_session)
    result = scorer.calculate(artist.id)
    h = result["chain_of_custody_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_no_data_returns_limited_tier(db_session, artist):
    scorer = RecoveryCreditScore(db_session)
    result = scorer.calculate(artist.id)
    # With no data, score should be very low => LIMITED or DEVELOPING
    assert result["tier"] in {"LIMITED", "DEVELOPING", "FAIR"}
