"""Render a claim's evidence packet to a PDF for dispute filing.

The structured evidence-package dict (produced by
ClaimsEvidencePackageBuilder and similar paths) is the canonical artifact;
this module renders it to a PDF that can be emailed to a payer (BMI/ASCAP/
MLC/SoundExchange) as the dispute attachment, downloaded by an operator
for review, or archived alongside the claim record.

Why WeasyPrint over ReportLab: HTML/CSS templates are easier to maintain
than programmatic PDF construction, Jinja2 is already in requirements,
and the system-deps cost (cairo/pango) is one-time at the Docker layer.
See PR #223 / #179 for context.

Usage:
    pdf_bytes = render_evidence_packet_pdf(
        claim={"id": "...", "payer_name": "BMI", ...},
        anomaly={"id": "...", "subtype": "HIGH_RETROACTIVE_PAYMENT_RATIO", ...},
        artist={"name": "Brody Kean"},
    )
    # pdf_bytes is ready to attach to email or write to disk

The function returns bytes, never raises on missing optional fields. Any
required-field-missing case logs and returns an empty cover-page-only PDF
so callers can fall back to manual filing without crashing.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import ChainableUndefined, Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).parent / "templates"
# ChainableUndefined: missing attrs/keys render as empty string instead of
# raising. Operator surface — partial data is preferable to a crashed render
# (a missing payer name is fine; a 500 from the download endpoint is not).
_jinja_env = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
    undefined=ChainableUndefined,
)


def render_evidence_packet_pdf(
    *,
    claim: dict[str, Any] | None = None,
    anomaly: dict[str, Any] | None = None,
    artist: dict[str, Any] | None = None,
    cover_page: dict[str, Any] | None = None,
    signature: str | None = None,
) -> bytes:
    """Render an evidence packet to PDF bytes.

    Args:
        claim: Claim dict (id, payer_name, sol_deadline, etc.). Required fields
            are tolerated as None; the cover page just shows '—' for missing
            fields. Don't fail closed on partial data — this is operator-facing
            and a missing field is preferable to a crashed render.
        anomaly: Anomaly finding dict (subtype, severity, confidence_score,
            estimated_recoverable, description, evidence, etc.).
        artist: Artist dict (at minimum 'name').
        cover_page: Optional cover-page overrides (sol_deadline_warning, etc.).
        signature: Optional cryptographic signature string to include in the
            provenance section.

    Returns:
        PDF bytes ready to attach to email or write to disk. Always returns
        a valid PDF even if input dicts are empty.
    """
    # Defer the WeasyPrint import so import-time at module load is cheap and
    # tests that don't actually render can run without the system libs being
    # installed.
    from weasyprint import HTML  # noqa: PLC0415

    # Pre-populate every key the template references so partial input doesn't
    # crash the render. Missing values resolve to None and the template's
    # `is not none` checks short-circuit cleanly. Without this, a missing
    # field triggers UndefinedError downstream of the `|float` filter.
    _claim_keys = {"id", "payer_name", "sol_deadline", "amount"}
    _anomaly_keys = {
        "id",
        "subtype",
        "rule_id",
        "category",
        "severity",
        "confidence_score",
        "estimated_recoverable",
        "created_at",
        "description",
        "evidence",
    }
    _artist_keys = {"name"}
    _cover_keys = {"sol_deadline", "sol_deadline_warning"}

    claim = {**{k: None for k in _claim_keys}, **(claim or {})}
    anomaly = {**{k: None for k in _anomaly_keys}, **(anomaly or {})}
    artist = {**{k: None for k in _artist_keys}, **(artist or {})}
    cover_page = {**{k: None for k in _cover_keys}, **(cover_page or {})}

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    evidence_json = ""
    if anomaly.get("evidence"):
        try:
            evidence_json = json.dumps(anomaly["evidence"], indent=2, default=str, sort_keys=True)
        except (TypeError, ValueError) as exc:
            logger.warning("Could not JSON-encode anomaly evidence: %s", exc)
            evidence_json = str(anomaly["evidence"])

    template = _jinja_env.get_template("evidence_packet.html")

    # Render once to compute the hash, then render again with the hash baked
    # in. Two-pass keeps the hash genuinely covering the entire visible content
    # except itself (the hash field on the second-pass render holds the
    # first-pass hash).
    first_pass_html = template.render(
        generated_at=generated_at,
        claim=claim,
        anomaly=anomaly,
        artist=artist,
        cover_page=cover_page,
        evidence_json=evidence_json,
        packet_hash="(computing)",
        signature=signature,
    )
    packet_hash = hashlib.sha256(first_pass_html.encode("utf-8")).hexdigest()

    final_html = template.render(
        generated_at=generated_at,
        claim=claim,
        anomaly=anomaly,
        artist=artist,
        cover_page=cover_page,
        evidence_json=evidence_json,
        packet_hash=packet_hash,
        signature=signature,
    )

    pdf_bytes = HTML(string=final_html).write_pdf()
    return pdf_bytes
