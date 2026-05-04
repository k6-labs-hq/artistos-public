"""GET/PUT /artists/{id}/payer-routing — captures the artist's PRO
affiliations + (if BMI) regional office. Drives dispute filing routing.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from tests.conftest import TestSession
from XR7.api.app import app
from XR7.models.artist import Artist

client = TestClient(app)


@pytest.fixture
def fresh_artist():
    db = TestSession()
    artist_id = str(uuid.uuid4())
    db.add(
        Artist(
            id=artist_id,
            name="Routing Test Artist",
            email="routing@example.com",
            country_code="US",
            created_at=datetime.now(timezone.utc),
        )
    )
    db.commit()
    db.close()
    yield artist_id
    db = TestSession()
    db.query(Artist).filter(Artist.id == artist_id).delete()
    db.commit()
    db.close()


def test_get_routing_initially_null(fresh_artist):
    resp = client.get(f"/artists/{fresh_artist}/payer-routing")
    assert resp.status_code == 200
    body = resp.json()
    assert body["pro_affiliations"] is None
    assert body["bmi_office_name"] is None


def test_put_routing_with_bmi_default_office(fresh_artist):
    resp = client.put(
        f"/artists/{fresh_artist}/payer-routing",
        json={"pro_affiliations": ["BMI", "MLC"], "bmi_office_name": "Nashville"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["pro_affiliations"] == ["BMI", "MLC"]
    assert body["bmi_office_name"] == "Nashville"


def test_put_routing_normalizes_canonical_uppercase(fresh_artist):
    resp = client.put(
        f"/artists/{fresh_artist}/payer-routing",
        json={"pro_affiliations": ["bmi", "ascap"], "bmi_office_name": None},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["pro_affiliations"] == ["ASCAP", "BMI"]


def test_put_routing_unknown_office_400(fresh_artist):
    resp = client.put(
        f"/artists/{fresh_artist}/payer-routing",
        json={"pro_affiliations": ["BMI"], "bmi_office_name": "Antarctica"},
    )
    assert resp.status_code == 400


def test_put_routing_office_case_insensitive(fresh_artist):
    resp = client.put(
        f"/artists/{fresh_artist}/payer-routing",
        json={"pro_affiliations": ["BMI"], "bmi_office_name": "los angeles"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["bmi_office_name"] == "Los Angeles"


def test_put_routing_clearing_office_works(fresh_artist):
    # First set
    client.put(
        f"/artists/{fresh_artist}/payer-routing",
        json={"pro_affiliations": ["BMI"], "bmi_office_name": "New York"},
    )
    # Then clear (e.g. artist switches off BMI)
    resp = client.put(
        f"/artists/{fresh_artist}/payer-routing",
        json={"pro_affiliations": ["MLC"], "bmi_office_name": None},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["pro_affiliations"] == ["MLC"]
    assert body["bmi_office_name"] is None
