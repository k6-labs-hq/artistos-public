from __future__ import annotations

from typing import Any


def tax_optimizer(artist_id: str, gross_amount: float, us_withholding_rate: float, global_withholding_rate: float, fx_rate: float) -> dict[str, Any]:
    us_withheld = gross_amount * us_withholding_rate
    global_withheld = gross_amount * global_withholding_rate
    net_usd = (gross_amount - us_withheld - global_withheld) * fx_rate
    return {
        "artist_id": artist_id,
        "gross_amount": round(gross_amount, 2),
        "us_withheld": round(us_withheld, 2),
        "global_withheld": round(global_withheld, 2),
        "fx_rate": fx_rate,
        "net_estimate": round(net_usd, 2),
        "strategies": [
            "Prioritize treaty-benefit territories for withholding reduction",
            "Batch claims by territory to reduce reconciliation costs",
            "Use FX windows for high-volatility disbursements",
        ],
    }
