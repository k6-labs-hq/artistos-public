"""Pillar 4 — Creator-economy anomaly rules.

Detects missing payouts, below-benchmark CPM/CPP, affiliate/merch gaps
across YouTube Studio, TikTok, Instagram Reels, Twitch, Patreon, Shopify.
"""

from __future__ import annotations

from typing import Any

_PLATFORM_CPM_BENCHMARKS: dict[str, float] = {
    "youtube_studio": 1.50,  # USD RPM floor
    "tiktok_creator_fund": 0.02,  # USD per 1k views floor
    "instagram_reels": 0.01,
    "twitch": 2.50,
    "patreon": 0.0,  # not applicable
    "shopify": 0.0,
}

_SHOPIFY_CONVERSION_FLOOR = 0.01  # 1 % minimum


def detect_creator_anomalies(
    events: list[dict[str, Any]],
    artist_id: str,
) -> list[dict[str, Any]]:
    """Run creator-economy anomaly rules over a batch of parsed events.

    Returns a list of anomaly dicts compatible with XR7's anomaly engine.
    """
    anomalies: list[dict[str, Any]] = []

    for ev in events:
        platform = ev.get("platform", "")
        period = ev.get("period", "")
        gross = float(ev.get("gross_amount") or 0.0)
        units = float(ev.get("units") or 0.0)

        # --- Missing payout detection (gross = 0 but units present) ---
        if units > 0 and gross == 0.0:
            anomalies.append(
                {
                    "artist_id": artist_id,
                    "anomaly_type": "missing_creator_payout",
                    "platform": platform,
                    "period": period,
                    "description": (
                        f"{platform} shows {units:,.0f} units for {period} but $0 payout."
                    ),
                    "estimated_recovery": None,
                    "confidence": 0.85,
                    "rule_id": "CE001",
                }
            )

        # --- CPM / CPP below benchmark ---
        bench = _PLATFORM_CPM_BENCHMARKS.get(platform, 0.0)
        if bench > 0 and units > 0:
            actual_cpm = (gross / units) * 1000
            if actual_cpm < bench:
                gap = (bench - actual_cpm) * (units / 1000)
                anomalies.append(
                    {
                        "artist_id": artist_id,
                        "anomaly_type": "below_benchmark_cpm",
                        "platform": platform,
                        "period": period,
                        "description": (
                            f"{platform} CPM ${actual_cpm:.4f} is below industry "
                            f"floor ${bench:.4f} for {period}."
                        ),
                        "estimated_recovery": round(gap, 2),
                        "confidence": 0.72,
                        "rule_id": "CE002",
                    }
                )

        # --- Shopify merch gap: refunds > 50 % of gross ---
        if platform == "shopify":
            refunds = float(ev.get("refunds") or 0.0)
            if gross > 0 and refunds / gross > 0.50:
                anomalies.append(
                    {
                        "artist_id": artist_id,
                        "anomaly_type": "high_merch_refund_rate",
                        "platform": "shopify",
                        "period": period,
                        "description": (
                            f"Shopify refunds {refunds/gross*100:.1f}% of gross for {period} — "
                            "possible fulfilment/fraud issue."
                        ),
                        "estimated_recovery": None,
                        "confidence": 0.65,
                        "rule_id": "CE003",
                    }
                )

        # --- TikTok CPP zero payment with views ---
        if platform == "tiktok_creator_fund":
            cpp = float(ev.get("cpp") or 0.0)
            if units > 1_000 and cpp == 0.0:
                anomalies.append(
                    {
                        "artist_id": artist_id,
                        "anomaly_type": "tiktok_zero_cpp",
                        "platform": "tiktok_creator_fund",
                        "period": period,
                        "description": (
                            f"TikTok reports {units:,.0f} views for {period} with $0 CPP reward."
                        ),
                        "estimated_recovery": round(units / 1000 * 0.02, 2),
                        "confidence": 0.70,
                        "rule_id": "CE004",
                    }
                )

    return anomalies
