import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.earnings.engine import EarningsEngine
from XR7.graph.rights_graph import RightsGraph
from XR7.ingestion.connectors.partner_ecosystem import normalize_provider, provider_status
from XR7.ml.catalog_scorer import CatalogScorer
from XR7.models.admin_audit_log import AdminAuditLog
from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist, ArtistCreate, ArtistSchema
from XR7.models.base import get_db
from XR7.models.claim import Claim
from XR7.models.contract import Contract
from XR7.models.event import Event
from XR7.models.notification_preference import NotificationPreference
from XR7.models.oauth_connector import ConnectorAccountLink, ConnectorAccountStatus
from XR7.models.payment import Payment
from XR7.models.work import Work
from XR7.recovery.weekly_digest import build_weekly_digest, deliver_weekly_digest
from XR7.services.branding import (
    branding_metadata,
    get_branding_for_artist,
    inject_branding_metadata,
)
from XR7.services.router_v21_phase1 import router_service_for
from XR7.tasks.hubspot import hubspot_sync_artist, hubspot_sync_recovery_update
from xr7_common.logging import get_logger

router = APIRouter(prefix="/artists", tags=["artists"])
_router_service = router_service_for("artists")
logger = get_logger(__name__)


def _audit(
    db: Session,
    *,
    actor: str,
    action: str,
    resource_type: str,
    resource_id: str | None,
    details: dict | None = None,
) -> None:
    db.add(
        AdminAuditLog(
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
        )
    )


class ArtistPreferenceUpdateRequest(BaseModel):
    default_attorney_grace_period_days: int = Field(default=60, ge=1, le=365)
    primary_jurisdiction: str = Field(default="USA", min_length=2, max_length=8)
    preferred_contract_type: str = Field(default="recording")


def _attorney_grace_period_settings_payload(artist: Artist) -> dict:
    fee_percent = float(artist.contingency_fee_percent or 0.0)
    if artist.is_founder:
        fee_display = "Contingency fee: 12% (Founder rate - permanent)"
    else:
        fee_display = f"Contingency fee: {fee_percent:.2f}%"

    return {
        "artist_id": artist.id,
        "default_attorney_grace_period_days": int(artist.default_attorney_grace_period_days or 60),
        "primary_jurisdiction": str(artist.primary_jurisdiction or "USA"),
        "preferred_contract_type": str(artist.preferred_contract_type or "recording"),
        "is_founder": bool(artist.is_founder),
        "founder_slot_number": artist.founder_slot_number,
        "contingency_fee_percent": fee_percent,
        "fee_display": fee_display,
        "helper_text": (
            "We recommend a minimum of 60 days to give payers reasonable time "
            "to resolve payment before legal escalation."
        ),
    }


@router.get("/{artist_id}", response_model=ArtistSchema)
def get_artist(artist_id: str, db: Session = Depends(get_db)):
    artist = _router_service.get_artist_or_404(artist_id, db)
    return artist


@router.post("/", response_model=ArtistSchema, status_code=201)
def create_artist(artist_in: ArtistCreate, db: Session = Depends(get_db)):
    artist = Artist(
        id=str(uuid.uuid4()),
        name=artist_in.name,
        email=artist_in.email,
        first_name=artist_in.first_name,
        last_name=artist_in.last_name,
        country_code=(artist_in.country_code or "US").strip().upper(),
        role=artist_in.role,
        ipi_number=artist_in.ipi_number,
        stage_names=artist_in.stage_names,
        default_attorney_grace_period_days=max(
            1, int(artist_in.default_attorney_grace_period_days or 60)
        ),
        primary_jurisdiction=(artist_in.primary_jurisdiction or "USA").strip().upper(),
        preferred_contract_type=(artist_in.preferred_contract_type or "recording").strip().lower(),
        primary_vertical=(artist_in.primary_vertical or "MUSIC").strip().upper(),
        tvfilm_role=(artist_in.tvfilm_role or None),
        organization_type=(artist_in.organization_type or None),
        enterprise_mode_enabled=bool(artist_in.enterprise_mode_enabled),
        created_at=datetime.now(timezone.utc),
    )
    db.add(artist)
    db.commit()
    db.refresh(artist)
    _audit(
        db,
        actor=f"artist:{artist.id}",
        action="artist_created",
        resource_type="artist",
        resource_id=artist.id,
        details={
            "name": artist.name,
            "email": artist.email,
            "role": str(artist.role),
            "primary_jurisdiction": artist.primary_jurisdiction,
            "primary_vertical": artist.primary_vertical,
        },
    )
    db.commit()
    try:
        hubspot_sync_artist.delay(artist.id, event="artist_created")
    except Exception:  # noqa: BLE001
        logger.exception("Failed to enqueue HubSpot artist sync", extra={"artist_id": artist.id})
    return artist


@router.get("/{artist_id}/preferences")
def get_artist_preferences(artist_id: str, db: Session = Depends(get_db)):
    artist = _router_service.get_artist_or_404(artist_id, db)
    return inject_branding_metadata(db, _attorney_grace_period_settings_payload(artist))


@router.put("/{artist_id}/preferences")
def update_artist_preferences(
    artist_id: str,
    payload: ArtistPreferenceUpdateRequest,
    db: Session = Depends(get_db),
):
    artist = _router_service.get_artist_or_404(artist_id, db)

    artist.default_attorney_grace_period_days = max(
        1, int(payload.default_attorney_grace_period_days)
    )
    artist.primary_jurisdiction = (payload.primary_jurisdiction or "USA").strip().upper()
    artist.preferred_contract_type = (
        (payload.preferred_contract_type or "recording").strip().lower()
    )
    _audit(
        db,
        actor=f"artist:{artist_id}",
        action="artist_preferences_updated",
        resource_type="artist",
        resource_id=artist_id,
        details={
            "default_attorney_grace_period_days": artist.default_attorney_grace_period_days,
            "primary_jurisdiction": artist.primary_jurisdiction,
            "preferred_contract_type": artist.preferred_contract_type,
        },
    )
    db.commit()
    db.refresh(artist)
    return inject_branding_metadata(db, _attorney_grace_period_settings_payload(artist))


class PayerRoutingUpdateRequest(BaseModel):
    pro_affiliations: list[str] | None = None
    bmi_office_name: str | None = None


@router.get("/{artist_id}/payer-routing")
def get_payer_routing(artist_id: str, db: Session = Depends(get_db)):
    artist = _router_service.get_artist_or_404(artist_id, db)
    return {
        "artist_id": artist.id,
        "pro_affiliations": artist.pro_affiliations,
        "bmi_office_name": artist.bmi_office_name,
    }


@router.put("/{artist_id}/payer-routing")
def update_payer_routing(
    artist_id: str,
    payload: PayerRoutingUpdateRequest,
    db: Session = Depends(get_db),
):
    """Set the artist's PRO affiliations and (if BMI) regional office.

    Validates the BMI office name against `payer_offices` to prevent
    operators from saving a typo'd region. Empty / null fields are
    allowed — they unset the field.
    """
    from XR7.models.payer_office import PayerOffice  # noqa: PLC0415

    artist = _router_service.get_artist_or_404(artist_id, db)

    affiliations = payload.pro_affiliations or []
    canonical = sorted({a.strip().upper() for a in affiliations if a and a.strip()})
    artist.pro_affiliations = canonical or None

    bmi_office = (payload.bmi_office_name or "").strip()
    if bmi_office:
        match = (
            db.query(PayerOffice)
            .filter(PayerOffice.payer_id == "BMI", PayerOffice.name.ilike(bmi_office))
            .first()
        )
        if match is None:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown BMI office '{bmi_office}'",
            )
        artist.bmi_office_name = match.name
    else:
        artist.bmi_office_name = None

    _audit(
        db,
        actor=f"artist:{artist_id}",
        action="payer_routing_updated",
        resource_type="artist",
        resource_id=artist_id,
        details={
            "pro_affiliations": artist.pro_affiliations,
            "bmi_office_name": artist.bmi_office_name,
        },
    )
    db.commit()
    db.refresh(artist)
    return {
        "artist_id": artist.id,
        "pro_affiliations": artist.pro_affiliations,
        "bmi_office_name": artist.bmi_office_name,
    }


@router.post("/{artist_id}/connect")
def connect_artist(artist_id: str, db: Session = Depends(get_db)):
    """
    Check which data connectors are configured for this artist and return
    their credential status.

    This endpoint validates that the required environment variables are set
    for each connector.  It does NOT make real API calls — it only confirms
    that the credentials are present and the connector is ready to use.

    For connectors that are not yet configured, use the statement file upload
    workflow: POST /artists/{artist_id}/statements/upload
    """
    _router_service.get_artist_or_404(artist_id, db)

    from XR7.ingestion.connectors.dsp import DSPConnector
    from XR7.ingestion.connectors.international_pro import (
        APRAAMCOSConnector,
        JASRACConnector,
        KOMCAConnector,
        SACEMConnector,
    )
    from XR7.ingestion.connectors.mlc import MLCConnector
    from XR7.ingestion.connectors.platform import PlatformConnector
    from XR7.ingestion.connectors.pro import PROConnector
    from XR7.ingestion.connectors.ticketing import TicketingConnector

    def _check(connector_cls, name: str, **kwargs) -> dict:
        try:
            c = connector_cls(config={}, **kwargs)
            ok = c.connect()
            return {
                "source": name,
                "configured": ok,
                "status": "ready" if ok else "missing_credentials",
            }
        except Exception as exc:  # noqa: BLE001
            return {"source": name, "configured": False, "status": f"error: {exc}"}

    sources = (
        [_check(PROConnector, pro, pro_name=pro) for pro in ("ASCAP", "BMI", "SESAC")]
        + [_check(DSPConnector, dsp, dsp_name=dsp) for dsp in ("Spotify", "Apple Music")]
        + [_check(PlatformConnector, p, platform_name=p) for p in ("YouTube", "TikTok")]
        + [_check(TicketingConnector, t, platform_name=t) for t in ("Ticketmaster", "AXS")]
        + [_check(APRAAMCOSConnector, "APRA AMCOS")]
        + [_check(JASRACConnector, "JASRAC")]
        + [_check(KOMCAConnector, "KOMCA")]
        + [_check(SACEMConnector, "SACEM")]
        + [_check(MLCConnector, "MLC")]
    )

    configured_count = sum(1 for s in sources if s["configured"])
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "status": "ready" if configured_count > 0 else "no_connectors_configured",
            "configured_sources": configured_count,
            "total_sources": len(sources),
            "sources": sources,
            "next_steps": (
                "Configure connector credentials via environment variables (see .env.example), "
                "then call this endpoint again.  Alternatively, upload royalty statement CSV files "
                "directly at POST /artists/{artist_id}/statements/upload — no API keys required."
                if configured_count == 0
                else "Use POST /artists/{artist_id}/statements/upload to ingest data from configured sources."
            ),
        },
    )


@router.get("/{artist_id}/summary")
def artist_summary(artist_id: str, db: Session = Depends(get_db)):
    _router_service.get_artist_or_404(artist_id, db)
    rg = RightsGraph()
    engine = EarningsEngine(rg)
    summary = engine.get_earnings_summary(artist_id, db)
    anomaly_count = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).count()
    claim_count = db.query(Claim).filter(Claim.artist_id == artist_id).count()
    # Lifetime recovery potential and complexity scoring feed operator and artist planning.
    potential = float(summary.get("total_expected", 0.0) or 0.0) - float(
        summary.get("total_received", 0.0) or 0.0
    )
    complexity = 0.0
    complexity += min(
        1.0, float(db.query(Contract).filter(Contract.artist_id == artist_id).count()) / 10.0
    )
    complexity += min(
        1.0, float(db.query(Event).filter(Event.artist_id == artist_id).count()) / 5000.0
    )
    complexity += min(
        1.0, float(db.query(Anomaly).filter(Anomaly.artist_id == artist_id).count()) / 50.0
    )
    complexity_score = round(min(1.0, complexity / 3.0), 6)

    try:
        hubspot_sync_recovery_update.delay(artist_id, event="artist_summary_requested")
    except Exception:  # noqa: BLE001
        logger.exception("Failed to enqueue HubSpot summary sync", extra={"artist_id": artist_id})

    return {
        **summary,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "anomaly_count": anomaly_count,
        "claim_count": claim_count,
        "recovery_potential": round(max(potential, 0.0), 2),
        "recovery_complexity_score": complexity_score,
    }


@router.get("/{artist_id}/ml/catalog-health")
def catalog_health(artist_id: str, db: Session = Depends(get_db)):
    """
    Return an ML-derived catalog health score (0–100) and grade for the artist.

    Combines metadata completeness, payment regularity, anomaly density,
    recovery rate, and earnings accuracy into a single composite score.
    """
    _router_service.get_artist_or_404(artist_id, db)

    works = [
        {"id": w.id, "isrc": w.isrc, "iswc": w.iswc}
        for w in db.query(Work).filter(Work.artist_id == artist_id).limit(2_000).all()
    ]
    payments = [
        {
            "id": p.id,
            "amount": p.amount,
            "currency": p.currency,
            "received_at": p.received_at.isoformat(),
        }
        for p in db.query(Payment).filter(Payment.artist_id == artist_id).limit(2_000).all()
    ]
    anomalies = [
        {"id": a.id, "status": a.status}
        for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).limit(2_000).all()
    ]
    claims = [
        {"id": c.id, "status": c.status, "recovered_amount": c.recovered_amount}
        for c in db.query(Claim).filter(Claim.artist_id == artist_id).limit(2_000).all()
    ]
    rg = RightsGraph()
    engine = EarningsEngine(rg)
    earnings_summary = engine.get_earnings_summary(artist_id, db)

    scorer = CatalogScorer()
    report = scorer.score(
        artist_id=artist_id,
        works=works,
        payments=payments,
        anomalies=anomalies,
        claims=claims,
        earnings_summary=earnings_summary,
    )
    return {
        **report.to_dict(),
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
    }


@router.get("/{artist_id}/digest/weekly")
def weekly_digest(artist_id: str, db: Session = Depends(get_db)):
    artist = _router_service.get_artist_or_404(artist_id, db)

    anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).limit(500).all()
    claims = db.query(Claim).filter(Claim.artist_id == artist_id).limit(500).all()
    contracts = db.query(Contract).filter(Contract.artist_id == artist_id).limit(500).all()
    payments = db.query(Payment).filter(Payment.artist_id == artist_id).limit(500).all()
    preference = (
        db.query(NotificationPreference)
        .filter(NotificationPreference.artist_id == artist_id)
        .first()
    )

    digest = build_weekly_digest(
        artist_id=artist_id,
        anomalies=anomalies,
        claims=claims,
        contracts=[
            {
                "id": c.id,
                "contract_type": str(c.contract_type),
                "territory": c.territory,
                "terms": c.terms or {},
            }
            for c in contracts
        ],
        payments=[
            {
                "id": p.id,
                "amount": p.amount,
                "currency": p.currency,
                "source": p.source,
                "received_at": p.received_at.isoformat() if p.received_at else None,
            }
            for p in payments
        ],
    )

    delivery = deliver_weekly_digest(
        digest,
        preference,
        email=(preference.email if preference else artist.email),
        sms_number=(preference.phone if preference else None),
    )
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "delivery": delivery,
        "digest": digest,
    }


@router.post("/{artist_id}/connect/{provider}")
def connect_provider(artist_id: str, provider: str, db: Session = Depends(get_db)):
    _router_service.get_artist_or_404(artist_id, db)

    provider_key = normalize_provider(provider)
    status = provider_status(provider_key)
    if not status.get("supported"):
        raise HTTPException(status_code=422, detail=f"Unsupported provider: {provider}")

    external_id = f"manual-{provider_key}-{artist_id}"
    link = (
        db.query(ConnectorAccountLink)
        .filter(
            ConnectorAccountLink.artist_id == artist_id,
            ConnectorAccountLink.provider == provider_key,
            ConnectorAccountLink.tenant_id == "default",
            ConnectorAccountLink.external_account_id == external_id,
        )
        .first()
    )
    if not link:
        link = ConnectorAccountLink(
            artist_id=artist_id,
            provider=provider_key,
            tenant_id="default",
            external_account_id=external_id,
            display_name=f"{provider_key} account",
            granted_scopes="read write",
            access_token="configured-via-environment",
            refresh_token="configured-via-environment",
            token_type="Bearer",
            status=ConnectorAccountStatus.ACTIVE,
            is_active=True,
        )
        db.add(link)
    else:
        link.status = ConnectorAccountStatus.ACTIVE
        link.is_active = True
    _audit(
        db,
        actor=f"artist:{artist_id}",
        action="provider_connected",
        resource_type="connector_account_link",
        resource_id=link.id if link.id else None,
        details={"artist_id": artist_id, "provider": provider_key},
    )
    db.commit()
    db.refresh(link)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "provider": provider_key,
            "status": provider_status(provider_key),
            "link_id": link.id,
        },
    )


@router.get("/{artist_id}/connect/{provider}/status")
def provider_connection_status(artist_id: str, provider: str, db: Session = Depends(get_db)):
    _router_service.get_artist_or_404(artist_id, db)

    provider_key = normalize_provider(provider)
    links = (
        db.query(ConnectorAccountLink)
        .filter(
            ConnectorAccountLink.artist_id == artist_id,
            ConnectorAccountLink.provider == provider_key,
        )
        .order_by(ConnectorAccountLink.updated_at.desc())
        .all()
    )
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "provider": provider_key,
            "status": provider_status(provider_key),
            "accounts": [
                {
                    "id": link.id,
                    "external_account_id": link.external_account_id,
                    "display_name": link.display_name,
                    "status": str(link.status),
                    "last_refreshed_at": (
                        link.last_refreshed_at.isoformat() if link.last_refreshed_at else None
                    ),
                    "is_active": bool(link.is_active),
                }
                for link in links
            ],
        },
    )
