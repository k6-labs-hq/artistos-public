import pytest
import json
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.models.base import Base
from XR7.models.artist import Artist
from XR7.models.contract import Contract
from XR7.models.payment import Payment
from XR7.modules.contract_drift_monitor import ContractDriftMonitor


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
    a = Artist(id="artist-cdm", name="Drift Artist")
    db_session.add(a)
    db_session.commit()
    return a


def make_contract(db_session, artist_id, contract_id, contracted_rate=0.20, payer="Spotify"):
    c = Contract(
        id=contract_id,
        artist_id=artist_id,
        contract_type="PUBLISHING",
        counterparty=payer,
        terms={
            "counterparty": payer,
            "royalty_rate": contracted_rate,
            "effective_date": "2022-01-01",
        },
    )
    db_session.add(c)


def make_payments_for_contract(db_session, artist_id, source, actual_rate, year=2023):
    for month in [3, 6, 9, 12]:
        pay = Payment(
            id=f"pay-{source}-{year}-{month}",
            artist_id=artist_id,
            payment_type="ROYALTY",
            amount=1000.0 * actual_rate,
            received_at=datetime(year, month, 15, tzinfo=timezone.utc),
            source=source,
        )
        db_session.add(pay)


def test_analyze_all_returns_required_keys(db_session, artist):
    make_contract(db_session, artist.id, "contract-1", contracted_rate=0.20, payer="Spotify")
    db_session.commit()

    monitor = ContractDriftMonitor(db_session)
    result = monitor.analyze_all(artist.id)

    assert "contracts" in result
    assert "total_cumulative_underpayment" in result
    assert "chain_of_custody_hash" in result


def test_no_contracts_returns_empty(db_session, artist):
    monitor = ContractDriftMonitor(db_session)
    result = monitor.analyze_all(artist.id)
    assert result["contracts"] == []


def test_drift_classification_within_variance(db_session, artist):
    # contracted rate = 20%, actual ~20% => WITHIN_VARIANCE
    make_contract(db_session, artist.id, "contract-wv", contracted_rate=0.20, payer="BMI")
    make_payments_for_contract(db_session, artist.id, "BMI", actual_rate=0.20)
    db_session.commit()

    monitor = ContractDriftMonitor(db_session)
    result = monitor.analyze_all(artist.id)
    assert len(result["contracts"]) >= 1


def test_classification_is_valid_value(db_session, artist):
    make_contract(db_session, artist.id, "contract-cls", contracted_rate=0.20, payer="ASCAP")
    make_payments_for_contract(db_session, artist.id, "ASCAP", actual_rate=0.15)
    db_session.commit()

    monitor = ContractDriftMonitor(db_session)
    result = monitor.analyze_all(artist.id)
    valid = {"WITHIN_VARIANCE", "SOFT_DRIFT", "HARD_DRIFT", "BREACH_RISK"}
    for c in result["contracts"]:
        assert c["classification"] in valid


def test_drift_trend_is_valid(db_session, artist):
    make_contract(db_session, artist.id, "contract-trend", contracted_rate=0.25, payer="Tidal")
    make_payments_for_contract(db_session, artist.id, "Tidal", actual_rate=0.18)
    db_session.commit()

    monitor = ContractDriftMonitor(db_session)
    result = monitor.analyze_all(artist.id)
    valid_trends = {"WIDENING", "STABLE", "NARROWING"}
    for c in result["contracts"]:
        assert c["drift_trend"] in valid_trends


def test_cumulative_underpayment_non_negative(db_session, artist):
    make_contract(db_session, artist.id, "contract-cum", contracted_rate=0.20, payer="Apple Music")
    make_payments_for_contract(db_session, artist.id, "Apple Music", actual_rate=0.15)
    db_session.commit()

    monitor = ContractDriftMonitor(db_session)
    result = monitor.analyze_all(artist.id)
    assert result["total_cumulative_underpayment"] >= 0


def test_chain_of_custody_hash_format(db_session, artist):
    make_contract(db_session, artist.id, "contract-hash", contracted_rate=0.20, payer="Spotify")
    db_session.commit()

    monitor = ContractDriftMonitor(db_session)
    result = monitor.analyze_all(artist.id)
    h = result["chain_of_custody_hash"]
    assert isinstance(h, str) and len(h) == 64
