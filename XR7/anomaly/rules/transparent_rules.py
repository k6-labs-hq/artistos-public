from __future__ import annotations

from datetime import datetime, timezone


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _to_dt(value):
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None


def run_transparent_rules(
    artist_id: str, events: list[dict], payments: list[dict], contracts: list[dict]
) -> list[dict]:
    now = datetime.now(timezone.utc)
    findings: list[dict] = []

    stream_events = [e for e in events if str(e.get("event_type", "")).upper() == "STREAM"]
    stream_rates = [
        float(e.get("unit_value") or 0.0)
        for e in stream_events
        if float(e.get("unit_value") or 0.0) > 0
    ]
    median_platform_rate = 0.004
    if stream_rates:
        sorted_rates = sorted(stream_rates)
        median_platform_rate = sorted_rates[len(sorted_rates) // 2]

    royalty_payments = [
        p for p in payments if str(p.get("payment_type", "")).upper() in {"ROYALTY", "SETTLEMENT"}
    ]
    payout_months = {
        (_to_dt(p.get("received_at")).year, _to_dt(p.get("received_at")).month)
        for p in royalty_payments
        if _to_dt(p.get("received_at"))
    }

    # RULE 1: streaming payout under 50% of expected market baseline.
    if stream_events:
        observed_rate = _mean(stream_rates) if stream_rates else 0.0
        baseline = max(median_platform_rate, 0.001)
        ratio = observed_rate / baseline if baseline > 0 else 0.0
        if ratio < 0.5:
            est_loss = max(
                (baseline - observed_rate)
                * sum(float(e.get("quantity") or 0.0) for e in stream_events),
                0.0,
            )
            findings.append(
                {
                    "artist_id": artist_id,
                    "category": "PLATFORM",
                    "subtype": "STREAM_PAYOUT_BELOW_50PCT",
                    "severity": "HIGH",
                    "expected_amount": round(baseline, 6),
                    "actual_amount": round(observed_rate, 6),
                    "estimated_recoverable": round(est_loss, 2),
                    "confidence_score": 0.9,
                    "status": "OPEN",
                    "description": "Average stream payout rate is below 50% of recent platform baseline.",
                    "rule_id": "STREAM_PAYOUT_UNDER_50",
                    "rule_name": "Stream payout less than 50% baseline",
                    "evidence": {
                        "observed_rate": round(observed_rate, 6),
                        "median_platform_rate": round(baseline, 6),
                        "ratio": round(ratio, 4),
                        "stream_events_count": len(stream_events),
                    },
                }
            )

    # RULE 2: monthly royalty history has gap > 60 days.
    payment_dates = sorted(
        [_to_dt(p.get("received_at")) for p in royalty_payments if _to_dt(p.get("received_at"))]
    )
    if len(payment_dates) >= 2:
        largest_gap = max((b - a).days for a, b in zip(payment_dates[:-1], payment_dates[1:]))
        if largest_gap > 60:
            findings.append(
                {
                    "artist_id": artist_id,
                    "category": "ROYALTY",
                    "subtype": "PAYMENT_GAP_OVER_60_DAYS",
                    "severity": "HIGH",
                    "expected_amount": None,
                    "actual_amount": None,
                    "estimated_recoverable": round(
                        _mean([float(p.get("amount") or 0.0) for p in royalty_payments]), 2
                    ),
                    "confidence_score": 0.88,
                    "status": "OPEN",
                    "description": "Detected royalty payment gap greater than 60 days.",
                    "rule_id": "PAYMENT_GAP_OVER_60",
                    "rule_name": "Royalty payment gap exceeds 60 days",
                    "evidence": {
                        "largest_gap_days": largest_gap,
                        "payment_count": len(payment_dates),
                        "first_payment_at": payment_dates[0].isoformat(),
                        "last_payment_at": payment_dates[-1].isoformat(),
                    },
                }
            )

    # RULE 3: contract baseline and observed stream rate differ by >20%.
    contract_rates = []
    for c in contracts:
        terms = c.get("terms") or {}
        rate = terms.get("rate")
        if rate is None:
            rate = terms.get("unit_rate")
        if rate is not None:
            contract_rates.append(float(rate))
    if contract_rates and stream_rates:
        contract_rate = _mean(contract_rates)
        observed = _mean(stream_rates)
        if contract_rate > 0:
            delta_ratio = abs(observed - contract_rate) / contract_rate
            if delta_ratio > 0.2:
                findings.append(
                    {
                        "artist_id": artist_id,
                        "category": "ROYALTY",
                        "subtype": "CONTRACT_RATE_DEVIATION_OVER_20PCT",
                        "severity": "MEDIUM",
                        "expected_amount": round(contract_rate, 6),
                        "actual_amount": round(observed, 6),
                        "estimated_recoverable": 0.0,
                        "confidence_score": 0.82,
                        "status": "OPEN",
                        "description": "Observed stream unit values deviate from contract baseline by over 20%.",
                        "rule_id": "CONTRACT_RATE_DEVIATION_OVER_20",
                        "rule_name": "Contract rate deviation exceeds 20%",
                        "evidence": {
                            "contract_rate": round(contract_rate, 6),
                            "observed_rate": round(observed, 6),
                            "delta_ratio": round(delta_ratio, 4),
                            "contracts_considered": len(contract_rates),
                        },
                    }
                )

    # RULE 4: if no royalty payments in months with streams.
    event_months = {
        (_to_dt(e.get("timestamp")).year, _to_dt(e.get("timestamp")).month)
        for e in stream_events
        if _to_dt(e.get("timestamp"))
    }
    missing_months = sorted(event_months - payout_months)
    if missing_months:
        findings.append(
            {
                "artist_id": artist_id,
                "category": "ROYALTY",
                "subtype": "STREAM_MONTH_WITHOUT_PAYMENT",
                "severity": "HIGH",
                "expected_amount": None,
                "actual_amount": None,
                "estimated_recoverable": round(
                    sum(
                        float(e.get("quantity") or 0.0) * float(e.get("unit_value") or 0.0)
                        for e in stream_events
                    ),
                    2,
                ),
                "confidence_score": 0.86,
                "status": "OPEN",
                "description": "At least one month contains stream activity with no corresponding royalty payment.",
                "rule_id": "STREAM_MONTH_NO_PAYMENT",
                "rule_name": "Stream month missing payment",
                "evidence": {
                    "months_with_events": len(event_months),
                    "months_with_payments": len(payout_months),
                    "missing_months": [f"{y:04d}-{m:02d}" for y, m in missing_months[:6]],
                },
            }
        )

    # RULE 5: payment concentration risk if top payment > 60% of total.
    amounts = [
        float(p.get("amount") or 0.0)
        for p in royalty_payments
        if float(p.get("amount") or 0.0) > 0.0
    ]
    if len(amounts) >= 3:
        total = sum(amounts)
        top = max(amounts)
        concentration = top / total if total > 0 else 0.0
        if concentration > 0.6:
            findings.append(
                {
                    "artist_id": artist_id,
                    "category": "ROYALTY",
                    "subtype": "PAYMENT_CONCENTRATION_RISK",
                    "severity": "MEDIUM",
                    "expected_amount": round(total / len(amounts), 2),
                    "actual_amount": round(top, 2),
                    "estimated_recoverable": 0.0,
                    "confidence_score": 0.74,
                    "status": "OPEN",
                    "description": "Single payment concentration suggests volatility or delayed remittance behavior.",
                    "rule_id": "PAYMENT_CONCENTRATION_OVER_60",
                    "rule_name": "Top payment concentration above 60%",
                    "evidence": {
                        "top_payment": round(top, 2),
                        "total_payments": round(total, 2),
                        "concentration_ratio": round(concentration, 4),
                    },
                }
            )

    # RULE 6: stale contracts lacking clear term data.
    incomplete_contracts = [
        c for c in contracts if not isinstance(c.get("terms"), dict) or not c.get("terms")
    ]
    if incomplete_contracts:
        findings.append(
            {
                "artist_id": artist_id,
                "category": "ROYALTY",
                "subtype": "CONTRACT_TERMS_INCOMPLETE",
                "severity": "LOW",
                "expected_amount": None,
                "actual_amount": None,
                "estimated_recoverable": 0.0,
                "confidence_score": 0.68,
                "status": "OPEN",
                "description": "Contracts missing terms may weaken automated validation and recovery posture.",
                "rule_id": "CONTRACT_TERMS_MISSING",
                "rule_name": "Contract terms are incomplete",
                "evidence": {
                    "contracts_total": len(contracts),
                    "contracts_missing_terms": len(incomplete_contracts),
                    "generated_at": now.isoformat(),
                },
            }
        )

    return findings
