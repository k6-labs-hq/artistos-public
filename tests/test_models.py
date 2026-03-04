import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from arcos7.models.base import Base
from arcos7.models.artist import Artist, ArtistSchema
from arcos7.models.work import Work, WorkType
from arcos7.models.event import Event, EventType
from arcos7.models.contract import Contract, ContractType


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_create_artist(db_session):
    artist = Artist(
        id="artist-1",
        name="Test Artist",
        ipi_number="00123456789",
        stage_names=["TA", "The Artist"],
    )
    db_session.add(artist)
    db_session.commit()
    result = db_session.query(Artist).filter(Artist.id == "artist-1").first()
    assert result is not None
    assert result.name == "Test Artist"
    assert result.ipi_number == "00123456789"


def test_create_work_with_artist(db_session):
    artist = Artist(id="artist-2", name="Work Artist")
    db_session.add(artist)
    db_session.commit()
    work = Work(
        id="work-1",
        title="My Song",
        isrc="USABC1234567",
        work_type=WorkType.RECORDING,
        artist_id="artist-2",
    )
    db_session.add(work)
    db_session.commit()
    result = db_session.query(Work).filter(Work.id == "work-1").first()
    assert result is not None
    assert result.title == "My Song"
    assert result.artist_id == "artist-2"
    assert result.work_type == WorkType.RECORDING


def test_enum_values_work(db_session):
    artist = Artist(id="artist-3", name="Enum Test Artist")
    db_session.add(artist)
    db_session.commit()
    from datetime import datetime
    event = Event(
        id="event-1",
        event_type=EventType.STREAM,
        artist_id="artist-3",
        timestamp=datetime.utcnow(),
        quantity=1000,
        unit_value=0.004,
        currency="USD",
    )
    db_session.add(event)
    db_session.commit()
    result = db_session.query(Event).filter(Event.id == "event-1").first()
    assert result.event_type == EventType.STREAM
    assert result.quantity == 1000


def test_pydantic_schema_validates(db_session):
    from datetime import datetime
    artist = Artist(id="artist-4", name="Schema Artist", created_at=datetime.utcnow())
    db_session.add(artist)
    db_session.commit()
    schema = ArtistSchema.model_validate(artist)
    assert schema.id == "artist-4"
    assert schema.name == "Schema Artist"
