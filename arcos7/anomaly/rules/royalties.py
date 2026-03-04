def check_missing_royalty_payments(artist_id: str, events: list[dict], payments: list[dict]) -> list[dict]:
    anomalies = []
    royalty_events = [e for e in events if e.get("event_type") in ("STREAM", "SALE")]
    royalty_payments = [p for p in payments if p.get("payment_type") == "ROYALTY"]

    if royalty_events and not royalty_payments:
        anomalies.append({
            "artist_id": artist_id,
            "category": "ROYALTY",
            "subtype": "MISSING_PAYMENT",
            "severity": "HIGH",
            "description": "Royalty-generating events found but no royalty payments received.",
            "confidence_score": 0.85,
        })
    return anomalies


def check_incorrect_rates(artist_id: str, payments: list[dict], contracts: list[dict]) -> list[dict]:
    anomalies = []
    for payment in payments:
        expected_rate = None
        for contract in contracts:
            terms = contract.get("terms") or {}
            if terms.get("rate"):
                expected_rate = terms["rate"]
                break
        if expected_rate is None:
            continue
        actual_amount = payment.get("amount", 0.0)
        quantity = payment.get("quantity", 1)
        expected_amount = expected_rate * quantity
        if expected_amount > 0:
            discrepancy = abs(actual_amount - expected_amount) / expected_amount
            if discrepancy > 0.05:
                anomalies.append({
                    "artist_id": artist_id,
                    "category": "ROYALTY",
                    "subtype": "INCORRECT_RATE",
                    "severity": "MEDIUM",
                    "expected_amount": expected_amount,
                    "actual_amount": actual_amount,
                    "estimated_recoverable": expected_amount - actual_amount,
                    "confidence_score": 0.75,
                    "description": f"Payment rate discrepancy of {discrepancy:.1%} detected.",
                })
    return anomalies


def check_unmatched_works(artist_id: str, works: list[dict], events: list[dict]) -> list[dict]:
    anomalies = []
    work_ids_with_contracts = {w.get("id") for w in works if w.get("has_contract")}
    for event in events:
        work_id = event.get("work_id")
        if work_id and work_id not in work_ids_with_contracts:
            anomalies.append({
                "artist_id": artist_id,
                "category": "ROYALTY",
                "subtype": "UNMATCHED_WORK",
                "severity": "LOW",
                "description": f"Event references work {work_id} with no associated contract.",
                "confidence_score": 0.6,
            })
    return anomalies


def check_foreign_royalties_not_remitted(artist_id: str, events: list[dict], payments: list[dict]) -> list[dict]:
    anomalies = []
    foreign_events = [e for e in events if e.get("territory") not in (None, "US", "USA")]
    foreign_payments = [p for p in payments if p.get("source") not in (None, "DOMESTIC")]
    if foreign_events and not foreign_payments:
        anomalies.append({
            "artist_id": artist_id,
            "category": "ROYALTY",
            "subtype": "FOREIGN_ROYALTIES_NOT_REMITTED",
            "severity": "HIGH",
            "description": "Foreign territory events found with no corresponding foreign royalty payments.",
            "confidence_score": 0.7,
        })
    return anomalies
