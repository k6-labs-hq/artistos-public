from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.ml.forecaster import EarningsForecaster
from XR7.models.claim import Claim
from XR7.models.payment import Payment


class FinancingMarketplace:
    def match_to_financiers(self, catalog_value: dict[str, Any]) -> list[dict[str, Any]]:
        value = float(catalog_value.get("catalog_value_total") or 0.0)
        return [
            {"name": "Apex Music Capital", "estimated_advance": round(value * 0.2, 2), "api_mode": "placeholder"},
            {"name": "Bluebird Royalty Finance", "estimated_advance": round(value * 0.15, 2), "api_mode": "placeholder"},
        ]

    def generate_financing_terms(self, catalog_value: dict[str, Any]) -> str:
        value = float(catalog_value.get("catalog_value_total") or 0.0)
        return (
            "# Financing Terms Draft\n\n"
            f"Catalog Value Basis: ${value:,.2f}\n"
            "- Advance structure: tiered by recoupment velocity\n"
            "- Security: royalty receivable assignment\n"
            "- Settlement: monthly with transparent ledger access\n"
        )


class CatalogValuationEngine:
    def __init__(self, db: Session):
        self.db = db
        self.forecaster = EarningsForecaster()
        self.market = FinancingMarketplace()

    def calculate_catalog_value(self, artist_id: str) -> dict[str, Any]:
        payments = self.db.query(Payment).filter(Payment.artist_id == artist_id).all()
        claims = self.db.query(Claim).filter(Claim.artist_id == artist_id).all()
        trailing = sum(float(p.amount or 0.0) for p in payments)
        forecast = self.forecaster.forecast([], horizon_days=90)
        projected = float(forecast.get("predicted_total") or 0.0)
        multiple = 4.2
        total = round((trailing + projected) * multiple + sum(float(c.recovered_amount or 0.0) for c in claims), 2)
        return {
            "artist_id": artist_id,
            "catalog_value_total": total,
            "breakdown": {
                "trailing_earnings": round(trailing, 2),
                "projected_90d": round(projected, 2),
                "market_multiple": multiple,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def generate_financing_matches(self, catalog_value: dict[str, Any]) -> list[dict[str, Any]]:
        return self.market.match_to_financiers(catalog_value)

    async def export_valuation_report_with_anchor(self, artist_id: str) -> dict[str, Any]:
        value = self.calculate_catalog_value(artist_id)
        terms = self.market.generate_financing_terms(value)
        payload = {"valuation": value, "terms": terms}
        # Anchoring is handled by the service layer; return unanchored report here.
        return payload
