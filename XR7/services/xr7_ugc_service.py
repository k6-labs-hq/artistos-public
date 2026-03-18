from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from XR7.models.xr7_royalty import XR7MatchMethod, XR7SourceCategory, XR7UsageEvent


def _now() -> datetime:
    return datetime.now(timezone.utc)


def ingest_ugc_signals(
    db: Session,
    *,
    tenant_id: str,
    artist_id: str,
    platform: str,
    signals: list[dict[str, object]],
) -> dict[str, object]:
    accepted = 0
    rejected = 0

    for signal in signals:
        content_id = str(signal.get("ugc_content_id") or "").strip()
        if not content_id:
            rejected += 1
            continue

        units = float(signal.get("units") or 1.0)
        estimated_rate = float(signal.get("estimated_rate") or 0.001)
        estimated_value = round(units * estimated_rate, 6)
        confidence = float(signal.get("confidence") or 0.7)

        event = XR7UsageEvent(
            tenant_id=tenant_id,
            artist_id=artist_id,
            platform=platform,
            event_type="ugc_detection",
            event_timestamp=_now(),
            territory=str(signal.get("territory") or "GLOBAL"),
            channel="ugc",
            units=units,
            asset_ref=str(signal.get("asset_ref") or content_id),
            match_method=XR7MatchMethod.FINGERPRINT,
            confidence_score=confidence,
            monetization_estimate=estimated_value,
            currency=str(signal.get("currency") or "USD"),
            source_category=XR7SourceCategory.FINGERPRINT,
            raw_ref=content_id,
            ugc_content_id=content_id,
            ugc_format=str(signal.get("ugc_format") or "short_form"),
            ugc_video_duration_sec=int(signal.get("ugc_video_duration_sec") or 0) or None,
            remix_parent_ref=str(signal.get("remix_parent_ref") or "") or None,
            trend_cluster_id=str(signal.get("trend_cluster_id") or "") or None,
            short_form_signal_strength=float(signal.get("signal_strength") or confidence),
            black_box_risk_score=max(0.0, min(1.0, 1.0 - confidence)),
            explainability_json=json.dumps(
                {
                    "driver": "ugc_signal_ingestion",
                    "confidence": confidence,
                    "units": units,
                    "estimated_rate": estimated_rate,
                },
                sort_keys=True,
            ),
        )
        db.add(event)
        accepted += 1

    db.commit()
    return {
        "accepted": accepted,
        "rejected": rejected,
        "ingestion_ref": f"ugc:{artist_id}:{int(_now().timestamp())}",
    }


def get_ugc_opportunities(
    db: Session,
    *,
    tenant_id: str,
    artist_id: str,
    min_confidence: float = 0.65,
    min_estimated_value: float = 0.0,
    status: str | None = None,
) -> list[dict[str, object]]:
    _ = status
    rows = (
        db.query(XR7UsageEvent)
        .filter(
            XR7UsageEvent.tenant_id == tenant_id,
            XR7UsageEvent.artist_id == artist_id,
            XR7UsageEvent.ugc_content_id.isnot(None),
            XR7UsageEvent.confidence_score >= min_confidence,
            XR7UsageEvent.monetization_estimate >= min_estimated_value,
        )
        .order_by(XR7UsageEvent.monetization_estimate.desc())
        .limit(200)
        .all()
    )

    return [
        {
            "usage_event_id": row.id,
            "platform": row.platform,
            "ugc_content_id": row.ugc_content_id,
            "territory": row.territory,
            "estimated_value": row.monetization_estimate,
            "confidence": row.confidence_score,
            "black_box_risk_score": row.black_box_risk_score,
            "trend_cluster_id": row.trend_cluster_id,
        }
        for row in rows
    ]
