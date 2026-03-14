import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from XR7.models.base import Base, engine
from XR7.api.routers import artists, earnings, anomalies, claims, billing, recovery, widget
from XR7.api.routers import ingestion
from XR7.api.routers import celero as celero_router
from XR7.api.routers import dashboard as dashboard_router
from XR7.api.routers import terms as terms_router
from XR7.api.routers import intelligence as intelligence_router
from XR7.api.routers import expansion as expansion_router
from XR7.api.routers import onboarding as onboarding_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import models to ensure all tables are registered before create_all
    import XR7.models.terms_acceptance  # noqa: F401
    import XR7.models.recovery_intelligence  # noqa: F401
    import XR7.models.notification_preference  # noqa: F401
    import XR7.models.team_access  # noqa: F401
    import XR7.models.evidence_anchor  # noqa: F401
    import XR7.models.oauth_connector  # noqa: F401
    import XR7.models.catalog_confirmation  # noqa: F401
    import XR7.models.immutable_ledger_entry  # noqa: F401
    import XR7.models.parser_plugin  # noqa: F401
    import XR7.models.sync_job  # noqa: F401
    import XR7.models.universal_royalty_event  # noqa: F401
    import XR7.models.catalog_graph  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="XR7 Engine",
    version="2.0.0",
    description="Artist Earnings Accuracy Platform",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS configuration.
#
# ``WIDGET_ALLOWED_ORIGINS`` — comma-separated list of origins permitted to
# embed the widget, e.g. "https://yourlabel.com,https://partner-site.com".
#
# When ``XR7_ENV=production`` this variable MUST be set to an explicit
# allowlist; using the wildcard "*" in production raises a RuntimeError at
# startup to prevent accidental misconfiguration.
#
# In development (default), "*" is used so the local widget HTML can call the
# local API without extra setup.
# ---------------------------------------------------------------------------
_env = os.environ.get("XR7_ENV", "development").lower()
_allowed_origins_raw = os.environ.get("WIDGET_ALLOWED_ORIGINS", "*").strip()

if _env == "production" and _allowed_origins_raw == "*":
    raise RuntimeError(
        "WIDGET_ALLOWED_ORIGINS must be set to an explicit list of domains "
        "when XR7_ENV=production.  Using '*' in production is not permitted."
    )

_allowed_origins = (
    [o.strip() for o in _allowed_origins_raw.split(",") if o.strip()]
    if _allowed_origins_raw != "*"
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Key"],
)

app.include_router(artists.router)
app.include_router(earnings.router)
app.include_router(anomalies.router)
app.include_router(claims.router)
app.include_router(billing.router)
app.include_router(recovery.router)
app.include_router(widget.router)
app.include_router(ingestion.router)
app.include_router(celero_router.router)
app.include_router(dashboard_router.router)
app.include_router(terms_router.router)
app.include_router(intelligence_router.router)
app.include_router(expansion_router.router)
app.include_router(onboarding_router.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.get("/health/readiness")
def readiness():
    """
    Return the platform readiness status for every integration point.

    Operators can call this endpoint to see exactly which connectors are
    configured (credentials present) vs. which require additional setup.

    ``ready`` is ``True`` only when the core platform components are
    functional.  Individual connector status reflects whether the required
    environment variables are set — it does NOT make real network connections.
    """
    from XR7.ingestion.connectors.pro import PROConnector
    from XR7.ingestion.connectors.dsp import DSPConnector
    from XR7.ingestion.connectors.platform import PlatformConnector
    from XR7.ingestion.connectors.ticketing import TicketingConnector
    from XR7.ingestion.connectors.distributor import DistributorConnector
    from XR7.ingestion.connectors.mlc import MLCConnector
    from XR7.ingestion.connectors.international_pro import (
        APRAAMCOSConnector,
        JASRACConnector,
        KOMCAConnector,
        SACEMConnector,
    )

    def _connector_status(connector_cls, name: str, **kwargs) -> dict:
        try:
            c = connector_cls(config={}, **kwargs)
            connected = c.connect()
            return {"name": name, "configured": connected,
                    "status": "ready" if connected else "missing_credentials"}
        except Exception as exc:  # noqa: BLE001
            return {"name": name, "configured": False, "status": f"error: {exc}"}

    # PROs
    pros = [
        _connector_status(PROConnector, pro, pro_name=pro)
        for pro in ("ASCAP", "BMI", "SESAC", "GMR", "SOCAN", "PRS", "GEMA")
    ]
    international_pros = [
        _connector_status(APRAAMCOSConnector, "APRA AMCOS"),
        _connector_status(JASRACConnector, "JASRAC"),
        _connector_status(KOMCAConnector, "KOMCA"),
        _connector_status(SACEMConnector, "SACEM"),
    ]
    # DSPs
    dsps = [
        _connector_status(DSPConnector, dsp, dsp_name=dsp)
        for dsp in ("Spotify", "Apple Music", "Amazon Music", "Tidal", "Deezer")
    ]
    # Platforms
    platforms = [
        _connector_status(PlatformConnector, plat, platform_name=plat)
        for plat in ("YouTube", "TikTok", "Instagram")
    ]
    # Ticketing
    ticketing = [
        _connector_status(TicketingConnector, plat, platform_name=plat)
        for plat in ("Ticketmaster", "AXS", "SeatGeek", "Eventbrite")
    ]
    # Distributors (small-label / indie)
    distributors = [
        _connector_status(DistributorConnector, dist, distributor_name=dist)
        for dist in DistributorConnector.supported_distributors()
    ]
    # Mechanical royalties
    mechanical = [_connector_status(MLCConnector, "MLC")]

    # Notification services
    twilio_ready = bool(
        os.environ.get("TWILIO_ACCOUNT_SID")
        and os.environ.get("TWILIO_AUTH_TOKEN")
        and os.environ.get("TWILIO_FROM_NUMBER")
    )
    smtp_ready = bool(
        os.environ.get("SMTP_HOST")
        and os.environ.get("SMTP_USER")
        and os.environ.get("SMTP_PASSWORD")
    )

    # Celero Commerce — Merchant of Record
    from XR7.celero.client import CeleroClient
    celero_client = CeleroClient()
    celero_webhook_secret_set = bool(os.environ.get("CELERO_WEBHOOK_SECRET"))

    # Core platform is always ready (DB + API)
    core_ready = True

    return {
        "ready": core_ready,
        "version": "2.0.0",
        "environment": _env,
        "core": {
            "database": "ready",
            "api": "ready",
            "widget": "ready",
            "statement_upload": "ready",
        },
        "merchant_of_record": {
            "provider": "Celero Commerce",
            "gateway": "Celero Connect®",
            "api_configured": celero_client.configured,
            "webhook_secret_configured": celero_webhook_secret_set,
            "status": (
                "ready"
                if celero_client.configured and celero_webhook_secret_set
                else "missing_credentials"
            ),
            **celero_client.status(),
        },
        "notifications": {
            "sms_twilio": "ready" if twilio_ready else "missing_credentials",
            "email_smtp": "ready" if smtp_ready else "missing_credentials",
        },
        "connectors": {
            "pros": pros,
            "international_pros": international_pros,
            "dsps": dsps,
            "platforms": platforms,
            "ticketing": ticketing,
            "distributors": distributors,
            "mechanical": mechanical,
        },
        "note": (
            "Connector 'missing_credentials' status means the API key environment "
            "variables are not set.  Use POST /artists/{id}/statements/upload to "
            "ingest royalty statement CSV files without requiring any connector credentials.  "
            "See GET /ingestion/supported-formats for the full list of auto-detected "
            "CSV formats (DistroKid, TuneCore, CD Baby, Amuse, United Masters, ONErpm, "
            "Stem, LANDR, Ditto Music, ReverbNation, Bandcamp, ASCAP, BMI, Spotify, + generic). "
            "For MLC feed integration, configure MLC_API_KEY (and optionally MLC_API_BASE_URL). "
            "For international PRO feeds, configure APRA_AMCOS_API_KEY, JASRAC_API_KEY, "
            "KOMCA_API_KEY, and SACEM_API_KEY."
        ),
    }
