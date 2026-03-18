from __future__ import annotations

import csv
import io
import json
import zipfile
from datetime import datetime, timezone
from typing import Any

from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.claim import Claim
from XR7.services.pdf_builder import build_simple_pdf


def build_tvfilm_evidence_packet(*, artist: Artist, claim: Claim, anomaly: Anomaly, feature_snapshot: dict[str, Any], template: str) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    estimated = float(anomaly.estimated_recoverable or 0.0)
    expected_amount = float(anomaly.expected_amount or 0.0)
    actual_amount = float(anomaly.actual_amount or 0.0)

    packet = {
        "packet_type": "TV_FILM_EVIDENCE",
        "generated_at": generated_at,
        "artist": {
            "artist_id": artist.id,
            "name": artist.name,
            "role": artist.tvfilm_role or artist.role,
            "vertical": artist.primary_vertical or "TV_FILM",
        },
        "claim": {
            "claim_id": claim.id,
            "claim_type": claim.claim_type,
            "status": str(getattr(claim.status, "value", claim.status)),
            "template": template,
        },
        "anomaly": {
            "anomaly_id": anomaly.id,
            "category": str(getattr(anomaly.category, "value", anomaly.category)),
            "subtype": anomaly.subtype,
            "confidence": float(anomaly.confidence_score or 0.0),
            "estimated_recoverable": estimated,
            "expected_amount": expected_amount,
            "actual_amount": actual_amount,
        },
        "production": {
            "production_id": feature_snapshot.get("production_id"),
            "season": feature_snapshot.get("season"),
            "episode": feature_snapshot.get("episode"),
            "platform": feature_snapshot.get("platform"),
            "distribution_window": feature_snapshot.get("distribution_window"),
            "market": feature_snapshot.get("market"),
        },
        "required_sections": list((claim.evidence or {}).get("required_sections") or []),
        "narrative": {
            "summary": (
                f"XR7 identified a {anomaly.subtype} variance for {artist.name} tied to production "
                f"{feature_snapshot.get('production_id') or 'UNKNOWN'} with an estimated recoverable amount of ${estimated:,.2f}."
            ),
            "plain_language": (
                "We compared expected TV/Film compensation by role, union, studio/platform, and reuse window against what was actually paid."
            ),
        },
        "supporting_tables": {
            "payment_delta": [
                {
                    "expected_amount": expected_amount,
                    "actual_amount": actual_amount,
                    "recoverable_delta": estimated,
                }
            ],
            "production_context": [feature_snapshot],
        },
        "integrity": {
            "evidence_hashes": list((claim.evidence or {}).get("evidence_hashes") or []),
        },
    }
    return packet


def build_tvfilm_packet_lines(packet: dict[str, Any]) -> list[str]:
    artist = packet.get("artist") or {}
    claim = packet.get("claim") or {}
    anomaly = packet.get("anomaly") or {}
    production = packet.get("production") or {}
    lines = [
        "XR7 TV/Film Evidence Packet",
        f"Generated At: {packet.get('generated_at')}",
        f"Artist: {artist.get('name')} ({artist.get('role')})",
        f"Claim ID: {claim.get('claim_id')}",
        f"Claim Type: {claim.get('claim_type')}",
        f"Template: {claim.get('template')}",
        "",
        f"Anomaly: {anomaly.get('subtype')}",
        f"Confidence: {anomaly.get('confidence')}",
        f"Expected Amount: {anomaly.get('expected_amount')}",
        f"Actual Amount: {anomaly.get('actual_amount')}",
        f"Estimated Recoverable: {anomaly.get('estimated_recoverable')}",
        "",
        f"Production ID: {production.get('production_id')}",
        f"Season/Episode: {production.get('season')} / {production.get('episode')}",
        f"Platform: {production.get('platform')}",
        f"Distribution Window: {production.get('distribution_window')}",
        f"Market: {production.get('market')}",
        "",
        "Narrative Summary",
        str((packet.get('narrative') or {}).get('summary') or ''),
        "",
        "Plain Language",
        str((packet.get('narrative') or {}).get('plain_language') or ''),
    ]
    for section in packet.get("required_sections") or []:
        lines.append(f"Required Section: {section}")
    return lines


def build_tvfilm_packet_pdf(packet: dict[str, Any]) -> bytes:
    return build_simple_pdf(build_tvfilm_packet_lines(packet))


def build_tvfilm_packet_zip(packet: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    pdf_bytes = build_tvfilm_packet_pdf(packet)

    payment_delta = ((packet.get("supporting_tables") or {}).get("payment_delta") or [])
    table_csv = io.StringIO()
    writer = csv.DictWriter(table_csv, fieldnames=["expected_amount", "actual_amount", "recoverable_delta"])
    writer.writeheader()
    for row in payment_delta:
        writer.writerow(row)

    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("tvfilm_evidence_packet.json", json.dumps(packet, indent=2, sort_keys=True))
        zf.writestr("tvfilm_evidence_summary.txt", "\n".join(build_tvfilm_packet_lines(packet)) + "\n")
        zf.writestr("tvfilm_evidence_packet.pdf", pdf_bytes)
        zf.writestr("payment_delta.csv", table_csv.getvalue())
        zf.writestr("integrity_manifest.json", json.dumps(packet.get("integrity") or {}, indent=2, sort_keys=True))
    return buffer.getvalue()


def build_tvfilm_bulk_export_zip(items: list[dict[str, Any]]) -> bytes:
    buffer = io.BytesIO()
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_count": len(items),
        "claim_ids": [item.get("claim_id") for item in items],
    }

    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
        for item in items:
            claim_id = str(item.get("claim_id"))
            packet = item.get("packet") or {}
            zf.writestr(f"{claim_id}/tvfilm_evidence_packet.json", json.dumps(packet, indent=2, sort_keys=True))
            zf.writestr(f"{claim_id}/tvfilm_evidence_packet.pdf", build_tvfilm_packet_pdf(packet))
            zf.writestr(f"{claim_id}/tvfilm_evidence_summary.txt", "\n".join(build_tvfilm_packet_lines(packet)) + "\n")
    return buffer.getvalue()
