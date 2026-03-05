def check_royalty_not_paid(artist_id: str, events: list[dict], payments: list[dict], contracts: list[dict]) -> list[dict]:
    anomalies = []
    merch_contracts = [c for c in contracts if c.get("contract_type") == "MERCH"]
    merch_payments = [p for p in payments if p.get("payment_type") == "ROYALTY" and p.get("source", "").upper() == "MERCH"]
    sale_events = [e for e in events if e.get("event_type") == "SALE"]
    if merch_contracts and sale_events and not merch_payments:
        anomalies.append({
            "artist_id": artist_id,
            "category": "MERCH",
            "subtype": "ROYALTY_NOT_PAID",
            "severity": "MEDIUM",
            "description": "Merch sale events found with contract but no merch royalty payments.",
            "confidence_score": 0.75,
        })
    return anomalies


def check_advance_unrecouped(artist_id: str, payments: list[dict], contracts: list[dict]) -> list[dict]:
    anomalies = []
    for contract in contracts:
        if contract.get("contract_type") != "MERCH":
            continue
        terms = contract.get("terms") or {}
        advance = terms.get("advance", 0.0)
        recoupment_rate = terms.get("recoupment_rate", 1.0)
        total_received = sum(p.get("amount", 0.0) for p in payments)
        recouped = total_received * recoupment_rate
        if advance > 0 and recouped < advance:
            anomalies.append({
                "artist_id": artist_id,
                "category": "MERCH",
                "subtype": "ADVANCE_UNRECOUPED",
                "severity": "LOW",
                "expected_amount": advance,
                "actual_amount": recouped,
                "confidence_score": 0.65,
                "description": f"Merch advance of {advance} not yet fully recouped (recouped: {recouped}).",
            })
    return anomalies
