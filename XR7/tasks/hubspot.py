from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from XR7.celery_app import celery_app
from XR7.models.base import SessionLocal
from XR7.models.artist import Artist
from XR7.models.statement import Statement
from XR7.models.anomaly import Anomaly
from XR7.models.claim import Claim
from XR7.models.widget_lead import WidgetLead
from XR7.models.oauth_connector import ConnectorAccountLink
from XR7.models.payment import Payment
from XR7.models.event import Event
from XR7.services.hubspot_client import HubSpotClient
from xr7_common.logging import get_logger

logger = get_logger(__name__)


def _is_placeholder_email(value: str | None) -> bool:
    v = (value or "").strip().lower()
    return (not v) or v.endswith("@placeholder.xr7.local")


def _placeholder_email(artist_id: str) -> str:
    return f"{artist_id}@placeholder.xr7.local"


def _safe_json(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except Exception:  # noqa: BLE001
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _first_non_empty(values: list[str | None]) -> str | None:
    for v in values:
        vv = (v or "").strip()
        if vv:
            return vv
    return None


def _collect_artist_context(db, artist_id: str) -> dict[str, Any]:
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        return {"artist": None}

    statements = db.query(Statement).filter(Statement.artist_id == artist_id).all()
    anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    payments = db.query(Payment).filter(Payment.artist_id == artist_id).all()
    events = db.query(Event).filter(Event.artist_id == artist_id).all()
    oauth_links = db.query(ConnectorAccountLink).filter(ConnectorAccountLink.artist_id == artist_id).all()

    signal_maps = [_safe_json(s.ingestion_metadata_json) for s in statements if s.ingestion_metadata_json]

    distributors: list[str] = []
    pros: list[str] = []
    labels_publishers: list[str] = []
    pro_writer_id = None
    distributor_account_id = None
    inferred_name = None
    inferred_email = None

    for sm in signal_maps:
        for d in list(sm.get("distributor_list") or []):
            if d and d not in distributors:
                distributors.append(d)
        for p in list(sm.get("pro_affiliations") or []):
            if p and p not in pros:
                pros.append(p)
        for lp in list(sm.get("label_publishers") or []):
            if lp and lp not in labels_publishers:
                labels_publishers.append(lp)
        if not pro_writer_id and sm.get("pro_writer_id"):
            pro_writer_id = str(sm.get("pro_writer_id"))
        if not distributor_account_id and sm.get("distributor_account_id"):
            distributor_account_id = str(sm.get("distributor_account_id"))
        if not inferred_name and sm.get("artist_name"):
            inferred_name = str(sm.get("artist_name"))
        if not inferred_email and sm.get("email"):
            inferred_email = str(sm.get("email"))

    for p in payments:
        if p.source and p.source not in distributors:
            distributors.append(p.source)
    for e in events:
        if e.platform and e.platform not in distributors:
            distributors.append(e.platform)

    oauth_sources = []
    oauth_profile_image = None
    oauth_name = None
    oauth_email = None
    for link in oauth_links:
        provider = (link.provider or "").strip().lower()
        if provider in {"google", "apple", "spotify", "youtube"} and provider not in oauth_sources:
            oauth_sources.append(provider)
        meta = _safe_json(link.profile_metadata_json)
        if not oauth_profile_image:
            oauth_profile_image = _first_non_empty([meta.get("picture"), meta.get("profile_image"), meta.get("avatar_url")])
        if not oauth_name:
            oauth_name = _first_non_empty([meta.get("name"), meta.get("display_name"), link.display_name])
        if not oauth_email:
            oauth_email = _first_non_empty([meta.get("email")])

    total_estimated = sum(float(a.estimated_recoverable or 0.0) for a in anomalies)
    total_recovered = sum(float(c.recovered_amount or 0.0) for c in claims if str(c.status) in {"PAID", "CLOSED"})
    claim_count = len(claims)
    anomaly_count = len(anomalies)
    active_claim_count = sum(1 for c in claims if str(c.status) not in {"PAID", "CLOSED"})

    # Lightweight catalog health proxy when no dedicated model output is persisted.
    catalog_health_score = round(max(0.0, min(100.0, 50.0 + (5.0 * min(10, len(events) / 100.0)) - (3.0 * min(10, anomaly_count / 10.0)))), 2)

    return {
        "artist": artist,
        "statements": statements,
        "anomalies": anomalies,
        "claims": claims,
        "total_estimated": round(total_estimated, 2),
        "total_recovered": round(total_recovered, 2),
        "anomaly_count": anomaly_count,
        "claim_count": claim_count,
        "active_claim_count": active_claim_count,
        "catalog_health_score": catalog_health_score,
        "distributors": distributors,
        "pros": pros,
        "labels_publishers": labels_publishers,
        "pro_writer_id": pro_writer_id,
        "distributor_account_id": distributor_account_id,
        "inferred_name": inferred_name,
        "inferred_email": inferred_email,
        "oauth_sources": oauth_sources,
        "oauth_profile_image": oauth_profile_image,
        "oauth_name": oauth_name,
        "oauth_email": oauth_email,
    }


def _sync_artist_bundle(artist_id: str, event: str, *, statement_signals: dict[str, Any] | None = None) -> dict:
    db = SessionLocal()
    try:
        context = _collect_artist_context(db, artist_id)
        artist = context.get("artist")
        if not artist:
            return {"ok": False, "reason": "artist_not_found"}

        client = HubSpotClient()

        statement_signals = statement_signals or {}
        merged_name = _first_non_empty(
            [
                getattr(artist, "name", None),
                statement_signals.get("artist_name"),
                context.get("oauth_name"),
                context.get("inferred_name"),
                f"Artist {artist.id[:8]}",
            ]
        )
        merged_email = _first_non_empty(
            [
                getattr(artist, "email", None),
                statement_signals.get("email"),
                context.get("oauth_email"),
                context.get("inferred_email"),
            ]
        )
        if _is_placeholder_email(merged_email):
            merged_email = _placeholder_email(artist.id)

        if _is_placeholder_email(getattr(artist, "email", None)) and merged_email and not _is_placeholder_email(merged_email):
            artist.email = merged_email
            db.add(artist)
            db.commit()

        pro_writer_id = _first_non_empty([statement_signals.get("pro_writer_id"), context.get("pro_writer_id")])
        distributor_account_id = _first_non_empty([
            statement_signals.get("distributor_account_id"),
            context.get("distributor_account_id"),
        ])

        distributors = list(context.get("distributors") or [])
        for d in list(statement_signals.get("distributor_list") or []):
            if d and d not in distributors:
                distributors.append(d)
        pros = list(context.get("pros") or [])
        for p in list(statement_signals.get("pro_affiliations") or []):
            if p and p not in pros:
                pros.append(p)
        labels_publishers = list(context.get("labels_publishers") or [])
        for lp in list(statement_signals.get("label_publishers") or []):
            if lp and lp not in labels_publishers:
                labels_publishers.append(lp)

        contact = client.upsert_contact(
            email=merged_email,
            name=merged_name,
            properties={
                "xr7_artist_id": artist.id,
                "onboarding_status": artist.status,
                "source": "XR7 Engine 2",
                "trigger_event": event,
                "distributor_account_id": distributor_account_id,
                "pro_writer_id": pro_writer_id,
                "xr7_estimated_recoverable": context.get("total_estimated"),
                "xr7_total_recovered": context.get("total_recovered"),
                "xr7_catalog_health_score": context.get("catalog_health_score"),
                "xr7_anomaly_count": context.get("anomaly_count"),
                "xr7_claim_count": context.get("claim_count"),
                "xr7_distributor_list": ", ".join(distributors[:50]),
                "xr7_pro_affiliations": ", ".join(pros[:50]),
                "xr7_oauth_sources": ", ".join(context.get("oauth_sources") or []),
                "xr7_profile_image_url": context.get("oauth_profile_image"),
            },
        )

        artist_company = client.upsert_company(
            name=merged_name,
            properties={
                "xr7_artist_id": artist.id,
                "source": "XR7 Artist Brand",
                "xr7_distributor_list": ", ".join(distributors[:50]),
                "xr7_pro_affiliations": ", ".join(pros[:50]),
            },
        )

        associated_companies = []
        for lp in labels_publishers[:20]:
            associated_companies.append(
                client.upsert_company(
                    name=lp,
                    properties={
                        "xr7_artist_id": artist.id,
                        "source": "XR7 Label/Publisher Association",
                    },
                )
            )
        for dist in distributors[:20]:
            associated_companies.append(
                client.upsert_company(
                    name=dist,
                    properties={
                        "xr7_artist_id": artist.id,
                        "source": "XR7 Distributor Association",
                    },
                )
            )

        # HubSpot pipeline/dealstage are account-specific enum IDs in many setups;
        # keep stable semantic values while allowing account mapping.
        deal = client.upsert_deal(
            artist_id=artist.id,
            properties={
                "dealname": f"XR7 Recovery - {merged_name}",
                "amount": context.get("total_estimated"),
                "dealstage": "Discovery",
                "pipeline": "Artist Recovery",
                "onboarding_status": artist.status,
                "trigger_event": event,
                "xr7_estimated_recoverable": context.get("total_estimated"),
                "xr7_total_recovered": context.get("total_recovered"),
                "xr7_catalog_health_score": context.get("catalog_health_score"),
                "xr7_anomaly_count": context.get("anomaly_count"),
                "xr7_claim_count": context.get("claim_count"),
                "xr7_distributor_list": ", ".join(distributors[:50]),
                "xr7_pro_affiliations": ", ".join(pros[:50]),
            },
        )

        # Associations are best-effort and non-blocking.
        try:
            contact_id = contact.get("object_id")
            deal_id = deal.get("object_id")
            if contact_id and deal_id:
                client.link_contact_to_deal(contact_id=str(contact_id), deal_id=str(deal_id))
            artist_company_id = artist_company.get("object_id")
            if artist_company_id and deal_id:
                client.link_company_to_deal(company_id=str(artist_company_id), deal_id=str(deal_id))
        except Exception:  # noqa: BLE001
            logger.exception("HubSpot association linking failed", extra={"artist_id": artist.id, "event": event})

        ok = bool(contact.get("ok") or artist_company.get("ok") or deal.get("ok"))
        if not ok:
            logger.error(
                "HubSpot sync failed",
                extra={
                    "artist_id": artist.id,
                    "event": event,
                    "contact": contact,
                    "artist_company": artist_company,
                    "deal": deal,
                },
            )
        return {
            "ok": ok,
            "event": event,
            "artist_id": artist.id,
            "contact": contact,
            "artist_company": artist_company,
            "associated_companies": associated_companies,
            "deal": deal,
        }
    finally:
        db.close()


@celery_app.task(name="xr7.hubspot.sync_artist", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 4})
def hubspot_sync_artist(self, artist_id: str, event: str = "artist_created") -> dict:  # noqa: ANN001
    return _sync_artist_bundle(artist_id, event)


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
                "trigger_event": event,
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

        # Fallback update path: if a matching artist exists with placeholder/missing email,
        # enrich the artist profile with OTP-verified widget email and sync CRM.
        artist = (
            db.query(Artist)
            .filter(Artist.name == lead.artist_name)
            .order_by(Artist.created_at.desc())
            .first()
        )
        if artist and _is_placeholder_email(getattr(artist, "email", None)):
            artist.email = lead.email
            db.add(artist)
            db.commit()
            try:
                hubspot_sync_artist.delay(artist.id, event="artist_email_verified_from_widget")
            except Exception:  # noqa: BLE001
                logger.exception("Failed to enqueue HubSpot artist email enrichment sync", extra={"artist_id": artist.id})
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
    return _sync_artist_bundle(artist_id, event)


@celery_app.task(name="xr7.hubspot.sync_statement_ingestion", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 4})
def hubspot_sync_statement_ingestion(
    self,
    artist_id: str,
    statement_id: str | None = None,
    statement_signals: dict[str, Any] | None = None,
    event: str = "statement_uploaded",
) -> dict:  # noqa: ANN001
    signals = statement_signals or {}
    if statement_id and not signals:
        db = SessionLocal()
        try:
            st = db.query(Statement).filter(Statement.id == statement_id, Statement.artist_id == artist_id).first()
            if st:
                signals = _safe_json(st.ingestion_metadata_json)
        finally:
            db.close()
    return _sync_artist_bundle(artist_id, event, statement_signals=signals)
