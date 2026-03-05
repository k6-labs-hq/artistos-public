import pytest
from datetime import datetime
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.models.base import Base
from XR7.models.artist import Artist
from XR7.models.contract import Contract, ContractType
from XR7.models.event import Event, EventType
from XR7.models.payment import Payment, PaymentType
from XR7.graph.rights_graph import RightsGraph
from XR7.earnings.engine import EarningsEngine


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
def engine_instance():
    rg = RightsGraph()
    return EarningsEngine(rg)


def test_calculate_expected_earnings_gross(engine_instance):
    event = {"quantity": 500, "unit_value": 0.004, "currency": "USD"}
    result = engine_instance.calculate_expected_earnings(event, [])
    assert result["gross"] == pytest.approx(2.0)
    assert result["net"] == pytest.approx(2.0)
    assert result["currency"] == "USD"


def test_calculate_expected_earnings_with_contract(engine_instance):
    contract = MagicMock()
    contract.id = "contract-1"
    contract.contract_type = ContractType.LABEL
    contract.terms = {"artist_split": 0.5, "recoupment_balance": 0.0}
    event = {"quantity": 1000, "unit_value": 1.0, "currency": "USD"}
    result = engine_instance.calculate_expected_earnings(event, [contract])
    assert result["gross"] == pytest.approx(1000.0)
    assert result["net"] == pytest.approx(500.0)
    assert len(result["breakdown"]) == 1
    assert result["breakdown"][0]["artist_split"] == 0.5


def test_gross_equals_quantity_times_unit_value(engine_instance):
    event = {"quantity": 250, "unit_value": 0.0035, "currency": "USD"}
    result = engine_instance.calculate_expected_earnings(event, [])
    assert result["gross"] == pytest.approx(250 * 0.0035)


def test_get_earnings_summary_structure(db_session, engine_instance):
    artist = Artist(id="artist-summary", name="Summary Artist")
    db_session.add(artist)
    db_session.commit()
    summary = engine_instance.get_earnings_summary("artist-summary", db_session)
    assert "total_expected" in summary
    assert "total_received" in summary
    assert "variance" in summary
    assert "by_type" in summary
    assert summary["artist_id"] == "artist-summary"
