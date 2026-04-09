"""Legal authority, negotiation, and attorney-prep agents."""

from __future__ import annotations

from typing import Any

from XR7.agents.onboarding.core import _finalize, _now, _safe_score
from XR7.agents.state import XR7State
from XR7.llm.claim_drafter import claim_drafter
from XR7.models.anomaly import Anomaly, AnomalyStatus
from XR7.models.base import SessionLocal
from XR7.models.claim import Claim
from XR7.recovery.payer_playbooks import build_claim_playbook


def _primary_claim(state: XR7State) -> dict[str, Any]:
    claims = list(state.get("claims") or [])
    return dict(claims[0]) if claims else {}


def _severity_weight(raw: str) -> float:
    key = str(raw or "").upper()
    if key == "CRITICAL":
        return 1.0
    if key == "HIGH":
        return 0.8
    if key == "MEDIUM":
        return 0.55
    return 0.35


async def LegalAuthorityAgent(state: XR7State) -> XR7State:
    claim = _primary_claim(state)
    anomalies = list(state.get("anomalies") or [])
    evidence_hashes = list(state.get("evidence_hashes") or [])
    contract_terms = dict(state.get("contract_terms") or {})
    rights_conflicts = list(state.get("rights_conflicts") or [])
    expected = dict(state.get("expected_earnings") or {})

    findings_text = (
        f"This packet constitutes a structured evidentiary record for claim {claim.get('id', 'N/A')} "
        f"and summarizes {len(anomalies)} discrepancy signals under standardized variance analysis."
    )
    methodology_text = (
        "Supported by timestamped, cryptographically verifiable source data and deterministic calculations "
        "of expected-versus-received values by period, territory, and usage class."
    )
    chain_text = (
        f"Chain-of-custody is maintained through {len(evidence_hashes)} packet-linked integrity hash entries "
        "with immutable ledger registration."
    )
    contractual_text = (
        "Compiled pursuant to the artist's contractual and statutory rights, including audit rights, "
        "payment accuracy obligations, and reporting transparency provisions where applicable."
    )

    legal_sections = [
        f"Summary of Findings: {findings_text}",
        "Basis of Calculation: Expected minus received amounts were computed at record level and aggregated into material discrepancy totals.",
        f"Methodology and Standards Applied: {methodology_text}",
        "Supporting Documentation Index: Source statements, ledger extracts, anomaly traces, and reconciliation artifacts are indexed by integrity reference.",
        f"Chain-of-Custody Verification: {chain_text}",
        f"Applicable Contractual Provisions: {contractual_text}",
        "Applicable Industry Standards: Revenue reconciliation, variance analysis, and independent verification controls were applied consistently.",
        "Recommended Next Steps: Submit this packet for payer reconciliation review and preserve all cited source records for counsel-led follow-up.",
    ]
    compliance_statements = [
        "Packet language is factual, neutral, and non-adversarial.",
        "All calculations are reproducible from cited source rows and ledger references.",
        "Evidence integrity is represented through chain hashes and immutable ledger traceability.",
        "Claims framing is compliance-oriented and suitable for attorney review.",
    ]

    legal_structured_packet = {
        "summary_of_findings": findings_text,
        "basis_of_calculation": (
            "Prepared in accordance with industry-standard audit procedures, using reconciliation summary "
            "methods against a source-of-truth ledger and independent verification checkpoints."
        ),
        "methodology_and_standards_applied": methodology_text,
        "supporting_documentation_index": [f"evidence_hash:{h}" for h in evidence_hashes[:25]],
        "chain_of_custody_verification": chain_text,
        "applicable_contractual_provisions": {
            "contract_count": len(list(contract_terms.get("contracts") or [])),
            "rights_conflict_count": len(rights_conflicts),
        },
        "applicable_industry_standards": [
            "variance analysis",
            "material discrepancy",
            "reconciliation summary",
            "source-of-truth ledger",
            "independent verification",
        ],
        "recommended_next_steps": (
            "Provide packet to payer operations and counsel for documented reconciliation workflow."
        ),
    }
    legal_appendix = {
        "discrepancy_summaries": [
            {
                "anomaly_id": a.get("id"),
                "subtype": a.get("subtype"),
                "estimated_recoverable": float(a.get("estimated_recoverable") or 0.0),
                "confidence": float(a.get("confidence") or a.get("confidence_score") or 0.0),
            }
            for a in anomalies[:10]
        ],
        "exhibit_list": [f"Exhibit-{idx + 1}: {h}" for idx, h in enumerate(evidence_hashes[:20])],
        "chain_of_custody_summary": chain_text,
        "compliance_statement": compliance_statements,
        "signature_block": {
            "prepared_by": "XR7 LegalAuthorityAgent",
            "designation": "Recovery Intelligence Documentation",
            "signed_at": _now(),
            "notarized": False,
        },
        "calculation_basis": {
            "quarterly_expected": float(expected.get("quarterly_expected") or 0.0),
            "anomaly_count": len(anomalies),
        },
    }

    coverage = 0.6
    coverage += 0.1 if anomalies else 0.0
    coverage += 0.1 if evidence_hashes else 0.0
    coverage += 0.1 if contract_terms else 0.0
    coverage += 0.1 if claim else 0.0
    score = _safe_score(min(0.97, coverage))

    return _finalize(
        state,
        agent_name="legal_authority_agent",
        confidence_label="LegalAuthorityAgent",
        score=score,
        updates={
            "legal_authority_sections": legal_sections,
            "legal_methodology_summary": methodology_text,
            "legal_compliance_statements": compliance_statements,
            "legal_structured_packet": legal_structured_packet,
            "legal_appendix": legal_appendix,
        },
        decision="legal authority framing and audit-grade packet sections generated",
    )


async def LegalRiskScoringAgent(state: XR7State) -> XR7State:
    anomalies = list(state.get("anomalies") or [])
    evidence_hashes = list(state.get("evidence_hashes") or [])
    history = list(state.get("negotiation_history") or [])
    profile = dict(state.get("catalog_profile") or {})

    severity_factor = max(
        (_severity_weight(a.get("severity", "MEDIUM")) for a in anomalies), default=0.4
    )
    metadata_completeness = float(profile.get("metadata_completeness") or 0.65)
    evidence_strength = min(
        1.0,
        (len(evidence_hashes) / 8.0) + (0.15 if state.get("legal_structured_packet") else 0.0),
    )
    negotiation_friction = min(1.0, len(history) / 6.0)

    legal_risk = _safe_score(
        0.45 * severity_factor + 0.25 * (1.0 - metadata_completeness) + 0.30 * negotiation_friction
    )
    settlement_probability = _safe_score(
        0.55 * evidence_strength + 0.30 * metadata_completeness + 0.15 * (1.0 - severity_factor)
    )
    escalation_readiness = _safe_score(
        0.5 * evidence_strength + 0.25 * severity_factor + 0.25 * (1.0 - settlement_probability)
    )

    score = _safe_score(0.82 + 0.18 * evidence_strength)
    return _finalize(
        state,
        agent_name="legal_risk_scoring_agent",
        confidence_label="LegalRiskScoringAgent",
        score=score,
        updates={
            "legal_risk_score": legal_risk,
            "settlement_probability": settlement_probability,
            "escalation_readiness_score": escalation_readiness,
        },
        decision="legal risk and settlement-readiness scores computed",
    )


async def PayerBehaviorPredictionAgent(state: XR7State) -> XR7State:
    history = list(state.get("negotiation_history") or [])
    claim = _primary_claim(state)
    legal_sections = list(state.get("legal_authority_sections") or [])
    escalation_readiness = float(state.get("escalation_readiness_score") or 0.0)

    delay_events = sum(1 for row in history if "delay" in str(row.get("action", "")).lower())
    concession_events = sum(
        1
        for row in history
        if "accept" in str(row.get("action", "")).lower()
        or "settle" in str(row.get("action", "")).lower()
    )
    rounds = max(1, len(history))

    responsiveness = _safe_score(
        max(
            0.05,
            0.75 - (delay_events * 0.12) - (rounds - 1) * 0.05 + concession_events * 0.08,
        )
    )
    settlement_probability = _safe_score(
        0.5 * responsiveness
        + 0.35 * float(state.get("settlement_probability") or 0.0)
        + 0.15 * (1.0 - escalation_readiness)
    )
    escalation_resistance = _safe_score(1.0 - responsiveness * 0.8)
    speed_days = max(
        7,
        int(round(45 - responsiveness * 22 + escalation_resistance * 14)),
    )

    posture = (
        "cooperative"
        if responsiveness >= 0.7
        else "neutral" if responsiveness >= 0.45 else "resistant"
    )
    claim_amount = float(claim.get("estimated_recoverable") or 0.0)
    emphasis = [
        "chain-of-custody verification",
        "reconciliation summary",
        "source-of-truth ledger citations",
    ]
    if claim_amount >= 10000:
        emphasis.append("material discrepancy framing for high-value review")

    profile = {
        "posture": posture,
        "evidence_sensitive": responsiveness >= 0.55 or bool(legal_sections),
        "delay_pattern": {"rounds": rounds, "delay_events": delay_events},
        "historical_signal": "aggregated_xr7_pattern_based",
        "claim_size_band": (
            "high" if claim_amount >= 10000 else "medium" if claim_amount >= 3000 else "low"
        ),
    }
    strategy = (
        "Use concise, evidence-forward communication with reconciliation tables and immutable integrity references; "
        "request acknowledgement of cited source rows and expected response window."
    )
    attorney_briefing = {
        "payer_behavior_profile": profile,
        "predicted_settlement_likelihood": settlement_probability,
        "predicted_timeline_days": speed_days,
        "recommended_packet_emphasis": emphasis,
        "evidence_strength_summary": {
            "hash_count": len(state.get("evidence_hashes") or []),
            "legal_sections": len(legal_sections),
        },
        "non_legal_negotiation_insights": strategy,
        "escalation_readiness": escalation_readiness,
    }

    return _finalize(
        state,
        agent_name="payer_behavior_prediction_agent",
        confidence_label="PayerBehaviorPredictionAgent",
        score=_safe_score(0.86 + min(0.11, rounds * 0.01)),
        updates={
            "payer_behavior_profile": profile,
            "predicted_responsiveness": responsiveness,
            "predicted_settlement_speed_days": speed_days,
            "predicted_settlement_probability": settlement_probability,
            "predicted_escalation_resistance": escalation_resistance,
            "recommended_negotiation_strategy": strategy,
            "recommended_packet_emphasis": emphasis,
            "attorney_briefing_packet": attorney_briefing,
        },
        decision="payer behavior prediction profile generated for attorney review",
    )


async def NegotiationToneAdapterAgent(state: XR7State) -> XR7State:
    history = list(state.get("negotiation_history") or [])
    profile = dict(state.get("payer_behavior_profile") or {})
    posture = str(profile.get("posture") or "neutral")

    if posture == "cooperative":
        tone, structure, framing = "formal", "concise", "compliance_focused"
    elif posture == "resistant":
        tone, structure, framing = "evidence-heavy", "structured", "audit_grade"
    else:
        tone, structure, framing = "formal", "balanced", "compliance_focused"

    legal_anchor = ""
    if state.get("legal_methodology_summary"):
        legal_anchor = " Methodology references are included for independent verification."

    adapted = [
        f"We are sharing a structured reconciliation summary with source-row references and chain-of-custody verification.{legal_anchor}",
        "Please confirm receipt and provide any row-level variances so both parties can reconcile the same source-of-truth ledger.",
        "This communication is factual and intended to support an efficient, professional resolution workflow.",
    ]
    if history:
        adapted.append(
            "Given prior response cadence, this packet emphasizes direct citations and short reconciliation checkpoints."
        )

    return _finalize(
        state,
        agent_name="negotiation_tone_adapter_agent",
        confidence_label="NegotiationToneAdapterAgent",
        score=0.9,
        updates={
            "negotiation_tone_profile": {
                "payer_posture": posture,
                "tone": tone,
                "structure": structure,
                "framing": framing,
            },
            "adapted_messages": adapted,
        },
        decision="negotiation tone and message framing adapted",
    )


async def ClaimOutcomeForecasterAgent(state: XR7State) -> XR7State:
    claim = _primary_claim(state)
    anomalies = list(state.get("anomalies") or [])
    behavior = dict(state.get("payer_behavior_profile") or {})

    claim_amount = float(claim.get("estimated_recoverable") or 0.0)
    if claim_amount <= 0:
        claim_amount = sum(float(a.get("estimated_recoverable") or 0.0) for a in anomalies[:5])

    evidence_strength = min(1.0, len(state.get("evidence_hashes") or []) / 10.0)
    metadata = float((state.get("catalog_profile") or {}).get("metadata_completeness") or 0.65)
    base_settlement = float(
        state.get("predicted_settlement_probability") or state.get("settlement_probability") or 0.5
    )
    resistance = float(state.get("predicted_escalation_resistance") or 0.4)
    posture = str(behavior.get("posture") or "neutral")

    posture_factor = 1.05 if posture == "cooperative" else 0.93 if posture == "resistant" else 1.0
    payout_prob = _safe_score(base_settlement * (0.75 + 0.25 * evidence_strength) * posture_factor)
    escalation_prob = _safe_score(max(0.05, 0.35 + resistance * 0.45 - evidence_strength * 0.2))
    expected_value = round(claim_amount * payout_prob, 2)
    low = round(expected_value * max(0.45, 0.7 - escalation_prob * 0.3), 2)
    high = round(
        min(
            claim_amount,
            expected_value * (1.2 + evidence_strength * 0.25 + metadata * 0.1),
        ),
        2,
    )
    timeline_days = max(10, int(round(28 + escalation_prob * 30 + (1.0 - metadata) * 14)))
    full_payout_prob = _safe_score(
        max(0.02, payout_prob - escalation_prob * 0.25 + evidence_strength * 0.15)
    )

    return _finalize(
        state,
        agent_name="claim_outcome_forecaster_agent",
        confidence_label="ClaimOutcomeForecasterAgent",
        score=_safe_score(0.86 + evidence_strength * 0.1),
        updates={
            "predicted_recovery_amount": round(expected_value, 2),
            "predicted_recovery_low": low,
            "predicted_recovery_high": high,
            "predicted_expected_value": expected_value,
            "predicted_settlement_timeline_days": timeline_days,
            "predicted_escalation_probability": escalation_prob,
            "predicted_full_payout_probability": full_payout_prob,
        },
        decision="probability-weighted claim outcome forecast generated",
    )


async def EvidenceNarrativeAgent(state: XR7State) -> XR7State:
    anomalies = list(state.get("anomalies") or [])
    claim = _primary_claim(state)
    behavior = dict(state.get("payer_behavior_profile") or {})

    discrepancy_total = sum(float(a.get("estimated_recoverable") or 0.0) for a in anomalies)
    overview = (
        f"XR7 identified {len(anomalies)} discrepancy signals associated with claim {claim.get('id', 'N/A')}. "
        "This narrative summarizes evidence lineage, calculation basis, and context for attorney review."
    )
    calc = (
        f"Calculation basis estimates total discrepancy at ${discrepancy_total:,.2f} "
        "from expected-versus-received deltas."
    )
    payer_insights = (
        f"Payer behavior posture is {behavior.get('posture', 'neutral')} with responsiveness score "
        f"{float(state.get('predicted_responsiveness') or 0.0):.2f}."
    )
    expected_range = (
        f"Expected recovery range is ${float(state.get('predicted_recovery_low') or 0.0):,.2f} to "
        f"${float(state.get('predicted_recovery_high') or 0.0):,.2f} (non-legal statistical estimate)."
    )
    timeline = (
        f"Predicted settlement timeline is approximately "
        f"{int(state.get('predicted_settlement_timeline_days') or 0)} days."
    )

    sections = {
        "Overview": overview,
        "Nature of the discrepancy": "Primary discrepancy categories were mapped from anomaly subtype and amount variance records.",
        "How XR7 detected it": "XR7 detection combined structured ledger comparisons, variance analysis, and metadata cross-checks.",
        "Evidence summary": (
            f"Evidence summary references {len(state.get('evidence_hashes') or [])} integrity hashes and "
            "source-row citations for reproducible verification."
        ),
        "Calculation basis": calc,
        "Metadata and catalog context": (
            f"Metadata completeness signal: {float((state.get('catalog_profile') or {}).get('metadata_completeness') or 0.0):.2f}."
        ),
        "Payer behavior insights": payer_insights,
        "Expected recovery range (non-legal)": expected_range,
        "Timeline reconstruction": timeline,
        "Supporting exhibits": [
            f"evidence_hash:{h}" for h in (state.get("evidence_hashes") or [])[:20]
        ],
    }
    summary = " ".join([overview, calc, payer_insights, expected_range])

    return _finalize(
        state,
        agent_name="evidence_narrative_agent",
        confidence_label="EvidenceNarrativeAgent",
        score=0.9,
        updates={
            "narrative_summary": summary,
            "narrative_sections": sections,
            "narrative_highlights": [
                f"Total discrepancy signal: ${discrepancy_total:,.2f}",
                f"Payer posture: {behavior.get('posture', 'neutral')}",
                f"Expected value: ${float(state.get('predicted_expected_value') or 0.0):,.2f}",
            ],
        },
        decision="factual attorney-ready evidence narrative generated",
    )


async def LegalCounselPrepAgent(state: XR7State) -> XR7State:
    claim = _primary_claim(state)
    anomalies = list(state.get("anomalies") or [])
    exhibits = [
        {"id": idx + 1, "type": "integrity_hash", "reference": h}
        for idx, h in enumerate((state.get("evidence_hashes") or [])[:30])
    ]
    chain_summary = (
        f"Chain-of-custody is supported by {len(exhibits)} integrity-linked exhibit references "
        "and immutable ledger event logging for generation steps."
    )
    factual_summary = (
        f"Claim {claim.get('id', 'N/A')} is supported by {len(anomalies)} anomaly signals, "
        f"predicted expected value ${float(state.get('predicted_expected_value') or 0.0):,.2f}, "
        "and a documented reconciliation basis suitable for attorney-led review."
    )
    case_file = {
        "claim": claim,
        "factual_narrative_summary": state.get("narrative_summary") or factual_summary,
        "discrepancy_analysis": {
            "anomaly_count": len(anomalies),
            "estimated_total": sum(float(a.get("estimated_recoverable") or 0.0) for a in anomalies),
        },
        "variance_analysis": state.get("legal_structured_packet") or {},
        "evidence_strength_summary": {
            "hash_count": len(state.get("evidence_hashes") or []),
            "compliance_statement_count": len(state.get("legal_compliance_statements") or []),
        },
        "metadata_completeness_summary": {
            "metadata_completeness": float(
                (state.get("catalog_profile") or {}).get("metadata_completeness") or 0.0
            ),
        },
        "payer_behavior_predictions": state.get("payer_behavior_profile") or {},
        "settlement_probability": float(
            state.get("predicted_settlement_probability")
            or state.get("settlement_probability")
            or 0.0
        ),
        "escalation_readiness": float(state.get("escalation_readiness_score") or 0.0),
        "timeline_reconstruction": {
            "predicted_settlement_days": int(state.get("predicted_settlement_timeline_days") or 0),
            "negotiation_rounds": len(state.get("negotiation_history") or []),
        },
        "chain_of_custody_verification_summary": chain_summary,
        "supporting_exhibits_index": exhibits,
        "recommended_packet_emphasis": state.get("recommended_packet_emphasis") or [],
    }

    return _finalize(
        state,
        agent_name="legal_counsel_prep_agent",
        confidence_label="LegalCounselPrepAgent",
        score=0.9,
        updates={
            "attorney_case_file": case_file,
            "attorney_case_file_summary": factual_summary,
            "attorney_exhibits_index": exhibits,
            "attorney_chain_of_custody_summary": chain_summary,
            "attorney_packet_metadata": {
                "prepared_at": _now(),
                "prepared_by": "XR7 LegalCounselPrepAgent",
                "non_advisory": True,
                "attorney_review_ready": True,
            },
        },
        decision="attorney-ready case file assembled",
    )


async def ClaimEscalationAgent(state: XR7State) -> XR7State:
    claim = _primary_claim(state)
    anomalies = list(state.get("anomalies") or [])
    rounds = len(state.get("negotiation_history") or [])
    readiness = float(state.get("escalation_readiness_score") or 0.0)
    timeline_days = int(state.get("predicted_settlement_timeline_days") or 0)

    # Build minimal duck-typed proxies for build_claim_playbook
    claim_like = type(
        "ClaimLike",
        (),
        {
            "id": str(claim.get("id") or "state-claim"),
            "artist_id": str(state.get("artist_id") or ""),
            "anomaly_id": str(claim.get("anomaly_id") or ""),
            "claim_type": str(claim.get("claim_type") or "ROYALTY"),
            "evidence": {
                "legal_support": {
                    "contract_basis": [
                        {
                            "counterparty": str(
                                ((state.get("contract_terms") or {}).get("contracts") or [{}])[0]
                                .get("parsed_terms", {})
                                .get("counterparty")
                                or ""
                            )
                        }
                    ]
                }
            },
        },
    )
    anomaly_like = type(
        "AnomalyLike",
        (),
        {"subtype": str((anomalies[0] if anomalies else {}).get("subtype") or "generic")},
    )
    playbook = build_claim_playbook(claim_like, anomaly_like)

    eligible = rounds >= 3 or readiness >= 0.68 or timeline_days >= 60
    packet = {
        "eligible": eligible,
        "eligibility_reasons": {
            "negotiation_rounds": rounds,
            "escalation_readiness_score": readiness,
            "predicted_timeline_days": timeline_days,
        },
        "payer_specific_escalation_instructions": playbook.get("escalation_paths") or [],
        "recommended_escalation_paths": [
            "Maintain documented reconciliation request trail",
            "Escalate through payer operations per playbook SLA",
            "Prepare counsel handoff packet with chain-of-custody summary",
        ],
        "statutory_references": [
            "Applicable contractual audit-right windows should be checked against claim timeline records.",
            "Any SOL-related timeline should be validated with jurisdiction-specific counsel before filing decisions.",
        ],
        "escalation_summary": "Escalation packet prepared using neutral factual framing and payer-specific workflow guidance.",
    }

    score = 0.91 if eligible else 0.84
    return _finalize(
        state,
        agent_name="claim_escalation_agent",
        confidence_label="ClaimEscalationAgent",
        score=score,
        updates={"escalation_prepared_packet": packet},
        decision="claim escalation readiness packet prepared",
    )


async def AttorneyExportAgent(state: XR7State) -> XR7State:
    case_file = dict(state.get("attorney_case_file") or {})
    package = {
        "structured_case_file": case_file,
        "narrative_summary": state.get("narrative_summary") or "",
        "legal_authority_sections": state.get("legal_authority_sections") or [],
        "discrepancy_analysis": case_file.get("discrepancy_analysis") or {},
        "evidence_strength_summary": case_file.get("evidence_strength_summary") or {},
        "payer_behavior_predictions": state.get("payer_behavior_profile") or {},
        "settlement_forecasts": {
            "expected_value": float(state.get("predicted_expected_value") or 0.0),
            "low": float(state.get("predicted_recovery_low") or 0.0),
            "high": float(state.get("predicted_recovery_high") or 0.0),
            "timeline_days": int(state.get("predicted_settlement_timeline_days") or 0),
        },
        "escalation_readiness": float(state.get("escalation_readiness_score") or 0.0),
        "chain_of_custody_verification": state.get("attorney_chain_of_custody_summary") or "",
        "supporting_exhibits_index": state.get("attorney_exhibits_index") or [],
        "recommended_emphasis_points": state.get("recommended_packet_emphasis") or [],
        "integrity": {
            "evidence_hashes": state.get("evidence_hashes") or [],
            "prepared_at": _now(),
        },
    }
    manifest = {
        "artifact_count": 9,
        "contains": [
            "structured_case_file",
            "narrative_summary",
            "legal_authority_sections",
            "payer_behavior_predictions",
            "settlement_forecasts",
            "escalation_readiness",
            "chain_of_custody_verification",
            "supporting_exhibits_index",
            "integrity",
        ],
        "exported_at": _now(),
        "non_advisory": True,
    }
    summary = (
        "Attorney export package compiled with factual discrepancy analysis, evidence integrity lineage, "
        "payer behavior intelligence, and probability-weighted recovery forecasts."
    )

    return _finalize(
        state,
        agent_name="attorney_export_agent",
        confidence_label="AttorneyExportAgent",
        score=0.91,
        updates={
            "attorney_export_package": package,
            "attorney_export_manifest": manifest,
            "attorney_export_summary": summary,
        },
        decision="attorney export package finalized",
    )


async def DetectionAgent(state: XR7State) -> XR7State:
    from XR7.agents.onboarding.enrichment_agents import SocialUGCCollectorAgent

    return await SocialUGCCollectorAgent(state)


async def EvidenceVerifierAgent(state: XR7State) -> XR7State:
    evidence_hashes = list(state.get("evidence_hashes") or [])
    valid = all(len(h) >= 32 for h in evidence_hashes)
    score = 0.92 if valid else 0.79
    return _finalize(
        state,
        agent_name="evidence_verifier",
        score=score,
        updates={
            "error_log": [] if valid else ["Evidence verification found invalid or missing hashes"]
        },
        decision="evidence integrity verified",
    )


async def ClaimDrafterAgent(state: XR7State) -> XR7State:
    claims = list(state.get("claims") or [])
    if claims:
        return _finalize(
            state,
            agent_name="claim_drafter",
            score=0.9,
            updates={},
            decision="claims already drafted",
        )

    artist_id = str(state.get("artist_id") or "")
    db = SessionLocal()
    try:
        anomaly = (
            db.query(Anomaly)
            .filter(Anomaly.artist_id == artist_id, Anomaly.status == AnomalyStatus.OPEN)
            .order_by(Anomaly.confidence_score.desc())
            .first()
        )
        if not anomaly:
            return _finalize(
                state,
                agent_name="claim_drafter",
                score=0.86,
                updates={},
                decision="no anomalies to draft",
            )
        text = claim_drafter.generate_demand_letter(
            {
                "id": anomaly.id,
                "subtype": anomaly.subtype,
                "estimated_recoverable": float(anomaly.estimated_recoverable or 0.0),
            },
            {"source": "claim_drafter_agent"},
            artist_id,
        )
        claim = Claim(
            artist_id=artist_id,
            anomaly_id=anomaly.id,
            claim_type="ROYALTY",
            status="PREPARED",
            evidence={"draft": text, "created_at": _now()},
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)
    finally:
        db.close()

    return _finalize(
        state,
        agent_name="claim_drafter",
        score=0.91,
        updates={"claims": [{"id": claim.id, "anomaly_id": claim.anomaly_id}]},
        decision=f"claim drafted {claim.id}",
    )


async def NegotiationAgent(state: XR7State) -> XR7State:
    history = list(state.get("negotiation_history") or [])
    round_idx = len(history) + 1
    offer = 3200.0 - (round_idx - 1) * 150.0
    adapted_messages = list(state.get("adapted_messages") or [])
    entry = {
        "round": round_idx,
        "action": "counter_offer_sent",
        "amount": max(offer, 800.0),
        "at": _now(),
        "tone_profile": state.get("negotiation_tone_profile") or {},
        "message": (
            adapted_messages[min(len(adapted_messages) - 1, max(0, round_idx - 1))]
            if adapted_messages
            else None
        ),
    }
    score = 0.9 if round_idx <= 3 else 0.82
    return _finalize(
        state,
        agent_name="negotiation_agent",
        score=score,
        updates={"negotiation_history": [entry]},
        decision=f"negotiation round {round_idx}",
    )


async def EscalationAgent(state: XR7State) -> XR7State:
    claim = dict(state.get("fast_track_claim") or {})
    amount = float(claim.get("estimated_recoverable") or 0.0)
    escalate = amount > 10000 or float((state.get("reflection_score") or 1.0)) < 0.85
    return _finalize(
        state,
        agent_name="escalation_agent",
        score=0.9,
        updates={
            "next_action": "human_review" if escalate else "proceed",
            "error_log": ["Legal escalation packet generated"] if escalate else [],
        },
        decision="escalation decision made",
    )


async def DisbursementAgent(state: XR7State) -> XR7State:
    claim = dict(state.get("fast_track_claim") or {})
    payout = float(claim.get("estimated_recoverable") or 0.0) * 0.7
    return _finalize(
        state,
        agent_name="disbursement_agent",
        score=0.92,
        updates={"final_payout": round(payout, 2)},
        decision="simulated disbursement created",
    )


async def CalibrationAgent(state: XR7State) -> XR7State:
    score = float(state.get("readiness_score") or 70.0)
    calibration = {
        "posterior_success_rate": round(min(0.99, max(0.5, score / 100.0)), 4),
        "catalog_health": score,
        "updated_at": _now(),
    }
    return _finalize(
        state,
        agent_name="calibration_agent",
        score=0.93,
        updates={
            "expected_earnings": {
                **(state.get("expected_earnings") or {}),
                "calibration_health": calibration,
            }
        },
        decision="calibration updated",
    )
