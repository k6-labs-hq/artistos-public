from __future__ import annotations

from collections import defaultdict
from typing import Any


def attribute_recovery(
    anomalies: list[dict[str, Any]], claims: list[dict[str, Any]]
) -> dict[str, Any]:
    """Attribute recovered value to anomalies, claims, catalog issues, and contract issues."""
    by_anomaly: dict[str, float] = defaultdict(float)
    by_claim: dict[str, float] = defaultdict(float)
    by_catalog_issue: dict[str, float] = defaultdict(float)
    by_contract_issue: dict[str, float] = defaultdict(float)

    anomaly_lookup = {str(a.get("id")): a for a in anomalies}

    for c in claims:
        amount = float(c.get("recovered_amount") or 0.0)
        claim_id = str(c.get("id") or "unknown")
        by_claim[claim_id] += amount

        anomaly_id = str(c.get("anomaly_id") or "unknown_anomaly")
        by_anomaly[anomaly_id] += amount

        anomaly = anomaly_lookup.get(anomaly_id) or {}
        by_catalog_issue[str(anomaly.get("subtype") or "unknown_catalog_issue")] += amount
        by_contract_issue[str(c.get("claim_type") or "unknown_contract_issue")] += amount

    return {
        "by_anomalies": dict(by_anomaly),
        "by_claims": dict(by_claim),
        "by_catalog_issues": dict(by_catalog_issue),
        "by_contract_issues": dict(by_contract_issue),
    }
