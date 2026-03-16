from __future__ import annotations

import asyncio

from XR7.agents.onboarding_agents import (
    AttorneyExportAgent,
    ClaimEscalationAgent,
    ClaimOutcomeForecasterAgent,
    EvidenceNarrativeAgent,
    LegalAuthorityAgent,
    LegalCounselPrepAgent,
    LegalRiskScoringAgent,
    NegotiationToneAdapterAgent,
    PayerBehaviorPredictionAgent,
)
from XR7.agents.state import initial_state


def _state() -> dict:
    s = initial_state("artist-legal-stack", "run-legal-stack")
    s["claims"] = [{"id": "claim-1", "anomaly_id": "a-1", "estimated_recoverable": 7500.0, "claim_type": "ROYALTY"}]
    s["anomalies"] = [
        {"id": "a-1", "subtype": "soundcloud_unreported_usage", "severity": "HIGH", "estimated_recoverable": 4200.0, "confidence": 0.91},
        {"id": "a-2", "subtype": "metadata_mismatch", "severity": "MEDIUM", "estimated_recoverable": 1100.0, "confidence": 0.82},
    ]
    s["evidence_hashes"] = ["hash-1", "hash-2", "hash-3"]
    s["catalog_profile"] = {"metadata_completeness": 0.72}
    s["contract_terms"] = {"contracts": [{"parsed_terms": {"counterparty": "SoundCloud"}}]}
    return s


def test_legal_authority_generates_structured_sections(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding_agents._ledger", lambda *args, **kwargs: "ledger-hash")
    out = asyncio.run(LegalAuthorityAgent(_state()))
    assert len(out["legal_authority_sections"]) >= 8
    assert "structured evidentiary record" in " ".join(out["legal_authority_sections"]).lower()
    assert "chain-of-custody" in out["legal_structured_packet"]["chain_of_custody_verification"].lower()
    assert out["confidence_scores"]["LegalAuthorityAgent"] >= 0.85


def test_escalation_reflection_behavior_when_not_eligible(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding_agents._ledger", lambda *args, **kwargs: "ledger-hash")
    s = _state()
    s["negotiation_history"] = []
    s["escalation_readiness_score"] = 0.2
    s["predicted_settlement_timeline_days"] = 12
    out = asyncio.run(ClaimEscalationAgent(s))
    assert "escalation_prepared_packet" in out
    assert out["confidence_scores"]["ClaimEscalationAgent"] <= 0.85
    assert out["next_action"] == "reflection"


def test_prediction_and_export_agents_update_state(monkeypatch):
    monkeypatch.setattr("XR7.agents.onboarding_agents._ledger", lambda *args, **kwargs: "ledger-hash")
    s = _state()
    s = {**s, **asyncio.run(LegalAuthorityAgent(s))}
    s = {**s, **asyncio.run(LegalRiskScoringAgent(s))}
    s = {**s, **asyncio.run(PayerBehaviorPredictionAgent(s))}
    s = {**s, **asyncio.run(NegotiationToneAdapterAgent(s))}
    s = {**s, **asyncio.run(ClaimOutcomeForecasterAgent(s))}
    s = {**s, **asyncio.run(EvidenceNarrativeAgent(s))}
    s = {**s, **asyncio.run(LegalCounselPrepAgent(s))}
    out = asyncio.run(AttorneyExportAgent(s))

    assert out["attorney_export_package"]["settlement_forecasts"]["expected_value"] >= 0.0
    assert out["attorney_export_manifest"]["artifact_count"] >= 9
    assert out["confidence_scores"]["AttorneyExportAgent"] >= 0.85
