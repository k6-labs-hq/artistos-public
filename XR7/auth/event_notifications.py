from __future__ import annotations

from XR7.auth.notification_service import get_notification_service
from XR7.models.notification_preference import NotificationPreference
from XR7.services.branding import apply_brand_placeholders, communication_templates, get_branding_profile


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
    org_id: str | None = None,
    db=None,
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

    brand = get_branding_profile(db, org_id)
    template_key = {
        "anomaly_detected": "anomaly_alert",
        "urgent_sol": "sol_urgency",
        "deposit_received": "deposit_notification",
        "claim_advanced": "claim_update",
    }.get(event_key)
    templates = communication_templates()
    selected = templates.get(template_key or "", {})
    source_title = selected.get("subject") or title
    source_body = selected.get("body") or body
    branded_title = apply_brand_placeholders(source_title, brand)
    branded_body = apply_brand_placeholders(source_body, brand)

    if pref.phone:
        sms_sent = svc.send_sms(pref.phone, f"{branded_title}: {branded_body}")
    if pref.email:
        email_sent = svc.send_email(pref.email, branded_title, branded_body)

    return {
        "sent": bool(sms_sent or email_sent),
        "sms_sent": sms_sent,
        "email_sent": email_sent,
        "rendered": {
            "title": branded_title,
            "body": branded_body,
        },
    }
