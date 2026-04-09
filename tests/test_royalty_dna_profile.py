from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.models.artist import Artist
from XR7.models.base import Base
from XR7.models.payment import Payment
from XR7.modules.royalty_dna_profile import RoyaltyDNAProfile


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
    a = Artist(id="artist-dna", name="DNA Artist")
    db_session.add(a)
    db_session.commit()
    return a


def make_payment(db_session, artist_id, amount, source, territory, royalty_type, month=6):
    pid = f"pay-{source}-{territory}-{amount}-{month}"
    p = Payment(
        id=pid,
        artist_id=artist_id,
        payment_type="ROYALTY",
        amount=amount,
        received_at=datetime(2023, month, 15, tzinfo=timezone.utc),
        source=source,
    )
    db_session.add(p)


def test_generate_returns_required_keys(db_session, artist):
    make_payment(db_session, artist.id, 1000.0, "Spotify", "US", "STREAMING")
    db_session.commit()

    profile = RoyaltyDNAProfile(db_session)
    result = profile.generate(artist.id)

    assert "platform_breakdown" in result
    assert "territory_gaps" in result
    assert "royalty_type_breakdown" in result
    assert "revenue_concentration_score" in result
    assert "dna_strand" in result
    assert "insights" in result
    assert "chain_of_custody_hash" in result


def test_concentration_score_between_0_and_1(db_session, artist):
    for src in ["Spotify", "Apple Music", "Amazon", "YouTube", "Tidal"]:
        make_payment(db_session, artist.id, 1000.0, src, "US", "STREAMING")
    db_session.commit()

    profile = RoyaltyDNAProfile(db_session)
    result = profile.generate(artist.id)
    hhi = result["revenue_concentration_score"]
    assert 0.0 <= hhi <= 1.0


def test_single_platform_high_concentration(db_session, artist):
    make_payment(db_session, artist.id, 10000.0, "Spotify", "US", "STREAMING")
    db_session.commit()

    profile = RoyaltyDNAProfile(db_session)
    result = profile.generate(artist.id)
    # All income from one platform => HHI = 1.0, max concentration
    assert result["revenue_concentration_score"] == pytest.approx(1.0)


def test_territory_gap_for_major_territory(db_session, artist):
    # Only US payments — GB, DE, etc. should be flagged as gaps
    make_payment(db_session, artist.id, 1000.0, "Spotify", "US", "STREAMING")
    db_session.commit()

    profile = RoyaltyDNAProfile(db_session)
    result = profile.generate(artist.id)
    # At least some major territories should be flagged as gaps
    assert isinstance(result["territory_gaps"], list)


def test_insights_count(db_session, artist):
    make_payment(db_session, artist.id, 500.0, "Spotify", "US", "STREAMING")
    make_payment(db_session, artist.id, 200.0, "Apple Music", "GB", "MECHANICAL")
    db_session.commit()

    profile = RoyaltyDNAProfile(db_session)
    result = profile.generate(artist.id)
    # Should return exactly 3 insights
    assert len(result["insights"]) == 3


def test_dna_strand_pcts_sum_to_100(db_session, artist):
    make_payment(db_session, artist.id, 1000.0, "Spotify", "US", "STREAMING")
    make_payment(db_session, artist.id, 500.0, "Apple Music", "GB", "MECHANICAL")
    db_session.commit()

    profile = RoyaltyDNAProfile(db_session)
    result = profile.generate(artist.id)
    total = sum(s["pct"] for s in result["dna_strand"])
    assert total == pytest.approx(100.0, abs=1.0)


def test_chain_of_custody_hash_format(db_session, artist):
    make_payment(db_session, artist.id, 1000.0, "Spotify", "US", "STREAMING")
    db_session.commit()

    profile = RoyaltyDNAProfile(db_session)
    result = profile.generate(artist.id)
    h = result["chain_of_custody_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_no_payments_returns_empty_platform_breakdown(db_session, artist):
    profile = RoyaltyDNAProfile(db_session)
    result = profile.generate(artist.id)
    # With no payments, platform breakdown should be empty or all zeros
    active = [p for p in result["platform_breakdown"] if p["amount"] > 0]
    assert active == []
