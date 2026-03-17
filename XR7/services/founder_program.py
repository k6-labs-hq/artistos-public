from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from XR7.auth.event_notifications import send_event_notification
from XR7.models.artist import Artist, ArtistLifecycleStatus
from XR7.models.notification_preference import NotificationPreference
from XR7.models.platform_config import PlatformConfig
from xr7_common.logging import get_logger


logger = get_logger(__name__)


@dataclass
class FounderAssignmentResult:
    assigned: bool
    is_founder: bool
    slot_number: int | None
    slots_filled: int
    slots_remaining: int
    slots_total: int
    founder_fee_percent: float
    cohort_open: bool
    milestone: str | None


def _safe_float(raw: str | None) -> float | None:
    if raw is None:
        return None
    try:
        return float(raw)
    except Exception:  # noqa: BLE001
        return None


def get_or_create_platform_config(db: Session, *, for_update: bool = False) -> PlatformConfig:
    query = db.query(PlatformConfig).filter(PlatformConfig.id == 1)
    if for_update:
        query = query.with_for_update()
    row = query.first()
    if row:
        return row

    row = PlatformConfig(id=1)
    env_fee = _safe_float(os.environ.get("XR7_STANDARD_CONTINGENCY_FEE_PERCENT"))
    if env_fee is None:
        env_fee = _safe_float(os.environ.get("TROLLEY_PLATFORM_FEE_PERCENT"))
    if env_fee is not None:
        row.standard_contingency_fee_percent = env_fee
    db.add(row)
    db.flush()
    return row


def resolve_standard_fee_percent(config: PlatformConfig) -> float:
    if config.standard_contingency_fee_percent is not None:
        return float(config.standard_contingency_fee_percent)

    env_fee = _safe_float(os.environ.get("XR7_STANDARD_CONTINGENCY_FEE_PERCENT"))
    if env_fee is None:
        env_fee = _safe_float(os.environ.get("TROLLEY_PLATFORM_FEE_PERCENT"))
    if env_fee is not None:
        return env_fee

    return float(config.founder_fee_percent)


def founder_status_payload(db: Session) -> dict[str, int | float | bool]:
    cfg = get_or_create_platform_config(db)
    total = int(cfg.founder_cohort_limit)
    filled = int(cfg.founder_slots_filled)
    remaining = max(0, total - filled)
    return {
        "slots_total": total,
        "slots_filled": filled,
        "slots_remaining": remaining,
        "founder_fee_percent": float(cfg.founder_fee_percent),
        "cohort_open": filled < total,
    }


def assign_founder_slot_on_activation(db: Session, artist: Artist) -> FounderAssignmentResult:
    cfg = get_or_create_platform_config(db, for_update=True)
    slots_total = int(cfg.founder_cohort_limit)
    slots_filled = int(cfg.founder_slots_filled)
    founder_fee = float(cfg.founder_fee_percent)

    # Idempotency: if the artist already has a slot, keep it unchanged.
    if bool(artist.is_founder) and artist.founder_slot_number is not None:
        remaining = max(0, slots_total - slots_filled)
        return FounderAssignmentResult(
            assigned=False,
            is_founder=True,
            slot_number=int(artist.founder_slot_number),
            slots_filled=slots_filled,
            slots_remaining=remaining,
            slots_total=slots_total,
            founder_fee_percent=founder_fee,
            cohort_open=slots_filled < slots_total,
            milestone=None,
        )

    milestone = None
    now = datetime.now(timezone.utc)
    if slots_filled < slots_total:
        next_slot = slots_filled + 1
        artist.is_founder = True
        artist.founder_slot_number = next_slot
        artist.founder_locked_at = now
        artist.contingency_fee_percent = founder_fee

        cfg.founder_slots_filled = next_slot
        slots_filled = next_slot
        if slots_filled == 2000:
            milestone = "last_500"
        elif slots_filled == 2400:
            milestone = "last_100"
        elif slots_filled == slots_total:
            milestone = "closed"

        return FounderAssignmentResult(
            assigned=True,
            is_founder=True,
            slot_number=next_slot,
            slots_filled=slots_filled,
            slots_remaining=max(0, slots_total - slots_filled),
            slots_total=slots_total,
            founder_fee_percent=founder_fee,
            cohort_open=slots_filled < slots_total,
            milestone=milestone,
        )

    artist.is_founder = False
    artist.founder_slot_number = None
    artist.founder_locked_at = None
    artist.contingency_fee_percent = resolve_standard_fee_percent(cfg)

    return FounderAssignmentResult(
        assigned=True,
        is_founder=False,
        slot_number=None,
        slots_filled=slots_filled,
        slots_remaining=max(0, slots_total - slots_filled),
        slots_total=slots_total,
        founder_fee_percent=founder_fee,
        cohort_open=False,
        milestone=None,
    )


def _upsert_pref_for_artist(db: Session, artist: Artist) -> NotificationPreference:
    pref = db.query(NotificationPreference).filter(NotificationPreference.artist_id == artist.id).first()
    if pref is None:
        pref = NotificationPreference(artist_id=artist.id)
        db.add(pref)

    if not pref.email and artist.email:
        pref.email = artist.email

    db.flush()
    return pref


def _notify_founder_slot_confirmed(
    db: Session,
    artist: Artist,
    result: FounderAssignmentResult,
    *,
    referral_link: str,
) -> None:
    pref = _upsert_pref_for_artist(db, artist)
    send_event_notification(
        pref,
        "founder_slot_confirmed",
        title=f"You're Founder #{result.slot_number} - your {int(result.founder_fee_percent)}% rate is locked for life",
        body=(
            f"You just became one of XR7's {result.slots_total} founding artists.\n\n"
            f"Your contingency fee is locked at {int(result.founder_fee_percent)}% permanently - on every "
            "claim you ever file through XR7, for as long as you use the platform.\n\n"
            f"{result.slots_remaining} founder slots remain. If you know other artists who should be in "
            f"this group, send them to {referral_link}.\n\n"
            "Welcome to the founding cohort."
        ),
        current_hour_utc=datetime.now(timezone.utc).hour,
        db=db,
    )


def _notify_non_activated_artists(db: Session, event_key: str, title: str, body: str) -> None:
    rows = db.query(Artist).filter(Artist.status == ArtistLifecycleStatus.ONBOARDED.value).all()
    for artist in rows:
        pref = _upsert_pref_for_artist(db, artist)
        if not pref.email and not pref.phone:
            continue
        send_event_notification(
            pref,
            event_key,
            title=title,
            body=body,
            current_hour_utc=datetime.now(timezone.utc).hour,
            db=db,
        )


def handle_founder_notifications(db: Session, artist: Artist, result: FounderAssignmentResult) -> None:
    if not result.assigned:
        return

    referral_link = os.environ.get("XR7_FOUNDER_REFERRAL_LINK", "https://xr7.com/referral")
    if result.is_founder:
        _notify_founder_slot_confirmed(db, artist, result, referral_link=referral_link)

    if result.milestone == "last_500":
        _notify_non_activated_artists(
            db,
            "founder_slots_closing",
            "500 founder slots remaining - upload your first statement to lock in 10% for life",
            "500 founder slots remain. Upload your first statement to lock in 10% for life.",
        )
    elif result.milestone == "last_100":
        _notify_non_activated_artists(
            db,
            "founder_slots_almost_gone",
            "Only 100 founder slots left",
            "Only 100 founder slots are left.",
        )
    elif result.milestone == "closed":
        admin_email = os.environ.get("XR7_ADMIN_ALERT_EMAIL")
        if admin_email:
            pref = NotificationPreference(artist_id="admin", email=admin_email)
            send_event_notification(
                pref,
                "founder_cohort_closed",
                "Founder cohort is now full.",
                "Founder cohort is now full.",
                current_hour_utc=datetime.now(timezone.utc).hour,
                db=db,
            )
        try:
            from XR7.tasks.hubspot import hubspot_sync_recovery_update

            hubspot_sync_recovery_update.delay(artist.id, event="founder_cohort_closed")
        except Exception:  # noqa: BLE001
            logger.exception("Failed to enqueue founder cohort closed HubSpot sync", extra={"artist_id": artist.id})
