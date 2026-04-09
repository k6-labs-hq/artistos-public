from __future__ import annotations

from datetime import datetime, timezone

from XR7.recovery.sol_calculator import calculate_sol


def test_calculate_sol_uses_jurisdiction_and_contract_rule():
    result = calculate_sol(
        governing_law_state="UK",
        contract_type="recording",
        infringement_date="2024-01-01T00:00:00+00:00",
        discovery_date=None,
        as_of=datetime(2024, 6, 1, tzinfo=timezone.utc),
    )
    assert result["governing_law_state"] == "UK"
    assert result["contract_type"] == "recording"
    assert result["sol_window_years"] == 6
    assert "Limitation Act" in result["sol_citation_source"]
    assert result["sol_deadline"] is not None


def test_calculate_sol_fallbacks_for_unknown_jurisdiction_and_type():
    result = calculate_sol(
        governing_law_state="ZZ",
        contract_type="unknown",
        infringement_date="2023-01-01T00:00:00+00:00",
        discovery_date="2023-02-01T00:00:00+00:00",
        as_of=datetime(2024, 2, 1, tzinfo=timezone.utc),
    )
    assert result["governing_law_state"] == "USA"
    assert result["contract_type"] == "recording"
    assert result["sol_window_years"] == 3


def test_calculate_sol_status_transitions():
    urgent = calculate_sol(
        governing_law_state="USA",
        contract_type="recording",
        infringement_date="2023-04-15T00:00:00+00:00",
        discovery_date=None,
        as_of=datetime(2026, 2, 1, tzinfo=timezone.utc),
    )
    expired = calculate_sol(
        governing_law_state="USA",
        contract_type="recording",
        infringement_date="2021-01-01T00:00:00+00:00",
        discovery_date=None,
        as_of=datetime(2026, 2, 1, tzinfo=timezone.utc),
    )
    assert urgent["sol_status"] in {"URGENT", "AT_RISK", "OK"}
    assert expired["sol_status"] == "EXPIRED"
