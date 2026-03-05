class ExpectedPayoutSimulator:
    """Estimate expected payout and variance from usage + contract term assumptions."""

    def simulate(
        self,
        usage_rows: list[dict],
        fallback_rate: float = 0.004,
        default_withholding_rate: float = 0.0,
        default_fx_rate: float = 1.0,
        payout_currency: str = "USD",
        received_amount: float | None = None,
    ) -> dict:
        expected_total = 0.0
        gross_native_total = 0.0
        withheld_native_total = 0.0
        details: list[dict] = []

        for row in usage_rows:
            quantity = float(row.get("quantity", 0.0) or 0.0)
            row_rate = row.get("rate")
            rate = float(row_rate if row_rate is not None else fallback_rate)
            withholding_rate = float(row.get("withholding_rate", default_withholding_rate) or 0.0)
            fx_rate = float(row.get("fx_rate", default_fx_rate) or 1.0)

            gross_native = quantity * rate
            withheld_native = gross_native * max(min(withholding_rate, 1.0), 0.0)
            net_native = gross_native - withheld_native
            expected = net_native * fx_rate

            gross_native_total += gross_native
            withheld_native_total += withheld_native
            expected_total += expected
            details.append(
                {
                    "source": row.get("source"),
                    "work_id": row.get("work_id"),
                    "territory": row.get("territory"),
                    "period_start": row.get("period_start"),
                    "period_end": row.get("period_end"),
                    "quantity": quantity,
                    "rate": rate,
                    "withholding_rate": withholding_rate,
                    "fx_rate": fx_rate,
                    "gross_native_amount": round(gross_native, 4),
                    "withheld_native_amount": round(withheld_native, 4),
                    "expected_amount": round(expected, 4),
                }
            )

        received = float(received_amount if received_amount is not None else 0.0)
        variance = expected_total - received
        variance_pct = 0.0 if expected_total == 0 else (variance / expected_total)

        return {
            "payout_currency": payout_currency,
            "gross_native_total": round(gross_native_total, 4),
            "withheld_native_total": round(withheld_native_total, 4),
            "expected_total": round(expected_total, 4),
            "received_total": round(received, 4),
            "variance": round(variance, 4),
            "variance_pct": round(variance_pct, 6),
            "line_items": details,
        }
