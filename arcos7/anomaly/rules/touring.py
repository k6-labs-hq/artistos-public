def check_missing_guarantee(artist_id: str, events: list[dict], payments: list[dict]) -> list[dict]:
    anomalies = []
    show_events = [e for e in events if e.get("event_type") == "SHOW"]
    settlement_payments = [p for p in payments if p.get("payment_type") == "SETTLEMENT"]
    if show_events and not settlement_payments:
        anomalies.append({
            "artist_id": artist_id,
            "category": "TOURING",
            "subtype": "MISSING_GUARANTEE",
            "severity": "HIGH",
            "description": "Show events found but no settlement payment received.",
            "confidence_score": 0.8,
        })
    return anomalies


def check_settlement_discrepancy(artist_id: str, events: list[dict], payments: list[dict], contracts: list[dict]) -> list[dict]:
    anomalies = []
    for contract in contracts:
        if contract.get("contract_type") != "TOURING":
            continue
        terms = contract.get("terms") or {}
        guarantee = terms.get("guarantee", 0.0)
        total_settlement = sum(p.get("amount", 0.0) for p in payments if p.get("payment_type") == "SETTLEMENT")
        if guarantee > 0 and total_settlement < guarantee * 0.95:
            anomalies.append({
                "artist_id": artist_id,
                "category": "TOURING",
                "subtype": "SETTLEMENT_DISCREPANCY",
                "severity": "MEDIUM",
                "expected_amount": guarantee,
                "actual_amount": total_settlement,
                "estimated_recoverable": guarantee - total_settlement,
                "confidence_score": 0.85,
                "description": f"Settlement total {total_settlement} is below contracted guarantee {guarantee}.",
            })
    return anomalies
