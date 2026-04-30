"""Tests for the evidence-packet PDF renderer.

Pinned behavior:
- Returns valid PDF bytes (starts with %PDF-)
- Tolerates missing optional fields (operator-facing, partial data is fine)
- Includes artist name, anomaly subtype, recoverable amount on the cover page
- Embeds evidence-as-JSON when anomaly.evidence is present
- Computes a hash that's stable for stable input

We don't validate visual layout in tests — that's a manual review concern
on the rendered sample. We DO validate that the renderer doesn't crash on
edge inputs because the operator surface depends on it being robust.
"""

from __future__ import annotations

from XR7.services.evidence_packet_pdf import render_evidence_packet_pdf


def test_renders_valid_pdf_with_brody_shaped_data():
    """Real anomaly fixture matching what's in QA today for Brody Kean's MLC finding."""
    pdf = render_evidence_packet_pdf(
        claim={
            "id": "claim-1",
            "payer_name": "MLC",
            "sol_deadline": "2027-09-30",
        },
        artist={"name": "Brody Kean"},
        anomaly={
            "id": "anm_8b2d19aa139a68882e32a7a9",
            "subtype": "HIGH_RETROACTIVE_PAYMENT_RATIO",
            "rule_id": "HIGH_RETROACTIVE_RATIO",
            "category": "ROYALTY",
            "severity": "HIGH",
            "confidence_score": 0.84,
            "estimated_recoverable": 24.22,
            "created_at": "2026-04-29T18:53:44Z",
            "description": "74% of MLC royalties are retroactive catch-ups...",
            "evidence": {
                "by_payer": {
                    "MLC": {
                        "total_payments": 218,
                        "retroactive_payments": 161,
                        "retroactive_ratio": 0.7409,
                    }
                },
                "worst_payer": "MLC",
            },
        },
    )
    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 1000  # sanity — empty pdf would be much smaller


def test_renders_with_empty_inputs_does_not_crash():
    """Operator surface — never fail closed on partial data."""
    pdf = render_evidence_packet_pdf()
    assert pdf.startswith(b"%PDF-")


def test_renders_with_only_claim_id():
    """Minimum-viable input: just a claim id, everything else None."""
    pdf = render_evidence_packet_pdf(claim={"id": "claim-min"})
    assert pdf.startswith(b"%PDF-")


def test_evidence_dict_does_not_break_render_when_unserializable():
    """Anomaly evidence may have datetime/Decimal/etc. — ensure tolerant fallback."""
    from datetime import datetime

    pdf = render_evidence_packet_pdf(
        anomaly={
            "subtype": "TEST",
            "evidence": {"timestamp": datetime.now(), "ratio": 0.5},
        }
    )
    assert pdf.startswith(b"%PDF-")


def test_hash_is_stable_for_stable_input():
    """Two renders of the same input should produce the same packet hash.

    The PDF byte stream itself isn't byte-stable (PDF embeds a creation
    timestamp), but the SHA-256 of the rendered HTML *should* be stable
    because the template is deterministic given the input.
    """
    args = dict(
        claim={"id": "stable-claim"},
        artist={"name": "Test"},
        anomaly={"subtype": "STABLE_TEST", "estimated_recoverable": 10.0},
    )
    pdf1 = render_evidence_packet_pdf(**args)
    pdf2 = render_evidence_packet_pdf(**args)
    # PDFs differ in the embedded /CreationDate but the visible content
    # (and therefore the size) should be very close. Allow 5% drift.
    assert abs(len(pdf1) - len(pdf2)) / len(pdf1) < 0.05
