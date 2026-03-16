from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.contract import Contract
from XR7.models.event import Event
from XR7.models.payment import Payment


@dataclass
class RateDriftReport:
    artist_id: str
    issues_found: int
    contract_discrepancies: list[dict[str, Any]]
    discrepancy_reports: list[dict[str, Any]]
    projected_future_leakage: float


class RateDriftCorrectionEngine:
    def __init__(self, db: Session):
        self.db = db

    def _extract_expected_rate(self, contract: Contract) -> float | None:
        terms = contract.terms or {}
        for key in ("expected_rate", "royalty_rate", "stream_rate", "unit_rate"):
            value = terms.get(key)
            if value is None:
                continue
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
        return None

    def _contract_term_discrepancies(self, artist_id: str, events: list[Event], contracts: list[Contract]) -> list[dict[str, Any]]:
        if not events:
            return []
        avg_rate = sum(float(e.unit_value or 0.0) for e in events) / max(len(events), 1)
        rows: list[dict[str, Any]] = []
        for contract in contracts:
            expected = self._extract_expected_rate(contract)
            if expected is None:
                continue
            drift = expected - avg_rate
            if abs(drift) < 1e-6:
                continue
            rows.append(
                {
                    "contract_id": contract.id,
                    "counterparty": contract.counterparty,
                    "expected_rate": round(expected, 6),
                    "actual_avg_rate": round(avg_rate, 6),
                    "drift": round(drift, 6),
                    "issue": "OUTDATED_CONTRACT_TERMS" if drift > 0 else "RATE_ABOVE_TERMS_REVIEW",
                }
            )
        return rows

    def detect_and_record(self, artist_id: str) -> RateDriftReport:
        events = self.db.query(Event).filter(Event.artist_id == artist_id).all()
        payments = self.db.query(Payment).filter(Payment.artist_id == artist_id).all()
        contracts = self.db.query(Contract).filter(Contract.artist_id == artist_id).all()

        contract_rows = self._contract_term_discrepancies(artist_id, events, contracts)

        discrepancy_reports: list[dict[str, Any]] = []
        if events:
            backend_expected = sum(float(e.unit_value or 0.0) * float(e.quantity or 0.0) for e in events)
            backend_received = sum(float(p.amount or 0.0) for p in payments)
            missing_backend = max(0.0, backend_expected - backend_received)
            if missing_backend > 0.0:
                discrepancy_reports.append(
                    {
                        "issue": "MISSING_BACKEND_SYNC",
                        "expected": round(backend_expected, 2),
                        "received": round(backend_received, 2),
                        "delta": round(missing_backend, 2),
                    }
                )

        foreign_events = [e for e in events if (e.territory or "US").upper() not in {"US", "USA"}]
        foreign_payments = [p for p in payments if str(p.source or "").strip().upper() in {"FOREIGN", "SUB_PUBLISHER", "CMO"}]
        if foreign_events and not foreign_payments:
            discrepancy_reports.append(
                {
                    "issue": "MISSING_FOREIGN_SUB_PUBLISHER_PAYMENTS",
                    "event_count": len(foreign_events),
                    "payment_count": 0,
                }
            )

        issues_found = len(contract_rows) + len(discrepancy_reports)
        projected = 0.0
        for row in contract_rows:
            projected += max(0.0, float(row.get("drift") or 0.0)) * 10000
        for row in discrepancy_reports:
            projected += float(row.get("delta") or 250.0)
        projected = round(projected, 2)

        if issues_found > 0:
            existing = (
                self.db.query(Anomaly)
                .filter(
                    Anomaly.artist_id == artist_id,
                    Anomaly.subtype == "RATE_DRIFT_FUTURE_RISK",
                    Anomaly.status == AnomalyStatus.OPEN,
                )
                .first()
            )
            description = "Detected contract-rate drift and accounting inconsistencies that can cause future leakage."
            if existing:
                existing.estimated_recoverable = projected
                existing.description = description
                existing.confidence_score = 0.82
            else:
                self.db.add(
                    Anomaly(
                        artist_id=artist_id,
                        category=AnomalyCategory.ROYALTY,
                        subtype="RATE_DRIFT_FUTURE_RISK",
                        severity=AnomalySeverity.HIGH if projected > 1000 else AnomalySeverity.MEDIUM,
                        estimated_recoverable=projected,
                        confidence_score=0.82,
                        status=AnomalyStatus.OPEN,
                        description=description,
                        time_window_end=datetime.now(timezone.utc),
                    )
                )

        self.db.commit()
        return RateDriftReport(
            artist_id=artist_id,
            issues_found=issues_found,
            contract_discrepancies=contract_rows,
            discrepancy_reports=discrepancy_reports,
            projected_future_leakage=projected,
        )
