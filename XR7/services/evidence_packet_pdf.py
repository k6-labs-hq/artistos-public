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
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import ChainableUndefined, Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).parent / "templates"

# Keys whose values should render as currency. Substring match so things like
# "total_amount", "retroactive_amount", "estimated_recoverable" all hit.
_CURRENCY_KEY_HINTS = ("amount", "recoverable", "payment_total", "total_received")
# Keys whose values should render as percentages. Same substring match.
_RATIO_KEY_HINTS = ("ratio", "percent", "_pct", "rate", "concentration", "share")
# Keys whose values are counts (integer, comma-formatted).
_COUNT_KEY_HINTS = ("count", "payments", "events", "tracks", "rows", "months", "days")


def _humanize_key(key: str) -> str:
    """`retroactive_ratio` → `Retroactive Ratio`. Special-case common abbreviations."""
    parts = key.replace("_", " ").split()
    title = " ".join(p.capitalize() for p in parts)
    return (
        title.replace("Mlc", "MLC")
        .replace("Bmi", "BMI")
        .replace("Ascap", "ASCAP")
        .replace("Sol", "SOL")
        .replace("Pct", "Percentage")
        .replace("Url", "URL")
    )


def _humanize_value(key: str, value: Any) -> str:
    """Format a scalar value based on the heuristic inferred from its key.

    Money keys → `$X,XXX.XX`. Ratio keys (0.7409) → `74.1%`. Count keys → `1,234`.
    Everything else → string-cast. Doesn't try to be clever about ambiguous keys.
    """
    if value is None:
        return "—"
    key_lower = key.lower()
    try:
        if any(h in key_lower for h in _CURRENCY_KEY_HINTS):
            return f"${float(value):,.2f}"
        if any(h in key_lower for h in _RATIO_KEY_HINTS):
            f = float(value)
            # If it's a fraction (0..1.5), render as percentage. If already a
            # whole-number percentage (e.g. 74), render with trailing %.
            return f"{f * 100:.1f}%" if abs(f) <= 1.5 else f"{f:.1f}%"
        if any(h in key_lower for h in _COUNT_KEY_HINTS) and isinstance(value, (int, float)):
            return f"{int(value):,}"
    except (TypeError, ValueError):
        pass
    return str(value)


def _format_evidence_sections(evidence: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Turn the raw evidence dict into a list of presentation sections.

    Each section: `{"title": str | None, "rows": [{"label": str, "value": str}]}`.
    The template iterates sections and renders each as a small key-value table.

    Why per-section: a finding's evidence often has flat scalar values (Summary)
    plus nested dicts like `by_payer.MLC`, plus optional list-of-dicts like
    `top_outliers`. Each subtree reads better with its own header. Without this,
    a flat key-value dump loses the by-payer breakout that's the whole point
    of the HIGH_RETROACTIVE_PAYMENT_RATIO finding.

    Per-rule narrative customization (BMI-specific framing of the same data,
    legal language tuning) is intentionally out of scope here — that's the
    next layer up and lives with the per-payer playbook (#179).
    """
    if not evidence or not isinstance(evidence, dict):
        return []

    sections: list[dict[str, Any]] = []

    # Top-level scalar values → "Summary" table
    summary_rows = [
        {"label": _humanize_key(k), "value": _humanize_value(k, v)}
        for k, v in evidence.items()
        if not isinstance(v, (dict, list))
    ]
    if summary_rows:
        sections.append({"title": "Summary", "rows": summary_rows})

    # `by_payer` is the most common nested structure (HIGH_RETROACTIVE_RATIO).
    # Each payer gets its own table.
    by_payer = evidence.get("by_payer")
    if isinstance(by_payer, dict):
        for payer, metrics in by_payer.items():
            if isinstance(metrics, dict):
                sections.append(
                    {
                        "title": f"Payer: {payer}",
                        "rows": [
                            {"label": _humanize_key(sk), "value": _humanize_value(sk, sv)}
                            for sk, sv in metrics.items()
                            if not isinstance(sv, (dict, list))
                        ],
                    }
                )

    # Other nested dicts (not `by_payer`) → their own section
    for k, v in evidence.items():
        if k == "by_payer":
            continue
        if isinstance(v, dict):
            sub_rows = [
                {"label": _humanize_key(sk), "value": _humanize_value(sk, sv)}
                for sk, sv in v.items()
                if not isinstance(sv, (dict, list))
            ]
            if sub_rows:
                sections.append({"title": _humanize_key(k), "rows": sub_rows})
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            # List of dicts (e.g., top_outliers) — render each as a row group
            for i, item in enumerate(v[:5], start=1):
                sections.append(
                    {
                        "title": f"{_humanize_key(k)} #{i}",
                        "rows": [
                            {"label": _humanize_key(sk), "value": _humanize_value(sk, sv)}
                            for sk, sv in item.items()
                            if not isinstance(sv, (dict, list))
                        ],
                    }
                )
        elif isinstance(v, list) and v:
            # List of scalars (e.g., missing_months) — single row with comma-joined values
            sections.append(
                {
                    "title": _humanize_key(k),
                    "rows": [{"label": "Values", "value": ", ".join(str(x) for x in v[:24])}],
                }
            )

    return sections


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
    line_items: list[dict[str, Any]] | None = None,
    line_items_meta: dict[str, Any] | None = None,
    payer_office: dict[str, Any] | None = None,
    payer_identifiers: dict[str, Any] | None = None,
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
    _claim_keys = {"id", "reference_number", "payer_name", "sol_deadline", "amount"}
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

    evidence_sections = _format_evidence_sections(anomaly.get("evidence"))

    template = _jinja_env.get_template("evidence_packet.html")

    # Render once to compute the hash, then render again with the hash baked
    # in. Two-pass keeps the hash genuinely covering the entire visible content
    # except itself (the hash field on the second-pass render holds the
    # first-pass hash).
    line_items = line_items or []
    line_items_meta = line_items_meta or {}

    render_ctx = {
        "generated_at": generated_at,
        "claim": claim,
        "anomaly": anomaly,
        "artist": artist,
        "cover_page": cover_page,
        "evidence_sections": evidence_sections,
        "line_items": line_items,
        "line_items_meta": line_items_meta,
        "payer_office": payer_office,
        "payer_identifiers": payer_identifiers,
        "signature": signature,
    }

    first_pass_html = template.render(**render_ctx, packet_hash="(computing)")
    packet_hash = hashlib.sha256(first_pass_html.encode("utf-8")).hexdigest()

    final_html = template.render(**render_ctx, packet_hash=packet_hash)

    pdf_bytes = HTML(string=final_html).write_pdf()
    return pdf_bytes
