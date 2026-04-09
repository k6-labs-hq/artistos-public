"""Tests for the split onboarding agent sub-modules.

Covers:
- Pure helper functions in core.py (no DB, no LLM)
- Pure-state async agents that run without a database session
- _intent_from_text and _severity_weight classification helpers
"""

from __future__ import annotations

import asyncio
import hashlib
import json

import pytest

from XR7.agents.onboarding.catalog_agents import (
    ArtistIntentInterpreterAgent,
    AutoTermsAcceptorAgent,
    _intent_from_text,
)
from XR7.agents.onboarding.core import _evidence_hash, _now, _safe_score
from XR7.agents.onboarding.enrichment_agents import (
    ArtistComfortAgent,
    ArtistReadinessScoreAgent,
    AutoFollowUpAgent,
)
from XR7.agents.onboarding.legal_agents import (
    CalibrationAgent,
    DisbursementAgent,
    EscalationAgent,
    _severity_weight,
)
from XR7.agents.onboarding.recovery_agents import (
    BlackBoxExpirationAgent,
    DiscoveryRuleAgent,
    RecoverabilityClassificationAgent,
)
from XR7.agents.state import initial_state

# ---------------------------------------------------------------------------
# Pure helpers — core.py
# ---------------------------------------------------------------------------


def test_safe_score_clamps_high():
    assert _safe_score(1.5) == 1.0


def test_safe_score_clamps_low():
    assert _safe_score(-0.1) == 0.0


def test_safe_score_passthrough():
    assert _safe_score(0.75) == 0.75


def test_now_is_iso_string():
    ts = _now()
    assert "T" in ts and "+" in ts or "Z" in ts or ts.endswith("+00:00")


def test_evidence_hash_deterministic():
    h1 = _evidence_hash("artist-1", "TestAgent", {"key": "val"})
    h2 = _evidence_hash("artist-1", "TestAgent", {"key": "val"})
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex


def test_evidence_hash_differs_for_different_inputs():
    h1 = _evidence_hash("artist-1", "AgentA", {"x": 1})
    h2 = _evidence_hash("artist-1", "AgentB", {"x": 1})
    assert h1 != h2


def test_evidence_hash_matches_manual_sha256():
    payload = {"key": "value", "number": 42}
    raw = json.dumps({"artist_id": "a1", "agent": "Foo", "payload": payload}, sort_keys=True)
    expected = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    assert _evidence_hash("a1", "Foo", payload) == expected


# ---------------------------------------------------------------------------
# catalog_agents — _intent_from_text
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,expected_intent,min_score",
    [
        ("please upload my csv statements", "upload_statements", 0.94),
        ("I have a pdf to upload", "upload_statements", 0.94),
        ("fix my isrc codes", "fix_metadata", 0.90),
        ("metadata looks wrong on my splits", "fix_metadata", 0.90),
        ("what revenue do I expect this quarter", "check_earnings", 0.89),
        ("I want to check my earnings forecast", "check_earnings", 0.89),
        ("I have missing royalty payments", "start_recovery", 0.92),
        ("start a claim for me", "start_recovery", 0.92),
        ("hello there", "clarify", 0.60),
        ("", "clarify", 0.60),
    ],
)
def test_intent_from_text(text, expected_intent, min_score):
    intent, score = _intent_from_text(text)
    assert intent == expected_intent
    assert score >= min_score


# ---------------------------------------------------------------------------
# legal_agents — _severity_weight
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("CRITICAL", 1.0),
        ("HIGH", 0.8),
        ("MEDIUM", 0.55),
        ("LOW", 0.35),
        ("UNKNOWN", 0.35),
        ("", 0.35),
    ],
)
def test_severity_weight(raw, expected):
    assert _severity_weight(raw) == expected


# ---------------------------------------------------------------------------
# Helpers shared by async agent tests
# ---------------------------------------------------------------------------


def _base_state(artist_id: str = "test-artist-onboarding") -> dict:
    s = initial_state(artist_id, "run-test-123")
    s["claims"] = []
    s["anomalies"] = []
    return s


# ---------------------------------------------------------------------------
# ArtistIntentInterpreterAgent — pure state, no DB
# ---------------------------------------------------------------------------


def test_intent_interpreter_upload_path(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-1")
    s = _base_state()
    s["persona_profile"] = {"last_ui_action": "upload_statements", "last_message": ""}
    out = asyncio.run(ArtistIntentInterpreterAgent(s))
    assert out["artist_intent"] == "upload_statements"
    assert out["dashboard_prompt"] is None


def test_intent_interpreter_clarify_path(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-2")
    s = _base_state()
    s["persona_profile"] = {"last_ui_action": "", "last_message": "hi"}
    out = asyncio.run(ArtistIntentInterpreterAgent(s))
    assert out["artist_intent"] == "clarify"
    assert out["dashboard_prompt"] is not None


def test_intent_interpreter_sets_confidence(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-3")
    s = _base_state()
    s["persona_profile"] = {"last_ui_action": "recover royalties", "last_message": ""}
    out = asyncio.run(ArtistIntentInterpreterAgent(s))
    assert out["confidence_scores"]["artist_intent_interpreter"] > 0.0


# ---------------------------------------------------------------------------
# AutoTermsAcceptorAgent — pure state, no DB
# ---------------------------------------------------------------------------


def test_auto_terms_acceptor_sets_onboarding_progress(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-t")
    s = _base_state()
    out = asyncio.run(AutoTermsAcceptorAgent(s))
    assert out["onboarding_progress"]["terms_status"] == "accepted"


def test_auto_terms_acceptor_confidence_is_high(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-t2")
    s = _base_state()
    out = asyncio.run(AutoTermsAcceptorAgent(s))
    assert out["confidence_scores"]["auto_terms_acceptor"] >= 0.95


# ---------------------------------------------------------------------------
# ArtistComfortAgent — pure state, no DB
# ---------------------------------------------------------------------------


def test_artist_comfort_agent_produces_messages(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-c")
    s = _base_state()
    out = asyncio.run(ArtistComfortAgent(s))
    # ArtistComfortAgent sets comfort_messages (list)
    assert "comfort_messages" in out
    assert isinstance(out["comfort_messages"], list)
    assert len(out["comfort_messages"]) >= 2


# ---------------------------------------------------------------------------
# ArtistReadinessScoreAgent — pure state, no DB
# ---------------------------------------------------------------------------


def test_readiness_score_minimal_state(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-r")
    s = _base_state()
    out = asyncio.run(ArtistReadinessScoreAgent(s))
    # ArtistReadinessScoreAgent sets readiness_score (0-100 scaled)
    assert "readiness_score" in out
    assert 0.0 <= out["readiness_score"] <= 100.0


def test_readiness_score_improves_with_more_data(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-r2")
    s_lean = _base_state()
    s_rich = _base_state()
    s_rich["catalog_profile"] = {"metadata_completeness": 0.9}
    s_rich["evidence_hashes"] = ["h1", "h2", "h3"]

    out_lean = asyncio.run(ArtistReadinessScoreAgent(s_lean))
    out_rich = asyncio.run(ArtistReadinessScoreAgent(s_rich))
    assert out_rich["readiness_score"] >= out_lean["readiness_score"]


# ---------------------------------------------------------------------------
# AutoFollowUpAgent — pure state, no DB
# ---------------------------------------------------------------------------


def test_auto_follow_up_no_claims(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-f")
    s = _base_state()
    out = asyncio.run(AutoFollowUpAgent(s))
    assert "follow_up_actions" in out
    assert isinstance(out["follow_up_actions"], list)


# ---------------------------------------------------------------------------
# CalibrationAgent — pure state, no DB
# ---------------------------------------------------------------------------


def test_calibration_agent_runs(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-cal")
    s = _base_state()
    out = asyncio.run(CalibrationAgent(s))
    assert "expected_earnings" in out
    assert "calibration_health" in out["expected_earnings"]
    assert "confidence_scores" in out


# ---------------------------------------------------------------------------
# DisbursementAgent — pure state, no DB
# ---------------------------------------------------------------------------


def test_disbursement_agent_runs(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-dis")
    s = _base_state()
    out = asyncio.run(DisbursementAgent(s))
    # DisbursementAgent sets final_payout (70% of fast_track_claim recoverable)
    assert "final_payout" in out
    assert out["final_payout"] == 0.0  # no fast_track_claim in base state


# ---------------------------------------------------------------------------
# EscalationAgent — pure state, no DB
# ---------------------------------------------------------------------------


def test_escalation_agent_runs(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-esc")
    s = _base_state()
    out = asyncio.run(EscalationAgent(s))
    # EscalationAgent sets next_action; no fast_track_claim → proceeds without escalation
    assert "next_action" in out
    assert out["next_action"] in {"proceed", "human_review", "reflection"}


# ---------------------------------------------------------------------------
# BlackBoxExpirationAgent — pure state (no DB via empty artist_id)
# ---------------------------------------------------------------------------


def test_black_box_expiration_empty_state(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-bbe")
    s = _base_state()
    out = asyncio.run(BlackBoxExpirationAgent(s))
    # Should still return state without crashing
    assert "confidence_scores" in out


# ---------------------------------------------------------------------------
# RecoverabilityClassificationAgent — pure state
# ---------------------------------------------------------------------------


def test_recoverability_classification_empty_anomalies(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-rc")
    s = _base_state()
    out = asyncio.run(RecoverabilityClassificationAgent(s))
    # RecoverabilityClassificationAgent sets recoverability_results
    assert "recoverability_results" in out
    assert isinstance(out["recoverability_results"], list)


# ---------------------------------------------------------------------------
# DiscoveryRuleAgent — pure state, no DB
# ---------------------------------------------------------------------------


def test_discovery_rule_agent_no_anomalies(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding.core._ledger", lambda *a, **k: "hash-dr")
    s = _base_state()
    out = asyncio.run(DiscoveryRuleAgent(s))
    # DiscoveryRuleAgent sets discovery_rule_results
    assert "discovery_rule_results" in out
    assert isinstance(out["discovery_rule_results"], list)


# ---------------------------------------------------------------------------
# Backward-compat shim still exports all symbols
# ---------------------------------------------------------------------------


def test_shim_exports_intent_interpreter():
    from XR7.agents.onboarding_agents import ArtistIntentInterpreterAgent as A  # noqa: F401

    assert callable(A)


def test_shim_exports_legal_authority():
    from XR7.agents.onboarding_agents import LegalAuthorityAgent as L  # noqa: F401

    assert callable(L)


def test_shim_exports_auto_sol_guardian():
    from XR7.agents.onboarding_agents import AutoSOLGuardianAgent as S  # noqa: F401

    assert callable(S)
