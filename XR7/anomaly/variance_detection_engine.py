from __future__ import annotations

from typing import Any


def run_variance_scan(rows: list[dict[str, Any]]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    for row in rows:
        streams = float(row.get("streams") or 0.0)
        payout = float(row.get("payout") or 0.0)
        expected = float(row.get("expected_payout") or 0.0)
        has_registration = bool(row.get("has_registration", True))
        reported_usage = float(row.get("reported_usage") or streams)

        if expected > payout:
            findings.append({"type": "STREAM_VS_PAYOUT_MISMATCH", "amount": round(expected - payout, 4), "row": row})
        if not has_registration and streams > 0:
            findings.append({"type": "MISSING_REGISTRATION", "row": row})
        if streams > reported_usage:
            findings.append({"type": "UNDERREPORTED_USAGE", "amount": round(streams - reported_usage, 4), "row": row})
        if streams > 0 and payout == 0:
            findings.append({"type": "BLACK_BOX_LEAKAGE", "row": row})
        if expected and payout < expected * 0.75:
            findings.append({"type": "CONTRACT_BASED_VALIDATION_FAIL", "amount": round(expected - payout, 4), "row": row})

    return {"finding_count": len(findings), "findings": findings}
