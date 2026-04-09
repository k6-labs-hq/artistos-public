"""
Tests for XR7.core.workflow.variance_rows
==========================================
Covers:
  - event_to_variance_row() output shape and field types
  - event_to_variance_row() expected_payout = payout * EXPECTED_PAYOUT_UPLIFT
  - event_to_variance_row() handles zero quantity and unit_value
  - event_to_universal_row() output shape and all required fields present
  - event_to_universal_row() optional fields default correctly
  - event_to_universal_row() passes through all supplied values unchanged
  - EXPECTED_PAYOUT_UPLIFT constant is stable
  - Domain-boundary check: no DB / ORM imports

Mocks/fixtures: none — all pure transform functions.

Recommended future tests:
  - Property-based: quantity >= 0, unit_value >= 0 → payout and expected_payout >= 0.
  - Round-trip: feed event_to_variance_row output into a mock VarianceDetectionService.
  - Feed event_to_universal_row output into a mock UniversalEventService.persist_many().
  - Test negative values (edge case for refunds / adjustments).
"""
from __future__ import annotations

import pytest

from XR7.core.workflow.variance_rows import (
    EXPECTED_PAYOUT_UPLIFT,
    event_to_universal_row,
    event_to_variance_row,
)


# ---------------------------------------------------------------------------
# Domain-boundary guard
# ---------------------------------------------------------------------------

def test_no_db_imports_in_variance_rows():
    import XR7.core.workflow.variance_rows as mod

    with open(mod.__file__) as f:
        source = f.read()

    for token in ["sqlalchemy", "SessionLocal", "from XR7.services", "from XR7.api"]:
        assert token not in source, f"Pure core module must not import '{token}'"


# ---------------------------------------------------------------------------
# EXPECTED_PAYOUT_UPLIFT constant
# ---------------------------------------------------------------------------

def test_uplift_constant_value():
    assert EXPECTED_PAYOUT_UPLIFT == pytest.approx(1.2)


def test_uplift_is_float():
    assert isinstance(EXPECTED_PAYOUT_UPLIFT, float)


# ---------------------------------------------------------------------------
# event_to_variance_row
# ---------------------------------------------------------------------------

class TestEventToVarianceRow:
    def test_returns_dict(self):
        assert isinstance(event_to_variance_row(100, 0.005), dict)

    def test_payout_equals_quantity_times_unit_value(self):
        row = event_to_variance_row(1000, 0.004)
        assert row["payout"] == pytest.approx(4.0)

    def test_expected_payout_uses_uplift(self):
        row = event_to_variance_row(1000, 0.004)
        assert row["expected_payout"] == pytest.approx(4.0 * EXPECTED_PAYOUT_UPLIFT)

    def test_streams_matches_quantity(self):
        row = event_to_variance_row(5000, 0.003)
        assert row["streams"] == pytest.approx(5000)

    def test_reported_usage_matches_quantity(self):
        row = event_to_variance_row(250, 0.01)
        assert row["reported_usage"] == pytest.approx(250)

    def test_has_registration_is_true(self):
        row = event_to_variance_row(100, 0.005)
        assert row["has_registration"] is True

    def test_zero_quantity_produces_zero_payout(self):
        row = event_to_variance_row(0, 0.005)
        assert row["payout"] == pytest.approx(0.0)
        assert row["expected_payout"] == pytest.approx(0.0)

    def test_zero_unit_value_produces_zero_payout(self):
        row = event_to_variance_row(1000, 0.0)
        assert row["payout"] == pytest.approx(0.0)

    def test_fractional_values_are_preserved(self):
        row = event_to_variance_row(333, 0.00333)
        assert row["payout"] == pytest.approx(333 * 0.00333, rel=1e-6)

    def test_required_keys_present(self):
        row = event_to_variance_row(100, 0.003)
        required = {"streams", "payout", "expected_payout", "has_registration", "reported_usage"}
        assert required.issubset(row.keys())

    def test_large_values_do_not_overflow(self):
        row = event_to_variance_row(1_000_000_000, 0.01)
        assert row["payout"] == pytest.approx(10_000_000.0)
        assert row["expected_payout"] == pytest.approx(10_000_000.0 * 1.2)


# ---------------------------------------------------------------------------
# event_to_universal_row
# ---------------------------------------------------------------------------

class TestEventToUniversalRow:
    def _make(self, **overrides):
        defaults = dict(
            artist_id="artist-001",
            source_name="spotify",
            event_type="stream",
            amount=4.00,
            quantity=1000.0,
            unit_value=0.004,
        )
        defaults.update(overrides)
        return event_to_universal_row(**defaults)

    def test_returns_dict(self):
        assert isinstance(self._make(), dict)

    def test_artist_id_passed_through(self):
        row = self._make(artist_id="art-xyz")
        assert row["artist_id"] == "art-xyz"

    def test_source_type_is_event(self):
        assert self._make()["source_type"] == "event"

    def test_source_name_passed_through(self):
        assert self._make(source_name="apple_music")["source_name"] == "apple_music"

    def test_record_type_is_event(self):
        assert self._make()["record_type"] == "EVENT"

    def test_event_type_passed_through(self):
        assert self._make(event_type="download")["event_type"] == "download"

    def test_amount_passed_through(self):
        row = self._make(amount=12.50)
        assert row["amount"] == pytest.approx(12.50)

    def test_quantity_passed_through(self):
        row = self._make(quantity=2500.0)
        assert row["quantity"] == pytest.approx(2500.0)

    def test_unit_value_passed_through(self):
        row = self._make(unit_value=0.0035)
        assert row["unit_value"] == pytest.approx(0.0035)

    def test_currency_defaults_to_usd(self):
        assert self._make()["currency"] == "USD"

    def test_currency_can_be_overridden(self):
        assert self._make(currency="GBP")["currency"] == "GBP"

    def test_territory_defaults_to_none(self):
        assert self._make()["territory"] is None

    def test_territory_can_be_set(self):
        assert self._make(territory="US")["territory"] == "US"

    def test_work_id_is_none(self):
        assert self._make()["work_id"] is None

    def test_work_title_is_none(self):
        assert self._make()["work_title"] is None

    def test_isrc_is_none(self):
        assert self._make()["isrc"] is None

    def test_metadata_contains_event_id_key(self):
        row = self._make()
        assert "event_id" in row["metadata"]

    def test_event_id_propagated_to_metadata(self):
        row = event_to_universal_row(
            artist_id="a",
            source_name="deezer",
            event_type="stream",
            amount=1.0,
            quantity=100.0,
            unit_value=0.01,
            event_id="evt-9999",
        )
        assert row["metadata"]["event_id"] == "evt-9999"

    def test_event_id_none_when_not_supplied(self):
        row = self._make()
        assert row["metadata"]["event_id"] is None

    def test_all_required_keys_present(self):
        row = self._make()
        required = {
            "artist_id", "source_type", "source_name", "record_type",
            "event_type", "amount", "quantity", "unit_value", "currency",
            "territory", "work_id", "work_title", "isrc", "metadata",
        }
        assert required.issubset(row.keys())
