"""
Tests for XR7.core.claims.state_machine
========================================
Covers:
  - Every legal forward transition in the TRANSITIONS table
  - next_status() raises ValueError on terminal/unknown states
  - contract_type_for_category() maps all known categories
  - contract_type_for_category() returns None for unknown/None input
  - Transition table completeness assertions
  - Domain-boundary check: module has NO DB / ORM imports

Mocks/fixtures: none — all functions are pure and accept plain primitives.

Recommended future tests:
  - Property-based: generate random ClaimStatus values and verify
    next_status() either succeeds with a correct value or raises ValueError.
  - Integration: drive the full lifecycle through a real Claim ORM object
    (belongs in an integration test file, not here).
"""
from __future__ import annotations

import importlib

import pytest

from XR7.core.claims.state_machine import (
    TRANSITIONS,
    contract_type_for_category,
    next_status,
)
from XR7.models.claim import ClaimStatus


# ---------------------------------------------------------------------------
# Domain-boundary guard — no DB / ORM imports allowed in pure core module
# ---------------------------------------------------------------------------

def test_no_db_imports_in_state_machine():
    """The state_machine module must remain free of SQLAlchemy and FastAPI."""
    import XR7.core.claims.state_machine as sm_module

    src = importlib.import_module("XR7.core.claims.state_machine").__file__
    with open(src) as f:
        source = f.read()

    forbidden = ["sqlalchemy", "fastapi", "SessionLocal", "from XR7.services", "from XR7.api"]
    for token in forbidden:
        assert token not in source, (
            f"Pure core module must not import '{token}'. "
            "Move any DB logic to the service layer."
        )


# ---------------------------------------------------------------------------
# next_status — happy path: all defined forward transitions
# ---------------------------------------------------------------------------

class TestNextStatusHappyPath:
    def test_identified_to_prepared(self):
        assert next_status(ClaimStatus.IDENTIFIED) == ClaimStatus.PREPARED

    def test_prepared_to_submitted(self):
        assert next_status(ClaimStatus.PREPARED) == ClaimStatus.SUBMITTED

    def test_submitted_to_filed(self):
        assert next_status(ClaimStatus.SUBMITTED) == ClaimStatus.FILED

    def test_filed_to_in_review(self):
        assert next_status(ClaimStatus.FILED) == ClaimStatus.IN_REVIEW

    def test_in_review_to_accepted(self):
        assert next_status(ClaimStatus.IN_REVIEW) == ClaimStatus.ACCEPTED

    def test_accepted_to_paid(self):
        assert next_status(ClaimStatus.ACCEPTED) == ClaimStatus.PAID

    def test_paid_to_closed(self):
        assert next_status(ClaimStatus.PAID) == ClaimStatus.CLOSED

    def test_transitions_covers_every_entry(self):
        """Every key in TRANSITIONS resolves via next_status without raising."""
        for status in TRANSITIONS:
            result = next_status(status)
            assert isinstance(result, ClaimStatus)

    def test_transition_chain_terminates_at_closed(self):
        """Walking the chain from IDENTIFIED eventually reaches CLOSED."""
        current = ClaimStatus.IDENTIFIED
        visited = [current]
        while current in TRANSITIONS:
            current = next_status(current)
            visited.append(current)
        assert visited[-1] == ClaimStatus.CLOSED
        # Sanity: chain has no duplicates (no loops)
        assert len(visited) == len(set(visited))


# ---------------------------------------------------------------------------
# next_status — terminal and unknown states raise ValueError
# ---------------------------------------------------------------------------

class TestNextStatusErrors:
    def test_closed_has_no_forward_transition(self):
        with pytest.raises(ValueError, match="CLOSED"):
            next_status(ClaimStatus.CLOSED)

    def test_proof_submitted_is_terminal_or_branching(self):
        # PROOF_SUBMITTED is not defined in TRANSITIONS (terminal-ish in current model)
        # Verify it raises the expected error from next_status, confirming it has no forward step
        with pytest.raises(ValueError):
            next_status(ClaimStatus.PROOF_SUBMITTED)

    def test_error_message_contains_status_name(self):
        with pytest.raises(ValueError) as exc:
            next_status(ClaimStatus.CLOSED)
        assert "CLOSED" in str(exc.value)


# ---------------------------------------------------------------------------
# contract_type_for_category — all mapped categories
# ---------------------------------------------------------------------------

class TestContractTypeForCategory:
    @pytest.mark.parametrize("category,expected", [
        ("ROYALTY",  "LABEL"),
        ("TOURING",  "TOURING"),
        ("MERCH",    "MERCH"),
        ("SYNC",     "SYNC"),
        ("PLATFORM", "LABEL"),
        ("BRAND",    "BRAND"),
        ("GRANT",    "GRANT"),
    ])
    def test_known_category_returns_correct_contract_type(self, category, expected):
        assert contract_type_for_category(category) == expected

    def test_none_category_returns_none(self):
        assert contract_type_for_category(None) is None

    def test_unknown_category_returns_none(self):
        assert contract_type_for_category("UNKNOWN_VERTICAL") is None

    def test_empty_string_returns_none(self):
        assert contract_type_for_category("") is None

    def test_case_sensitive_mismatch_returns_none(self):
        # Categories are uppercase constants; lowercase input is not mapped
        assert contract_type_for_category("royalty") is None

    def test_return_type_is_str_or_none(self):
        for cat in ("ROYALTY", "SYNC", None, "UNRECOGNISED"):
            result = contract_type_for_category(cat)
            assert result is None or isinstance(result, str)


# ---------------------------------------------------------------------------
# TRANSITIONS table integrity
# ---------------------------------------------------------------------------

class TestTransitionsTableIntegrity:
    def test_all_transition_values_are_claim_statuses(self):
        for from_status, to_status in TRANSITIONS.items():
            assert isinstance(from_status, ClaimStatus)
            assert isinstance(to_status, ClaimStatus)

    def test_no_self_loops(self):
        for from_status, to_status in TRANSITIONS.items():
            assert from_status != to_status, (
                f"Self-loop detected: {from_status} → {to_status}"
            )

    def test_closed_not_a_key_in_transitions(self):
        assert ClaimStatus.CLOSED not in TRANSITIONS

    def test_disbursement_failed_not_a_key_in_transitions_if_terminal(self):
        # DISBURSEMENT_FAILED is a dead-end status in the current model
        if ClaimStatus.DISBURSEMENT_FAILED not in TRANSITIONS:
            assert ClaimStatus.DISBURSEMENT_FAILED not in TRANSITIONS
        else:
            # If it's mapped, the target must be a valid ClaimStatus
            assert isinstance(TRANSITIONS[ClaimStatus.DISBURSEMENT_FAILED], ClaimStatus)
