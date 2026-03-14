from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from XR7.auth.notification_service import MockNotificationService
from XR7.models.anomaly import Anomaly
from XR7.models.claim import Claim
from XR7.models.notification_preference import NotificationPreference
from XR7.recovery.deadline_risk_engine import evaluate_deadline_risk


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def build_weekly_digest(
    artist_id: str,
    anomalies: list[Anomaly],
    claims: list[Claim],
    contracts: list[dict[str, Any]],
    payments: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the weekly artist digest payload used by API and scheduled jobs."""
    now = _utc_now()
    week_ago = now - timedelta(days=7)

    new_anomalies = [a for a in anomalies if (a.created_at or now) >= week_ago]
    advanced_claims = [
        c for c in claims
        if (c.updated_at or now) >= week_ago and str(c.status) not in {"IDENTIFIED", "PREPARED"}
    ]
    expected_additional_recovery = sum(float(a.estimated_recoverable or 0.0) for a in new_anomalies)

    risk = evaluate_deadline_risk(
        anomalies=[
            {
                "id": a.id,
                "category": str(a.category),
                "subtype": a.subtype,
                "territory": a.territory,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "estimated_recoverable": float(a.estimated_recoverable or 0.0),
            }
            for a in anomalies
        ],
        claims=[
            {
                "id": c.id,
                "status": str(c.status),
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in claims
        ],
        contracts=contracts,
        payments=payments,
    )

    blocked_items = [
        {
            "claim_id": c.id,
            "status": str(c.status),
            "reason": "Awaiting payer response beyond expected SLA",
        }
        for c in claims
        if str(c.status) in {"SUBMITTED", "FILED", "IN_REVIEW"}
    ][:10]

    return {
        "artist_id": artist_id,
        "generated_at": now.isoformat(),
        "new_anomalies": len(new_anomalies),
        "claims_advanced": len(advanced_claims),
        "expected_additional_recovery": round(expected_additional_recovery, 2),
        "blocked_items": blocked_items,
        "upcoming_deadlines": risk,
        "in_app_feed": [
            f"{len(new_anomalies)} new anomalies detected this week.",
            f"{len(advanced_claims)} claims advanced stages.",
            f"Deadline risk color: {risk.get('risk_color')}",
        ],
    }


def deliver_weekly_digest(
    digest: dict[str, Any],
    preference: NotificationPreference | None,
    email: str | None = None,
    sms_number: str | None = None,
) -> dict[str, Any]:
    """Best-effort digest delivery to in-app, email, and SMS channels."""
    service = MockNotificationService()
    subject = "XR7 Weekly Recovery Digest"
    body = (
        f"New anomalies: {digest.get('new_anomalies')}\n"
        f"Claims advanced: {digest.get('claims_advanced')}\n"
        f"Expected additional recovery: ${digest.get('expected_additional_recovery')}\n"
        f"Deadline risk: {((digest.get('upcoming_deadlines') or {}).get('risk_color'))}\n"
    )

    delivered = {
        "in_app": True,
        "email": False,
        "sms": False,
    }

    if email and (preference is None or bool(getattr(preference, "email_enabled", True))):
        delivered["email"] = bool(service.send_email(email, subject, body))

    if sms_number and (preference is None or bool(getattr(preference, "sms_enabled", False))):
        delivered["sms"] = bool(service.send_sms(sms_number, body[:280]))

    return delivered
