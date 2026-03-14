from __future__ import annotations

from XR7.celery_app import celery_app
from XR7.models.base import SessionLocal
from XR7.models.artist import Artist
from XR7.models.statement import Statement
from XR7.models.anomaly import Anomaly
from XR7.models.claim import Claim
from XR7.models.widget_lead import WidgetLead
from XR7.services.hubspot_client import HubSpotClient


@celery_app.task(name="xr7.hubspot.sync_artist", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 4})
def hubspot_sync_artist(self, artist_id: str, event: str = "artist_created") -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        artist = db.query(Artist).filter(Artist.id == artist_id).first()
        if not artist:
            return {"ok": False, "reason": "artist_not_found"}
        client = HubSpotClient()
        contact = client.upsert_contact(
            email=getattr(artist, "email", None),
            name=artist.name,
            properties={
                "artist_id": artist.id,
                "onboarding_status": artist.status,
                "source": "XR7 Engine 2",
                "trigger_event": event,
            },
        )
        deal = client.upsert_deal(
            artist_id=artist.id,
            properties={
                "dealname": f"Artist Recovery - {artist.name}",
                "pipeline": "Artist Recovery",
                "dealstage": "new_artist",
                "onboarding_status": artist.status,
                "trigger_event": event,
            },
        )
        return {"ok": bool(contact.get("ok") or deal.get("ok")), "contact": contact, "deal": deal}
    finally:
        db.close()


@celery_app.task(name="xr7.hubspot.sync_widget_lead", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 4})
def hubspot_sync_widget_lead(self, lead_id: str, event: str = "widget_estimate") -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        lead = db.query(WidgetLead).filter(WidgetLead.id == lead_id).first()
        if not lead:
            return {"ok": False, "reason": "lead_not_found"}
        client = HubSpotClient()
        contact = client.upsert_contact(
            email=lead.email,
            name=lead.artist_name,
            properties={
                "source": "Royalty Estimator Widget",
                "widget_lead_id": lead.id,
                "mfa_verified": True,
            },
        )
        deal = client.upsert_deal(
            artist_id=lead.id,
            properties={
                "dealname": f"Widget Lead - {lead.artist_name or lead.email}",
                "pipeline": "Artist Recovery",
                "dealstage": "widget_lead",
                "estimated_recovery_range": f"{lead.estimate_conservative}-{lead.estimate_optimistic}",
                "widget_session_id": lead.id,
                "trigger_event": event,
            },
        )
        return {"ok": bool(contact.get("ok") or deal.get("ok")), "contact": contact, "deal": deal}
    finally:
        db.close()


@celery_app.task(name="xr7.hubspot.sync_widget_registration", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 4})
def hubspot_sync_widget_registration(self, *, artist_name: str, email: str, session_id: str) -> dict:  # noqa: ANN001
    client = HubSpotClient()
    contact = client.upsert_contact(
        email=email,
        name=artist_name,
        properties={
            "source": "Royalty Estimator Widget",
            "widget_session_id": session_id,
            "mfa_verified": False,
            "trigger_event": "widget_register",
        },
    )
    deal = client.upsert_deal(
        artist_id=session_id,
        properties={
            "dealname": f"Widget Lead - {artist_name or email}",
            "pipeline": "Artist Recovery",
            "dealstage": "widget_registered",
            "widget_session_id": session_id,
            "trigger_event": "widget_register",
        },
    )
    return {"ok": bool(contact.get("ok") or deal.get("ok")), "contact": contact, "deal": deal}


@celery_app.task(name="xr7.hubspot.sync_recovery_update", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 4})
def hubspot_sync_recovery_update(self, artist_id: str, event: str = "recovery_update") -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        artist = db.query(Artist).filter(Artist.id == artist_id).first()
        if not artist:
            return {"ok": False, "reason": "artist_not_found"}

        statement_count = db.query(Statement).filter(Statement.artist_id == artist_id, Statement.status == "PROCESSED").count()
        anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
        claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()

        total_estimated = sum(float(a.estimated_recoverable or 0.0) for a in anomalies)
        active_claim_count = sum(1 for c in claims if str(c.status) not in {"PAID", "CLOSED"})
        highest_severity = "LOW"
        severity_rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        for a in anomalies:
            sev = str(a.severity)
            if severity_rank.get(sev, 0) > severity_rank.get(highest_severity, 0):
                highest_severity = sev

        client = HubSpotClient()
        result = client.upsert_deal(
            artist_id=artist_id,
            properties={
                "dealname": f"Artist Recovery - {artist.name}",
                "pipeline": "Artist Recovery",
                "dealstage": "in_analysis" if statement_count > 0 else "new_artist",
                "onboarding_status": artist.status,
                "anomaly_count": len(anomalies),
                "active_claim_count": active_claim_count,
                "total_estimated_recoverable": round(total_estimated, 2),
                "highest_severity": highest_severity,
                "trigger_event": event,
            },
        )
        return {"ok": bool(result.get("ok")), "deal": result}
    finally:
        db.close()
