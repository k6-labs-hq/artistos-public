from __future__ import annotations

from XR7.auth.notification_service import get_notification_service
from XR7.models.notification_preference import NotificationPreference


def _is_within_quiet_hours(pref: NotificationPreference, hour_24: int) -> bool:
    if not pref.quiet_hours_start or not pref.quiet_hours_end:
        return False

    try:
        start = int(pref.quiet_hours_start.split(":")[0])
        end = int(pref.quiet_hours_end.split(":")[0])
    except Exception:
        return False

    if start == end:
        return False
    if start < end:
        return start <= hour_24 < end
    return hour_24 >= start or hour_24 < end


def send_event_notification(
    pref: NotificationPreference | None,
    event_key: str,
    title: str,
    body: str,
    *,
    current_hour_utc: int,
) -> dict:
    if not pref:
        return {"sent": False, "reason": "no_preferences"}

    allowed = {
        "anomaly_detected": pref.notify_anomaly_detected,
        "urgent_sol": pref.notify_urgent_sol,
        "deposit_received": pref.notify_deposit_received,
        "claim_advanced": pref.notify_claim_advanced,
    }.get(event_key, False)

    if not allowed:
        return {"sent": False, "reason": "event_disabled"}

    if _is_within_quiet_hours(pref, current_hour_utc):
        return {"sent": False, "reason": "quiet_hours"}

    svc = get_notification_service()
    sms_sent = False
    email_sent = False

    if pref.phone:
        sms_sent = svc.send_sms(pref.phone, f"{title}: {body}")
    if pref.email:
        email_sent = svc.send_email(pref.email, title, body)

    return {
        "sent": bool(sms_sent or email_sent),
        "sms_sent": sms_sent,
        "email_sent": email_sent,
    }
