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
        contract_terms: dict | None = None,
    ) -> dict:
        contract_terms = contract_terms or {}
        contract_rate = contract_terms.get("royalty_rate")
        contract_rate_pct = contract_terms.get("royalty_rate_percent")
        contract_withholding = contract_terms.get("withholding_rate")
        min_guarantee = float(contract_terms.get("minimum_guarantee", 0.0) or 0.0)

        expected_total = 0.0
        gross_native_total = 0.0
        withheld_native_total = 0.0
        details: list[dict] = []

        for row in usage_rows:
            quantity = float(row.get("quantity", 0.0) or 0.0)
            row_rate = row.get("rate")
            # Contract terms can override row/fallback assumptions when provided.
            if contract_rate is not None:
                rate = float(contract_rate)
            elif contract_rate_pct is not None:
                rate = float(contract_rate_pct) / 100.0
            else:
                rate = float(row_rate if row_rate is not None else fallback_rate)

            if contract_withholding is not None:
                withholding_rate = float(contract_withholding)
            else:
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
        if min_guarantee > 0:
            expected_total = max(expected_total, min_guarantee)
        variance = expected_total - received
        variance_pct = 0.0 if expected_total == 0 else (variance / expected_total)

        variance_explanations: list[dict] = []
        if variance > 0:
            variance_explanations.append(
                {
                    "type": "UNDERPAYMENT",
                    "message": "Actual received payout is below contract-aware expected payout.",
                    "amount": round(variance, 4),
                }
            )
        if withheld_native_total > 0:
            variance_explanations.append(
                {
                    "type": "WITHHOLDING",
                    "message": "Withholding deductions contributed to payout reduction.",
                    "amount": round(withheld_native_total, 4),
                }
            )
        if min_guarantee > 0 and expected_total == min_guarantee:
            variance_explanations.append(
                {
                    "type": "MINIMUM_GUARANTEE",
                    "message": "Expected payout floor set by contract minimum guarantee.",
                    "amount": round(min_guarantee, 4),
                }
            )

        return {
            "payout_currency": payout_currency,
            "gross_native_total": round(gross_native_total, 4),
            "withheld_native_total": round(withheld_native_total, 4),
            "expected_total": round(expected_total, 4),
            "received_total": round(received, 4),
            "variance": round(variance, 4),
            "variance_pct": round(variance_pct, 6),
            "contract_terms_used": contract_terms,
            "variance_explanations": variance_explanations,
            "line_items": details,
        }
