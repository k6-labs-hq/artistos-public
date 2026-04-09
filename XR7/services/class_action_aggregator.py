"""Pillar 8 — Class-action evidence aggregator.

Watches for common payer-drift anomalies across multiple artists and
automatically promotes threshold clusters to class-action signal packets.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly
from XR7.models.class_action_signal import ClassActionSignal
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# Minimum number of distinct artists to trigger a class-action signal
_MIN_ARTISTS_THRESHOLD = 3
# Minimum total estimated loss (USD) to trigger packet generation
_MIN_TOTAL_LOSS_THRESHOLD = 500.0


def aggregate_class_action_signals(db: Session) -> list[dict[str, Any]]:
    """Scan recent anomalies, cluster by payer+type, create/update signals."""
    # Group open anomalies by subtype+category as a practical payer/type proxy.
    rows = (
        db.query(
            Anomaly.subtype,
            Anomaly.category,
            func.count(func.distinct(Anomaly.artist_id)).label("artist_count"),
            func.sum(Anomaly.estimated_recoverable).label("total_loss"),
        )
        .filter(Anomaly.subtype.is_not(None), Anomaly.status != "CLOSED")
        .group_by(Anomaly.subtype, Anomaly.category)
        .having(func.count(func.distinct(Anomaly.artist_id)) >= _MIN_ARTISTS_THRESHOLD)
        .all()
    )

    created_or_updated: list[dict[str, Any]] = []

    for row in rows:
        payer = str(row.subtype or "unknown")
        atype = str(row.category or "unknown")
        count = int(row.artist_count or 0)
        total_loss = float(row.total_loss or 0.0)

        if total_loss < _MIN_TOTAL_LOSS_THRESHOLD:
            continue

        # Fetch contributing artist IDs
        affected = (
            db.query(Anomaly.artist_id)
            .filter(Anomaly.subtype == payer, Anomaly.category == atype)
            .distinct()
            .all()
        )
        artist_ids = [r.artist_id for r in affected]

        # Upsert signal
        signal = (
            db.query(ClassActionSignal)
            .filter(
                ClassActionSignal.payer_name == payer,
                ClassActionSignal.anomaly_type == atype,
                ClassActionSignal.status == "active",
            )
            .first()
        )
        if signal:
            signal.affected_artist_count = count
            signal.total_estimated_loss = round(total_loss, 2)
            signal.contributing_artist_ids = {"artist_ids": artist_ids}
            signal.last_updated_at = datetime.now(timezone.utc)
        else:
            signal = ClassActionSignal(
                payer_name=payer,
                anomaly_type=atype,
                affected_artist_count=count,
                total_estimated_loss=round(total_loss, 2),
                contributing_artist_ids={"artist_ids": artist_ids},
                status="active",
            )
            db.add(signal)

        db.commit()
        db.refresh(signal)
        logger.info(
            "class_action_signal_upserted",
            extra={"payer": payer, "type": atype, "count": count, "loss": total_loss},
        )
        created_or_updated.append(
            {
                "id": signal.id,
                "payer_name": payer,
                "anomaly_type": atype,
                "affected_artist_count": count,
                "total_estimated_loss": round(total_loss, 2),
                "status": signal.status,
            }
        )

    return created_or_updated


def get_active_signals(db: Session) -> list[dict[str, Any]]:
    signals = (
        db.query(ClassActionSignal)
        .filter(ClassActionSignal.status == "active")
        .order_by(ClassActionSignal.total_estimated_loss.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "payer_name": s.payer_name,
            "anomaly_type": s.anomaly_type,
            "affected_artist_count": s.affected_artist_count,
            "total_estimated_loss": s.total_estimated_loss,
            "currency": s.currency,
            "status": s.status,
            "first_detected_at": s.first_detected_at.isoformat() if s.first_detected_at else None,
            "last_updated_at": s.last_updated_at.isoformat() if s.last_updated_at else None,
        }
        for s in signals
    ]
