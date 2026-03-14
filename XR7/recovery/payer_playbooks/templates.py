from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PayerPlaybookTemplate:
    payer: str
    required_fields: list[str]
    sla_days: int
    escalation_path: list[str]
    packet_instructions: list[str]


DEFAULT_TEMPLATE = PayerPlaybookTemplate(
    payer="Generic Payer",
    required_fields=[
        "artist_id",
        "claim_id",
        "contract_reference",
        "ledger_rows",
        "shortfall_calculation",
        "supporting_statement_files",
    ],
    sla_days=30,
    escalation_path=[
        "Submit dispute portal ticket",
        "Send legal notice to payer operations",
        "Escalate to executive support and rights counsel",
    ],
    packet_instructions=[
        "Attach evidence packet JSON and PDF summary.",
        "Include line-level shortfall citations and contract basis.",
        "Highlight requested amount and response SLA in cover note.",
    ],
)


TEMPLATES_BY_PAYER: dict[str, PayerPlaybookTemplate] = {
    "distrokid": PayerPlaybookTemplate(
        payer="DistroKid",
        required_fields=["release_id", "isrc", "reporting_period", "bank_statement_ref", "evidence_packet_hash"],
        sla_days=14,
        escalation_path=["Open DistroKid support ticket", "Escalate via priority support", "Issue formal label-attorney demand"],
        packet_instructions=["Attach CSV rows for disputed streams.", "Include DSP-specific payout mismatch calculations."],
    ),
    "tunecore": PayerPlaybookTemplate(
        payer="TuneCore",
        required_fields=["release_id", "account_email", "period_start", "period_end", "variance_breakdown"],
        sla_days=21,
        escalation_path=["Open TuneCore support case", "Escalate to account manager", "Issue formal legal follow-up"],
        packet_instructions=["Include statement snapshots and contract terms.", "Call out territory-level payout deltas."],
    ),
    "ascap": PayerPlaybookTemplate(
        payer="ASCAP",
        required_fields=["work_id", "ipi_number", "cue_sheet_refs", "distribution_period", "writer_share_delta"],
        sla_days=45,
        escalation_path=["Submit member service claim", "Escalate to distribution operations", "Escalate to legal liaison"],
        packet_instructions=["Include performance logs and cue sheet references.", "Provide writer/publisher split history."],
    ),
    "bmi": PayerPlaybookTemplate(
        payer="BMI",
        required_fields=["work_id", "cae_ipi", "performance_period", "distribution_statement_ref", "split_sheet"],
        sla_days=45,
        escalation_path=["Open BMI royalty issue", "Escalate through writer relations", "Escalate to counsel"],
        packet_instructions=["Include PRO statement extracts.", "Attach split verification mismatch report."],
    ),
    "spotify": PayerPlaybookTemplate(
        payer="Spotify",
        required_fields=["isrc", "spotify_uri", "territory", "monthly_stream_count", "distribution_partner_ref"],
        sla_days=30,
        escalation_path=["Route through distributor partner manager", "Escalate to Spotify content operations", "Escalate through legal contact"],
        packet_instructions=["Map missing payout to specific URIs and territories.", "Attach evidence of rights ownership."],
    ),
}
