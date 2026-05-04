"""PayerOffice records + lookup helper.

Pins the seeded BMI offices and the resolution behavior of
get_payer_office (named lookup, default fallback, unknown payer).
"""

from __future__ import annotations

from tests.conftest import TestSession
from XR7.models.payer_office import PayerOffice
from XR7.recovery.payer_config import get_payer_office


def test_bmi_six_offices_seeded():
    db = TestSession()
    try:
        offices = db.query(PayerOffice).filter(PayerOffice.payer_id == "BMI").all()
        names = sorted(o.name for o in offices)
        assert names == ["Atlanta", "Austin", "London", "Los Angeles", "Nashville", "New York"]
    finally:
        db.close()


def test_bmi_nashville_is_default():
    db = TestSession()
    try:
        defaults = (
            db.query(PayerOffice)
            .filter(PayerOffice.payer_id == "BMI", PayerOffice.is_default.is_(True))
            .all()
        )
        assert len(defaults) == 1
        assert defaults[0].name == "Nashville"
        assert defaults[0].submission_email == "nashville@bmi.com"
    finally:
        db.close()


def test_get_payer_office_default_for_bmi():
    db = TestSession()
    try:
        office = get_payer_office(db, "BMI")
        assert office is not None
        assert office.name == "Nashville"
        assert office.submission_email == "nashville@bmi.com"
    finally:
        db.close()


def test_get_payer_office_named_lookup():
    db = TestSession()
    try:
        office = get_payer_office(db, "BMI", "New York")
        assert office is not None
        assert office.submission_email == "newyork@bmi.com"
    finally:
        db.close()


def test_get_payer_office_named_lookup_case_insensitive():
    db = TestSession()
    try:
        office = get_payer_office(db, "BMI", "los angeles")
        assert office is not None
        assert office.submission_email == "losangeles@bmi.com"
    finally:
        db.close()


def test_get_payer_office_unknown_payer_returns_none():
    db = TestSession()
    try:
        assert get_payer_office(db, "PRS") is None
    finally:
        db.close()


def test_get_payer_office_unknown_office_returns_none():
    db = TestSession()
    try:
        assert get_payer_office(db, "BMI", "Mars") is None
    finally:
        db.close()


def test_get_payer_office_payer_id_case_insensitive():
    db = TestSession()
    try:
        office = get_payer_office(db, "bmi")
        assert office is not None
        assert office.name == "Nashville"
    finally:
        db.close()
