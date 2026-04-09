from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.models.artist import Artist
from XR7.models.base import Base
from XR7.models.payment import Payment
from XR7.modules.earnings_time_machine import EarningsTimeMachine


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
    a = Artist(id="artist-etm", name="ETM Artist")
    db_session.add(a)
    db_session.commit()
    return a


def make_payment(db_session, artist_id, amount, year, month=6):
    p = Payment(
        id=f"pay-{year}-{month}-{amount}",
        artist_id=artist_id,
        payment_type="ROYALTY",
        amount=amount,
        received_at=datetime(year, month, 15, tzinfo=timezone.utc),
        source="Spotify",
    )
    db_session.add(p)


def test_run_returns_required_keys(db_session, artist):
    make_payment(db_session, artist.id, 1000.0, 2022)
    make_payment(db_session, artist.id, 1200.0, 2023)
    db_session.commit()

    etm = EarningsTimeMachine(db_session)
    result = etm.run(artist.id, granularity="yearly")

    assert "time_series" in result
    assert "total_lifetime_leakage" in result
    assert "confidence_band" in result
    assert "summary" in result
    assert "chain_of_custody_hash" in result


def test_confidence_band_order(db_session, artist):
    make_payment(db_session, artist.id, 5000.0, 2022)
    db_session.commit()

    etm = EarningsTimeMachine(db_session)
    result = etm.run(artist.id, granularity="yearly")

    band = result["confidence_band"]
    assert band["low"] <= band["expected"] <= band["high"]


def test_total_leakage_is_positive(db_session, artist):
    make_payment(db_session, artist.id, 3000.0, 2022)
    make_payment(db_session, artist.id, 4000.0, 2023)
    db_session.commit()

    etm = EarningsTimeMachine(db_session)
    result = etm.run(artist.id, granularity="yearly")

    assert result["total_lifetime_leakage"] >= 0


def test_time_series_has_entries(db_session, artist):
    for y in [2021, 2022, 2023]:
        make_payment(db_session, artist.id, 1000.0, y)
    db_session.commit()

    etm = EarningsTimeMachine(db_session)
    result = etm.run(artist.id, granularity="yearly")

    assert len(result["time_series"]) >= 1


def test_no_payments_returns_zero_leakage(db_session, artist):
    etm = EarningsTimeMachine(db_session)
    result = etm.run(artist.id, granularity="yearly")
    assert result["total_lifetime_leakage"] == 0


def test_chain_of_custody_hash_is_hex(db_session, artist):
    make_payment(db_session, artist.id, 1000.0, 2022)
    db_session.commit()

    etm = EarningsTimeMachine(db_session)
    result = etm.run(artist.id, granularity="yearly")

    h = result["chain_of_custody_hash"]
    assert isinstance(h, str)
    assert len(h) == 64  # sha256 hex digest


def test_monthly_granularity(db_session, artist):
    make_payment(db_session, artist.id, 500.0, 2023, month=1)
    make_payment(db_session, artist.id, 700.0, 2023, month=6)
    db_session.commit()

    etm = EarningsTimeMachine(db_session)
    result = etm.run(artist.id, granularity="monthly")
    assert len(result["time_series"]) >= 1
