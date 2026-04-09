from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from XR7.recovery.black_box_expiration import register_society_freeze_event
from XR7.recovery.recoverability_classifier import build_recoverability_payload


@dataclass
class SignalLogEntry:
    source: str
    signal_type: str
    payer_or_society: str
    timestamp: str
    affected_anomaly_count: int
    classification_impact: dict[str, int]


class SocietySignalFeed:
    """Monitor and apply society redistribution/matching/regulatory signals."""

    def __init__(self) -> None:
        self.signal_log: list[SignalLogEntry] = []

    def parse_signal(self, signal: dict[str, Any]) -> dict[str, Any]:
        kind = str(signal.get("signal_type") or "unknown").lower()
        payer = str(signal.get("payer_or_society") or "GENERIC").upper()
        freeze = kind in {"redistribution_pause", "matching_pause"}
        return {
            "signal_type": kind,
            "payer_or_society": payer,
            "freeze_event": freeze,
            "royalty_type": str(signal.get("royalty_type") or "unmatched_royalties").lower(),
            "effective_at": str(
                signal.get("effective_at") or datetime.now(timezone.utc).isoformat()
            ),
            "source": str(signal.get("source") or "partner_feed"),
            "raw": signal,
        }

    def apply_signal(
        self, signal: dict[str, Any], anomalies: list[dict[str, Any]]
    ) -> dict[str, Any]:
        parsed = self.parse_signal(signal)
        target_payer = parsed["payer_or_society"]
        before_after: dict[str, int] = {}
        affected = 0

        if parsed["freeze_event"]:
            register_society_freeze_event(
                payer_or_society=target_payer,
                royalty_type=parsed["royalty_type"],
                freeze_started_at=parsed["effective_at"],
                source=parsed["source"],
                note=f"Signal feed: {parsed['signal_type']}",
            )

        updates: list[dict[str, Any]] = []
        for anomaly in anomalies:
            payer = str(
                anomaly.get("payer") or anomaly.get("society") or anomaly.get("subtype") or ""
            ).upper()
            if target_payer not in payer and target_payer != "GENERIC":
                continue
            affected += 1
            previous = str(
                (anomaly.get("recoverability") or {}).get("recoverability_class")
                or anomaly.get("recoverability_class")
                or "UNSET"
            )
            new_payload = build_recoverability_payload(anomaly)
            new_class = str(
                (new_payload.get("recoverability") or {}).get("recoverability_class") or "UNSET"
            )
            before_after[f"{previous}->{new_class}"] = (
                before_after.get(f"{previous}->{new_class}", 0) + 1
            )
            updates.append(
                {
                    "anomaly_id": anomaly.get("id"),
                    "previous_class": previous,
                    "new_class": new_class,
                    "urgent_flag": bool(
                        (new_payload.get("black_box_expiration") or {}).get(
                            "days_remaining", 999999
                        )
                        <= 90
                    ),
                }
            )

        entry = SignalLogEntry(
            source=parsed["source"],
            signal_type=parsed["signal_type"],
            payer_or_society=parsed["payer_or_society"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            affected_anomaly_count=affected,
            classification_impact=before_after,
        )
        self.signal_log.append(entry)

        return {
            "signal": parsed,
            "affected_anomaly_count": affected,
            "classification_impact": before_after,
            "updates": updates,
            "signal_log_entry": {
                "source": entry.source,
                "signal_type": entry.signal_type,
                "payer_or_society": entry.payer_or_society,
                "timestamp": entry.timestamp,
                "affected_anomaly_count": entry.affected_anomaly_count,
                "classification_impact": entry.classification_impact,
            },
        }

    def dashboard_feed(self) -> list[dict[str, Any]]:
        return [
            {
                "source": row.source,
                "signal_type": row.signal_type,
                "payer_or_society": row.payer_or_society,
                "timestamp": row.timestamp,
                "affected_anomaly_count": row.affected_anomaly_count,
                "classification_impact": row.classification_impact,
            }
            for row in self.signal_log[-100:]
        ]
