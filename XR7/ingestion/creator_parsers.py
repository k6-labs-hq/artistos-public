"""Pillar 4 — Creator-economy expanded parsers.

Handles YouTube Studio, TikTok Creator Fund, Instagram Reels Bonuses,
Twitch, Patreon, and Shopify Merch statement formats.  Each parser
returns a list of UniversalRoyaltyEvent-compatible dicts.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _clean_currency(raw: str | None) -> float:
    if not raw:
        return 0.0
    return float(re.sub(r"[^\d.\-]", "", str(raw)) or 0)


def _row_to_event(
    *,
    platform: str,
    period: str,
    stream_type: str,
    gross_amount: float,
    currency: str = "USD",
    units: float | None = None,
    rate: float | None = None,
    title: str | None = None,
    territory: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "platform": platform,
        "period": period,
        "stream_type": stream_type,
        "gross_amount": gross_amount,
        "currency": currency,
        "units": units,
        "rate": rate,
        "title": title,
        "territory": territory,
        **(extra or {}),
    }


# ---------------------------------------------------------------------------
# YouTube Studio parser
# ---------------------------------------------------------------------------


def parse_youtube_studio(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Parse YouTube Studio monthly revenue export rows."""
    events: list[dict[str, Any]] = []
    for row in rows:
        amount = _clean_currency(row.get("Estimated Revenue") or row.get("revenue"))
        if amount == 0.0:
            continue
        events.append(
            _row_to_event(
                platform="youtube_studio",
                period=str(row.get("Month") or row.get("period") or ""),
                stream_type=str(row.get("Content Type") or "video"),
                gross_amount=amount,
                currency=str(row.get("Currency") or "USD"),
                units=_clean_currency(row.get("Views") or row.get("views")),
                title=str(row.get("Video Title") or row.get("title") or ""),
                territory=str(row.get("Country") or row.get("territory") or ""),
                extra={"rpm": _clean_currency(row.get("Revenue Per Mille (RPM)"))},
            )
        )
    return events


# ---------------------------------------------------------------------------
# TikTok Creator Fund parser
# ---------------------------------------------------------------------------


def parse_tiktok_creator_fund(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Parse TikTok Creator Fund payment export rows."""
    events: list[dict[str, Any]] = []
    for row in rows:
        amount = _clean_currency(row.get("Amount") or row.get("amount"))
        if amount == 0.0:
            continue
        events.append(
            _row_to_event(
                platform="tiktok_creator_fund",
                period=str(row.get("Payment Date") or row.get("period") or ""),
                stream_type="creator_fund_payout",
                gross_amount=amount,
                currency=str(row.get("Currency") or "USD"),
                units=_clean_currency(row.get("Video Views") or row.get("views")),
                extra={"cpp": _clean_currency(row.get("Rewards Per 1000 Views"))},
            )
        )
    return events


# ---------------------------------------------------------------------------
# Instagram Reels Bonus parser
# ---------------------------------------------------------------------------


def parse_instagram_reels_bonus(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for row in rows:
        amount = _clean_currency(row.get("Bonus Amount") or row.get("amount"))
        if amount == 0.0:
            continue
        events.append(
            _row_to_event(
                platform="instagram_reels",
                period=str(row.get("Date") or row.get("period") or ""),
                stream_type="reels_play_bonus",
                gross_amount=amount,
                currency=str(row.get("Currency") or "USD"),
                units=_clean_currency(row.get("Plays") or row.get("views")),
            )
        )
    return events


# ---------------------------------------------------------------------------
# Twitch parser
# ---------------------------------------------------------------------------


def parse_twitch(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for row in rows:
        amount = _clean_currency(row.get("Net Amount") or row.get("amount"))
        if amount == 0.0:
            continue
        events.append(
            _row_to_event(
                platform="twitch",
                period=str(row.get("Payout Period") or row.get("period") or ""),
                stream_type=str(row.get("Revenue Type") or "subscription"),
                gross_amount=amount,
                currency=str(row.get("Currency") or "USD"),
                extra={"gross": _clean_currency(row.get("Gross Amount"))},
            )
        )
    return events


# ---------------------------------------------------------------------------
# Patreon parser
# ---------------------------------------------------------------------------


def parse_patreon(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for row in rows:
        amount = _clean_currency(row.get("Net Amount Paid Out") or row.get("amount"))
        if amount == 0.0:
            continue
        events.append(
            _row_to_event(
                platform="patreon",
                period=str(row.get("Date") or row.get("period") or ""),
                stream_type=str(row.get("Type") or "pledge_payout"),
                gross_amount=amount,
                currency=str(row.get("Currency") or "USD"),
                units=_clean_currency(row.get("Patron Count") or row.get("patrons")),
            )
        )
    return events


# ---------------------------------------------------------------------------
# Shopify Merch parser
# ---------------------------------------------------------------------------


def parse_shopify_merch(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for row in rows:
        amount = _clean_currency(row.get("Net Sales") or row.get("net_sales"))
        if amount == 0.0:
            continue
        events.append(
            _row_to_event(
                platform="shopify",
                period=str(row.get("Day") or row.get("period") or ""),
                stream_type="merch_sale",
                gross_amount=amount,
                currency=str(row.get("Currency") or "USD"),
                units=_clean_currency(row.get("Net Quantity") or row.get("quantity")),
                title=str(row.get("Product Title") or row.get("title") or ""),
                extra={"refunds": _clean_currency(row.get("Refunds"))},
            )
        )
    return events


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

CREATOR_PARSERS: dict[str, Any] = {
    "youtube_studio": parse_youtube_studio,
    "tiktok_creator_fund": parse_tiktok_creator_fund,
    "instagram_reels": parse_instagram_reels_bonus,
    "twitch": parse_twitch,
    "patreon": parse_patreon,
    "shopify": parse_shopify_merch,
}


def parse_creator_platform(platform: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    parser = CREATOR_PARSERS.get(platform)
    if not parser:
        raise ValueError(f"No creator-economy parser found for platform: {platform!r}")
    return parser(rows)
