import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.models.base import Base
from XR7.models.artist import Artist
from XR7.models.payment import Payment
from datetime import datetime, timezone
from XR7.modules.catalog_value_appraiser import CatalogValueAppraiser, VALUATION_DISCLAIMER


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
    a = Artist(id="artist-cva", name="CVA Artist")
    db_session.add(a)
    db_session.commit()
    return a


def add_payments(db_session, artist_id, annual_total=12000.0):
    for month in range(1, 13):
        p = Payment(
            id=f"pay-cva-{month}",
            artist_id=artist_id,
            payment_type="ROYALTY",
            amount=annual_total / 12,
            received_at=datetime(2023, month, 15, tzinfo=timezone.utc),
            source="Spotify",
        )
        db_session.add(p)


def test_appraise_returns_required_keys(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    appraiser = CatalogValueAppraiser(db_session)
    result = appraiser.appraise(artist.id)

    assert "valuation_low" in result
    assert "valuation_expected" in result
    assert "valuation_high" in result
    assert "key_value_drivers" in result
    assert "key_value_risks" in result
    assert "waterfall" in result
    assert "narrative" in result
    assert "disclaimer" in result
    assert "chain_of_custody_hash" in result


def test_valuation_range_is_ordered(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    appraiser = CatalogValueAppraiser(db_session)
    result = appraiser.appraise(artist.id)

    assert result["valuation_low"] <= result["valuation_expected"] <= result["valuation_high"]


def test_valuation_positive_when_income(db_session, artist):
    add_payments(db_session, artist.id, annual_total=24000.0)
    db_session.commit()

    appraiser = CatalogValueAppraiser(db_session)
    result = appraiser.appraise(artist.id)

    assert result["valuation_expected"] > 0


def test_zero_income_returns_zero_valuation(db_session, artist):
    appraiser = CatalogValueAppraiser(db_session)
    result = appraiser.appraise(artist.id)
    assert result["valuation_expected"] == 0


def test_key_drivers_count(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    appraiser = CatalogValueAppraiser(db_session)
    result = appraiser.appraise(artist.id)

    assert len(result["key_value_drivers"]) == 3


def test_key_risks_count(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    appraiser = CatalogValueAppraiser(db_session)
    result = appraiser.appraise(artist.id)

    assert len(result["key_value_risks"]) == 3


def test_disclaimer_in_result(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    appraiser = CatalogValueAppraiser(db_session)
    result = appraiser.appraise(artist.id)

    assert result["disclaimer"] == VALUATION_DISCLAIMER


def test_waterfall_has_entries(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    appraiser = CatalogValueAppraiser(db_session)
    result = appraiser.appraise(artist.id)

    assert len(result["waterfall"]) >= 1


def test_chain_of_custody_hash_format(db_session, artist):
    add_payments(db_session, artist.id)
    db_session.commit()

    appraiser = CatalogValueAppraiser(db_session)
    result = appraiser.appraise(artist.id)
    h = result["chain_of_custody_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_high_health_score_increases_valuation(db_session, artist):
    add_payments(db_session, artist.id, annual_total=12000.0)
    db_session.commit()

    appraiser = CatalogValueAppraiser(db_session)
    r_low = appraiser.appraise(artist.id, catalog_health_score=0.2)
    r_high = appraiser.appraise(artist.id, catalog_health_score=0.9)

    assert r_high["valuation_expected"] >= r_low["valuation_expected"]
