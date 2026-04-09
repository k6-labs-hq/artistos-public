def check_unlicensed_usage(artist_id: str, events: list[dict], contracts: list[dict]) -> list[dict]:
    anomalies = []
    sync_events = [e for e in events if e.get("event_type") == "SYNC_USAGE"]
    sync_contracts = [c for c in contracts if c.get("contract_type") == "SYNC"]
    if sync_events and not sync_contracts:
        anomalies.append(
            {
                "artist_id": artist_id,
                "category": "SYNC",
                "subtype": "UNLICENSED_USAGE",
                "severity": "CRITICAL",
                "description": "Sync usage events detected with no corresponding sync license contract.",
                "confidence_score": 0.9,
            }
        )
    return anomalies


def check_brand_payment_missing(
    artist_id: str, events: list[dict], payments: list[dict]
) -> list[dict]:
    anomalies = []
    brand_events = [e for e in events if e.get("event_type") == "BRAND_IMPRESSION"]
    brand_payments = [p for p in payments if p.get("source", "").upper() == "BRAND"]
    if brand_events and not brand_payments:
        anomalies.append(
            {
                "artist_id": artist_id,
                "category": "BRAND",
                "subtype": "BRAND_PAYMENT_MISSING",
                "severity": "HIGH",
                "description": "Brand impression events found with no corresponding brand payment.",
                "confidence_score": 0.8,
            }
        )
    return anomalies
