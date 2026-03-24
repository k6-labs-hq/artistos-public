import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.models.base import Base
from XR7.models.artist import Artist
from XR7.models.payment import Payment
from XR7.modules.payer_health_score import PayerHealthScorer


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
    a = Artist(id="artist-phs", name="PHS Artist")
    db_session.add(a)
    db_session.commit()
    return a


def make_payment(db_session, artist_id, source, amount, days_ago=30):
    pid = f"pay-{source}-{amount}-{days_ago}"
    p = Payment(
        id=pid,
        artist_id=artist_id,
        payment_type="ROYALTY",
        amount=amount,
        received_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
        source=source,
    )
    db_session.add(p)


def test_score_all_returns_required_keys(db_session, artist):
    make_payment(db_session, artist.id, "Spotify", 1000.0)
    db_session.commit()

    scorer = PayerHealthScorer(db_session)
    result = scorer.score_all(artist.id)

    assert "payer_scores" in result
    assert "computed_at" in result
    assert "chain_of_custody_hash" in result


def test_no_payments_returns_empty_payers(db_session, artist):
    scorer = PayerHealthScorer(db_session)
    result = scorer.score_all(artist.id)
    assert result["payer_scores"] == []


def test_score_range_0_to_100(db_session, artist):
    for src in ["Spotify", "Apple Music"]:
        make_payment(db_session, artist.id, src, 500.0)
    db_session.commit()

    scorer = PayerHealthScorer(db_session)
    result = scorer.score_all(artist.id)
    for p in result["payer_scores"]:
        assert 0 <= p["composite_score"] <= 100


def test_sub_scores_within_range(db_session, artist):
    make_payment(db_session, artist.id, "BMI", 1500.0)
    db_session.commit()

    scorer = PayerHealthScorer(db_session)
    result = scorer.score_all(artist.id)
    for p in result["payer_scores"]:
        ss = p["sub_scores"]
        assert 0 <= ss["payment_accuracy"] <= 25
        assert 0 <= ss["redistribution_timing"] <= 20
        assert 0 <= ss["rate_drift"] <= 20
        assert 0 <= ss["dispute_resolution"] <= 20
        assert 0 <= ss["data_quality"] <= 15


def test_risk_tier_assigned(db_session, artist):
    make_payment(db_session, artist.id, "ASCAP", 2000.0)
    db_session.commit()

    scorer = PayerHealthScorer(db_session)
    result = scorer.score_all(artist.id)
    valid_tiers = {"TRUSTED", "RELIABLE", "WATCH", "ELEVATED_RISK", "HIGH_RISK"}
    for p in result["payer_scores"]:
        assert p["risk_tier"] in valid_tiers


def test_chain_of_custody_hash_format(db_session, artist):
    make_payment(db_session, artist.id, "Spotify", 1000.0)
    db_session.commit()

    scorer = PayerHealthScorer(db_session)
    result = scorer.score_all(artist.id)
    h = result["chain_of_custody_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_single_payer_is_scored(db_session, artist):
    make_payment(db_session, artist.id, "Tidal", 300.0, days_ago=60)
    make_payment(db_session, artist.id, "Tidal", 350.0, days_ago=30)
    db_session.commit()

    scorer = PayerHealthScorer(db_session)
    result = scorer.score_all(artist.id)
    payer_names = [p["payer_name"] for p in result["payer_scores"]]
    assert "Tidal" in payer_names
