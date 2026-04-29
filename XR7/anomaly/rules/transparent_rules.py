from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

# Rule 4 (STREAM_MONTH_WITHOUT_PAYMENT) gates — see #208 for the original false-positive,
# and #209 for why these gates exist. The credibility budget for the dashboard is the
# constraint: don't promise recoverable dollars unless we're confident the gap is real.
#
# These two gates intentionally make the rule conservative. Edge cases left as
# follow-up in #209: source-aware quarterly cadence for PRO-only uploads, and
# per-source lag tuning (DistroKid: 60d, BMI: 120d, MLC: 90d, etc.).

# How many days after a reporting period's end before we expect the payment to land.
# Most distributors are 60-90 days; pick the longer end conservatively. A month
# whose end-of-period is within this window of "now" is treated as "too recent
# to flag" rather than "missing."
PAYMENT_LAG_DAYS = 90

# Minimum number of distinct event months required before Rule 4 fires at all.
# With one or two months of data, "missing payment" claims are too speculative —
# the artist might just not have uploaded the corresponding statement. Three
# months gives the rule something to compare against.
MIN_COVERAGE_MONTHS = 3

# Realistic recovery fraction. Even when a missing-payment gap is real, full
# recovery is rare due to SOL windows, partial settlements, and audit ranges.
# Under-promise the recoverable amount until we have settlement data to
# calibrate against.
RECOVERY_LIKELIHOOD = 0.30


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _to_dt(value):
    # datetime check has to come before date because datetime is a subclass of date.
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        # period_start/period_end columns are stored as date (not datetime); without
        # this branch _to_dt returned None for them and the rules fell back to
        # received_at — re-introducing #208 by a different code path.
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
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

    def _payment_period_dt(p: dict) -> datetime | None:
        """Bucket a payment by the reporting period it covers, not by ingestion time.

        Statements are uploaded after the period closes, so received_at
        always lands in "today's month" — using it for month-bucketing fired
        STREAM_MONTH_WITHOUT_PAYMENT on every upload (#208). Prefer
        period_start, then period_end, and only fall back to received_at
        if neither is set.
        """
        return (
            _to_dt(p.get("period_start"))
            or _to_dt(p.get("period_end"))
            or _to_dt(p.get("received_at"))
        )

    payout_months = {
        (_payment_period_dt(p).year, _payment_period_dt(p).month)
        for p in royalty_payments
        if _payment_period_dt(p)
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
                    "identity_key": "",  # fires once per artist
                    "evidence": {
                        "observed_rate": round(observed_rate, 6),
                        "median_platform_rate": round(baseline, 6),
                        "ratio": round(ratio, 4),
                        "stream_events_count": len(stream_events),
                    },
                }
            )

    # RULE 2: monthly royalty history has gap > 60 days.
    # Same period-vs-ingestion concern as Rule 4 — if every payment was
    # ingested today, received_at-based gaps would be 0 even when the
    # underlying reporting periods are years apart. Bucket by period.
    payment_dates = sorted(
        [_payment_period_dt(p) for p in royalty_payments if _payment_period_dt(p)]
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
                    "identity_key": "",  # fires once per artist with the current largest gap
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
                        "identity_key": "",  # aggregates across all contracts; fires once per artist
                        "evidence": {
                            "contract_rate": round(contract_rate, 6),
                            "observed_rate": round(observed, 6),
                            "delta_ratio": round(delta_ratio, 4),
                            "contracts_considered": len(contract_rates),
                        },
                    }
                )

    # RULE 4: if no royalty payments in months with streams. See #208 / #209 / #210 / #211.
    #
    # Two gates avoid false positives that erode dashboard credibility:
    #   1) Coverage gate: at least 3 distinct event months. With less, we can't
    #      tell "missing" from "single-statement upload."
    #   2) Lag gate: months within PAYMENT_LAG_DAYS (90) of now are treated as
    #      "too recent to flag" — distributors normally pay 60-90 days after
    #      the period ends, so a recent month with no payment yet isn't an
    #      anomaly, it's just normal cadence.
    event_months = {
        (_to_dt(e.get("timestamp")).year, _to_dt(e.get("timestamp")).month)
        for e in stream_events
        if _to_dt(e.get("timestamp"))
    }

    raw_missing = sorted(event_months - payout_months)
    lag_cutoff_date = (now - timedelta(days=PAYMENT_LAG_DAYS)).date()

    def _month_end(year: int, month: int) -> date:
        if month == 12:
            return date(year + 1, 1, 1) - timedelta(days=1)
        return date(year, month + 1, 1) - timedelta(days=1)

    missing_months = [(y, m) for (y, m) in raw_missing if _month_end(y, m) <= lag_cutoff_date]
    months_skipped_due_to_lag = len(raw_missing) - len(missing_months)

    if len(event_months) >= MIN_COVERAGE_MONTHS and missing_months:
        gross_for_missing = sum(
            float(e.get("quantity") or 0.0) * float(e.get("unit_value") or 0.0)
            for e in stream_events
            if _to_dt(e.get("timestamp"))
            and (_to_dt(e.get("timestamp")).year, _to_dt(e.get("timestamp")).month)
            in set(missing_months)
        )
        findings.append(
            {
                "artist_id": artist_id,
                "category": "ROYALTY",
                "subtype": "STREAM_MONTH_WITHOUT_PAYMENT",
                "severity": "HIGH",
                "expected_amount": None,
                "actual_amount": None,
                # Multiply by RECOVERY_LIKELIHOOD: full recovery is rare even
                # when the gap is real (SOL windows, partial settlements). Don't
                # inflate the dashboard headline number with optimistic claims.
                "estimated_recoverable": round(gross_for_missing * RECOVERY_LIKELIHOOD, 2),
                "confidence_score": 0.86,
                "status": "OPEN",
                "description": (
                    f"{len(missing_months)} month(s) older than {PAYMENT_LAG_DAYS} days "
                    "show stream activity with no corresponding royalty payment recorded."
                ),
                "rule_id": "STREAM_MONTH_NO_PAYMENT",
                "rule_name": "Stream month missing payment",
                "identity_key": "",  # one finding per artist; missing_months is the time-varying detail
                "evidence": {
                    "months_with_events": len(event_months),
                    "months_with_payments": len(payout_months),
                    "missing_months": [f"{y:04d}-{m:02d}" for y, m in missing_months[:6]],
                    "months_skipped_due_to_lag": months_skipped_due_to_lag,
                    "payment_lag_days": PAYMENT_LAG_DAYS,
                    "min_coverage_months": MIN_COVERAGE_MONTHS,
                    "recovery_likelihood": RECOVERY_LIKELIHOOD,
                    "gross_unpaid_estimate": round(gross_for_missing, 2),
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
                    "identity_key": "",  # fires once per artist
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
                "identity_key": "",  # fires once per artist
                "evidence": {
                    "contracts_total": len(contracts),
                    "contracts_missing_terms": len(incomplete_contracts),
                    "generated_at": now.isoformat(),
                },
            }
        )

    # RULE 7: high retroactive payment ratio (MLC reprocessing pattern).
    # MLC's "Processing Type" column distinguishes regular (current period)
    # vs reprocessing (catch-up) vs adjustment. We encode it in payment.source
    # as ".../regular" / ".../reprocessing" / ".../adjustment". A high
    # reprocessing ratio is itself a recoverable signal — it means the
    # licensing system has been catching up on under-reported royalties, and
    # where it has caught up there is usually more still uncollected.
    def _is_retroactive(source: str | None) -> bool:
        s = (source or "").lower().replace(" ", "")
        return s.endswith("/reprocessing") or s.endswith("/adjustment")

    def _payer_of(source: str | None) -> str:
        # First slash-segment of a source like "MLC / Spotify / regular" → "MLC".
        s = (source or "").strip()
        if "/" in s:
            return s.split("/", 1)[0].strip().upper()
        return s.upper()

    # Compute retroactive ratio PER PAYER (not aggregated across all sources).
    # A 64% retroactive ratio at MLC is the signal we want, even when BMI
    # dollar volume would dilute the artist-wide ratio below threshold.
    by_payer: dict[str, dict[str, float]] = {}
    for p in royalty_payments:
        amt = float(p.get("amount") or 0.0)
        payer = _payer_of(p.get("source"))
        bucket = by_payer.setdefault(
            payer,
            {"all": 0.0, "retro": 0.0, "all_count": 0, "retro_count": 0},
        )
        bucket["all"] += amt
        bucket["all_count"] += 1
        if _is_retroactive(p.get("source")):
            bucket["retro"] += amt
            bucket["retro_count"] += 1

    high_retro_payers = [
        (payer, b)
        for payer, b in by_payer.items()
        if b["all"] > 0 and (b["retro"] / b["all"]) > 0.30 and b["retro"] > 0
    ]
    if high_retro_payers:
        total_retro = sum(b["retro"] for _, b in high_retro_payers)
        # Heuristic: where retroactive corrections happen at this scale,
        # roughly half the same amount is typically still uncollected.
        est_more_uncollected = round(total_retro * 0.5, 2)
        worst_payer, worst_b = max(high_retro_payers, key=lambda kv: kv[1]["retro"] / kv[1]["all"])
        worst_ratio = worst_b["retro"] / worst_b["all"]
        findings.append(
            {
                "artist_id": artist_id,
                "category": "ROYALTY",
                "subtype": "HIGH_RETROACTIVE_PAYMENT_RATIO",
                "severity": "HIGH" if worst_ratio > 0.5 else "MEDIUM",
                "expected_amount": None,
                "actual_amount": round(total_retro, 2),
                "estimated_recoverable": est_more_uncollected,
                "confidence_score": 0.84,
                "status": "OPEN",
                "description": (
                    f"{worst_ratio*100:.0f}% of {worst_payer} royalties are retroactive "
                    "catch-ups, not current-period payments. Where retroactive corrections "
                    "happen at this scale, additional uncollected royalties typically still exist."
                ),
                "rule_id": "HIGH_RETROACTIVE_RATIO",
                "rule_name": "High retroactive payment ratio",
                # Per-payer rule — same artist can have a finding for MLC AND a separate
                # finding for ASCAP. Identity is the worst payer in this firing.
                "identity_key": worst_payer,
                "evidence": {
                    "by_payer": {
                        payer: {
                            "total_payments": int(b["all_count"]),
                            "retroactive_payments": int(b["retro_count"]),
                            "total_amount": round(b["all"], 2),
                            "retroactive_amount": round(b["retro"], 2),
                            "retroactive_ratio": round(b["retro"] / b["all"], 4),
                        }
                        for payer, b in high_retro_payers
                    },
                    "worst_payer": worst_payer,
                },
            }
        )

    # RULE 8: outlier track underpayment.
    # For each track with material activity (≥1000 streams), compute
    # the per-stream rate. If a track's per-stream rate is below 50% of
    # the artist's median across tracks, flag it as a likely
    # under-monetised work — could indicate a missing license, wrong
    # rate card, or platform-side error.
    track_totals: dict[str, dict[str, float]] = {}
    for e in stream_events:
        title = str(e.get("work_title") or e.get("isrc") or "").strip()
        if not title:
            continue
        bucket = track_totals.setdefault(title, {"quantity": 0.0, "amount": 0.0})
        qty = float(e.get("quantity") or 0.0)
        unit_value = float(e.get("unit_value") or 0.0)
        bucket["quantity"] += qty
        bucket["amount"] += qty * unit_value

    track_rates: list[tuple[str, float, float]] = [
        (t, b["amount"] / b["quantity"], b["quantity"])
        for t, b in track_totals.items()
        if b["quantity"] >= 1000
    ]
    if len(track_rates) >= 4:
        sorted_rates = sorted(r for _, r, _ in track_rates)
        median_rate = sorted_rates[len(sorted_rates) // 2]
        threshold = median_rate * 0.5
        outliers = [
            (title, rate, qty) for title, rate, qty in track_rates if rate > 0 and rate < threshold
        ]
        if outliers and median_rate > 0:
            # Recoverable estimate: bring outliers up to median rate on their volume.
            est_recoverable = round(
                sum((median_rate - rate) * qty for _, rate, qty in outliers),
                2,
            )
            top_outliers = sorted(outliers, key=lambda x: x[1])[:5]
            findings.append(
                {
                    "artist_id": artist_id,
                    "category": "ROYALTY",
                    "subtype": "TRACK_RATE_OUTLIER_UNDERPAYMENT",
                    "severity": "MEDIUM",
                    "expected_amount": round(median_rate, 6),
                    "actual_amount": round(min(r for _, r, _ in outliers), 6),
                    "estimated_recoverable": est_recoverable,
                    "confidence_score": 0.78,
                    "status": "OPEN",
                    "description": (
                        f"{len(outliers)} track(s) earned less than half the artist's "
                        f"median per-stream rate (median ${median_rate:.6f}). Outliers "
                        "may indicate missing licenses or wrong rate cards."
                    ),
                    "rule_id": "TRACK_RATE_OUTLIER",
                    "rule_name": "Outlier track underpayment",
                    # Aggregated across all outlier tracks; one finding per artist that
                    # lists the worst offenders in evidence. Per-track findings would
                    # need their own rule_id.
                    "identity_key": "",
                    "evidence": {
                        "tracks_examined": len(track_rates),
                        "outlier_count": len(outliers),
                        "median_rate": round(median_rate, 6),
                        "top_outliers": [
                            {
                                "title": title,
                                "per_stream_rate": round(rate, 6),
                                "stream_count": int(qty),
                                "rate_pct_of_median": round(rate / median_rate * 100, 1),
                            }
                            for title, rate, qty in top_outliers
                        ],
                    },
                }
            )

    return findings
