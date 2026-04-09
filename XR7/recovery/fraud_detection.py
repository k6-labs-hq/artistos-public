from __future__ import annotations

import hashlib
from typing import Any


def run_fraud_scan(
    claims: list[dict[str, Any]], statements: list[dict[str, Any]]
) -> dict[str, Any]:
    """Detect duplicate claims, potential tampering, and suspicious statement patterns."""
    seen_claim_keys: set[tuple[str, str]] = set()
    duplicate_claims: list[dict[str, Any]] = []

    for c in claims:
        key = (str(c.get("anomaly_id") or ""), str(c.get("claim_type") or ""))
        if key in seen_claim_keys:
            duplicate_claims.append(
                {"claim_id": c.get("id"), "reason": "duplicate_anomaly_claim_type"}
            )
        else:
            seen_claim_keys.add(key)

    tampered = []
    suspicious = []

    for s in statements:
        content = str(s.get("raw_content") or "")
        calc_hash = hashlib.sha256(content.encode("utf-8")).hexdigest() if content else None
        stored_hash = s.get("file_hash")
        if stored_hash and calc_hash and stored_hash != calc_hash:
            tampered.append({"statement_id": s.get("id"), "reason": "hash_mismatch"})

        row_count = int(s.get("row_count") or 0)
        events_created = int(s.get("events_created") or 0)
        if row_count > 0 and events_created == 0:
            suspicious.append(
                {"statement_id": s.get("id"), "reason": "no_events_from_nonempty_file"}
            )

    return {
        "duplicate_claims": duplicate_claims,
        "fraudulent_statements": suspicious,
        "tampered_csvs": tampered,
        "suspicious_patterns": duplicate_claims + suspicious + tampered,
        "scan_summary": {
            "duplicate_claim_count": len(duplicate_claims),
            "fraud_statement_count": len(suspicious),
            "tampered_csv_count": len(tampered),
        },
    }
