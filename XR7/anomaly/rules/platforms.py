MIN_STREAM_RATE = 0.003


def check_low_stream_rates(artist_id: str, events: list[dict], payments: list[dict]) -> list[dict]:
    anomalies = []
    stream_events = [e for e in events if e.get("event_type") == "STREAM"]
    for event in stream_events:
        unit_value = event.get("unit_value", 0.0)
        if unit_value > 0 and unit_value < MIN_STREAM_RATE:
            anomalies.append({
                "artist_id": artist_id,
                "category": "PLATFORM",
                "subtype": "LOW_STREAM_RATE",
                "severity": "MEDIUM",
                "actual_amount": unit_value,
                "expected_amount": MIN_STREAM_RATE,
                "estimated_recoverable": (MIN_STREAM_RATE - unit_value) * event.get("quantity", 1),
                "confidence_score": 0.8,
                "description": f"Per-stream rate {unit_value} is below minimum threshold of {MIN_STREAM_RATE}.",
            })
    return anomalies


def check_missing_platform_payments(artist_id: str, events: list[dict], payments: list[dict]) -> list[dict]:
    anomalies = []
    stream_events = [e for e in events if e.get("event_type") == "STREAM"]
    dsp_payments = [p for p in payments if p.get("payment_type") == "ROYALTY"]
    if stream_events and not dsp_payments:
        anomalies.append({
            "artist_id": artist_id,
            "category": "PLATFORM",
            "subtype": "MISSING_PLATFORM_PAYMENT",
            "severity": "HIGH",
            "description": "Streaming events reported but no DSP royalty payments found.",
            "confidence_score": 0.85,
        })
    return anomalies
