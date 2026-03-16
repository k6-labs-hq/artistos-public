from __future__ import annotations

from collections import Counter
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.artist import Artist
from XR7.models.branding_profile import BrandingHelpArticle, BrandingProfile
from xr7_common.logging import get_logger


logger = get_logger(__name__)

_SESSION_ORG_CACHE_KEY = "branding_by_org"
_SESSION_ARTIST_ORG_CACHE_KEY = "branding_artist_org"
_OBS_COUNTERS: Counter[str] = Counter()


DEFAULT_BRANDING: dict[str, Any] = {
    "org_id": "xr7-default",
    "display_name": "XR7",
    "logo_url": "https://assets.xr7.ai/logo.svg",
    "primary_color": "#1f7a5a",
    "secondary_color": "#2f9c74",
    "accent_color": "#f59e0b",
    "dashboard_header_text": "Artist Recovery Dashboard",
    "dashboard_footer_text": "Powered by XR7 Engine",
    "support_email": "support@xr7.ai",
    "support_phone": "+1-800-XR7-HELP",
    "legal_disclaimer": (
        "Forecasts and recovery estimates are provided for operational guidance only. "
        "Actual outcomes may vary based on payer behavior, legal deadlines, and data quality."
    ),
    "custom_domain": None,
    "white_label_enabled": False,
}


def _observe(event: str, **fields: Any) -> None:
    _OBS_COUNTERS[event] += 1
    logger.info(
        "branding_observability",
        extra={
            "event": event,
            "count": int(_OBS_COUNTERS[event]),
            **fields,
        },
    )


def branding_observability_snapshot() -> dict[str, int]:
    return dict(_OBS_COUNTERS)


def reset_branding_observability() -> None:
    _OBS_COUNTERS.clear()


def _session_cache(db: Session, key: str) -> dict[str, Any]:
    cache = db.info.setdefault(key, {})
    if isinstance(cache, dict):
        return cache
    db.info[key] = {}
    return db.info[key]


def org_id_from_artist_role(role: str | None) -> str | None:
    value = str(role or "").strip()
    if value.lower().startswith("org:") and len(value.split(":", 1)) == 2:
        return value.split(":", 1)[1].strip() or None
    return None


def org_id_for_artist(db: Session, artist_id: str) -> str | None:
    artist_org_cache = _session_cache(db, _SESSION_ARTIST_ORG_CACHE_KEY)
    if artist_id in artist_org_cache:
        return artist_org_cache[artist_id]

    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        artist_org_cache[artist_id] = None
        _observe("artist_not_found", artist_id=artist_id)
        return None

    org_id = org_id_from_artist_role(artist.role)
    artist_org_cache[artist_id] = org_id
    return org_id


def _to_brand_dict(row: BrandingProfile | None, org_id: str | None = None) -> dict[str, Any]:
    if not row:
        return {**DEFAULT_BRANDING, "org_id": org_id or DEFAULT_BRANDING["org_id"]}

    merged = {
        **DEFAULT_BRANDING,
        "org_id": row.org_id,
        "display_name": row.display_name or DEFAULT_BRANDING["display_name"],
        "logo_url": row.logo_url or DEFAULT_BRANDING["logo_url"],
        "primary_color": row.primary_color or DEFAULT_BRANDING["primary_color"],
        "secondary_color": row.secondary_color or DEFAULT_BRANDING["secondary_color"],
        "accent_color": row.accent_color or DEFAULT_BRANDING["accent_color"],
        "dashboard_header_text": row.dashboard_header_text or DEFAULT_BRANDING["dashboard_header_text"],
        "dashboard_footer_text": row.dashboard_footer_text or DEFAULT_BRANDING["dashboard_footer_text"],
        "support_email": row.support_email or DEFAULT_BRANDING["support_email"],
        "support_phone": row.support_phone or DEFAULT_BRANDING["support_phone"],
        "legal_disclaimer": row.legal_disclaimer or DEFAULT_BRANDING["legal_disclaimer"],
        "custom_domain": row.custom_domain,
        "white_label_enabled": bool(row.white_label_enabled),
    }
    return merged


def get_branding_profile(db: Session | None, org_id: str | None) -> dict[str, Any]:
    if not org_id:
        _observe("default_branding_used", reason="missing_org_id")
        return {**DEFAULT_BRANDING}
    if db is None:
        _observe("default_branding_used", reason="missing_db", org_id=org_id)
        return {**DEFAULT_BRANDING, "org_id": org_id}

    org_cache = _session_cache(db, _SESSION_ORG_CACHE_KEY)
    if org_id in org_cache:
        return {**org_cache[org_id]}

    row = db.query(BrandingProfile).filter(BrandingProfile.org_id == org_id).first()
    merged = _to_brand_dict(row, org_id=org_id)
    org_cache[org_id] = merged

    if row is None:
        _observe("missing_branding_profile", org_id=org_id)
    elif not bool(row.white_label_enabled):
        _observe("white_label_disabled", org_id=org_id)

    return {**merged}


def get_branding_for_artist(db: Session, artist_id: str) -> dict[str, Any]:
    org_id = org_id_for_artist(db, artist_id)
    return get_branding_profile(db, org_id)


def branding_metadata(brand: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": brand.get("display_name"),
        "logo_url": brand.get("logo_url"),
        "primary_color": brand.get("primary_color"),
        "secondary_color": brand.get("secondary_color"),
        "accent_color": brand.get("accent_color"),
        "support_email": brand.get("support_email"),
        "support_phone": brand.get("support_phone"),
        "legal_disclaimer": brand.get("legal_disclaimer"),
        "dashboard_header_text": brand.get("dashboard_header_text"),
        "dashboard_footer_text": brand.get("dashboard_footer_text"),
        "custom_domain": brand.get("custom_domain"),
        "white_label_enabled": bool(brand.get("white_label_enabled")),
    }


def inject_branding_metadata(db: Session | None, payload: dict[str, Any]) -> dict[str, Any]:
    """Attach top-level branding metadata when payload includes artist/org identity."""
    if "branding" in payload:
        return payload

    artist_id = payload.get("artist_id")
    if artist_id:
        brand = get_branding_for_artist(db, str(artist_id)) if db is not None else get_branding_profile(None, None)
        return {**payload, "branding": branding_metadata(brand)}

    org_id = payload.get("org_id")
    if org_id:
        brand = get_branding_profile(db, str(org_id))
        return {**payload, "branding": branding_metadata(brand)}

    return payload


def placeholder_map(brand: dict[str, Any]) -> dict[str, str]:
    return {
        "{{BRAND.NAME}}": str(brand.get("display_name") or DEFAULT_BRANDING["display_name"]),
        "{{BRAND.LOGO}}": str(brand.get("logo_url") or DEFAULT_BRANDING["logo_url"]),
        "{{BRAND.PRIMARY_COLOR}}": str(brand.get("primary_color") or DEFAULT_BRANDING["primary_color"]),
        "{{BRAND.SECONDARY_COLOR}}": str(brand.get("secondary_color") or DEFAULT_BRANDING["secondary_color"]),
        "{{BRAND.ACCENT_COLOR}}": str(brand.get("accent_color") or DEFAULT_BRANDING["accent_color"]),
        "{{BRAND.SUPPORT_EMAIL}}": str(brand.get("support_email") or DEFAULT_BRANDING["support_email"]),
        "{{BRAND.SUPPORT_PHONE}}": str(brand.get("support_phone") or DEFAULT_BRANDING["support_phone"]),
        "{{BRAND.LEGAL_DISCLAIMER}}": str(brand.get("legal_disclaimer") or DEFAULT_BRANDING["legal_disclaimer"]),
    }


def apply_brand_placeholders(value: Any, brand: dict[str, Any]) -> Any:
    mapping = placeholder_map(brand)
    if isinstance(value, str):
        out = value
        for key, replacement in mapping.items():
            out = out.replace(key, replacement)
        return out
    if isinstance(value, list):
        return [apply_brand_placeholders(v, brand) for v in value]
    if isinstance(value, dict):
        return {k: apply_brand_placeholders(v, brand) for k, v in value.items()}
    return value


def communication_templates() -> dict[str, dict[str, str]]:
    return {
        "onboarding_email": {
            "subject": "Welcome to {{BRAND.NAME}}",
            "body": "Welcome to {{BRAND.NAME}}. Need help? Contact {{BRAND.SUPPORT_EMAIL}}.",
        },
        "anomaly_alert": {
            "subject": "{{BRAND.NAME}} detected a new anomaly",
            "body": "A new anomaly requires attention. {{BRAND.LEGAL_DISCLAIMER}}",
        },
        "sol_urgency": {
            "subject": "Urgent SOL timeline notice from {{BRAND.NAME}}",
            "body": "A claim is nearing deadline. Contact {{BRAND.SUPPORT_EMAIL}} immediately.",
        },
        "claim_update": {
            "subject": "Claim update from {{BRAND.NAME}}",
            "body": "Your claim status changed. Reply to {{BRAND.SUPPORT_EMAIL}} for details.",
        },
        "deposit_notification": {
            "subject": "Deposit update from {{BRAND.NAME}}",
            "body": "A deposit event was recorded. {{BRAND.LEGAL_DISCLAIMER}}",
        },
        "weekly_digest": {
            "subject": "Your {{BRAND.NAME}} weekly digest",
            "body": "Here is your weekly summary from {{BRAND.NAME}}.",
        },
        "sms_alert": {
            "subject": "{{BRAND.NAME}} SMS",
            "body": "{{BRAND.NAME}} alert. Help: {{BRAND.SUPPORT_PHONE}}",
        },
        "push_alert": {
            "subject": "{{BRAND.NAME}} Mobile",
            "body": "{{BRAND.NAME}} notification received.",
        },
    }


def org_help_articles(db: Session, org_id: str) -> list[dict[str, Any]]:
    rows = (
        db.query(BrandingHelpArticle)
        .filter(BrandingHelpArticle.org_id == org_id)
        .order_by(BrandingHelpArticle.updated_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "title": r.title,
            "body": r.body,
            "category": r.category,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        }
        for r in rows
    ]