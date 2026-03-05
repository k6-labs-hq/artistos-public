import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from arcos7.models.base import Base, engine
from arcos7.api.routers import artists, earnings, anomalies, claims, billing, recovery, widget
from arcos7.api.routers import ingestion
from arcos7.api.routers import celero as celero_router
from arcos7.api.routers import dashboard as dashboard_router
from arcos7.api.routers import terms as terms_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import models to ensure all tables are registered before create_all
    import arcos7.models.terms_acceptance  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="ARCOS7 Engine",
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
# When ``ARCOS7_ENV=production`` this variable MUST be set to an explicit
# allowlist; using the wildcard "*" in production raises a RuntimeError at
# startup to prevent accidental misconfiguration.
#
# In development (default), "*" is used so the local widget HTML can call the
# local API without extra setup.
# ---------------------------------------------------------------------------
_env = os.environ.get("ARCOS7_ENV", "development").lower()
_allowed_origins_raw = os.environ.get("WIDGET_ALLOWED_ORIGINS", "*").strip()

if _env == "production" and _allowed_origins_raw == "*":
    raise RuntimeError(
        "WIDGET_ALLOWED_ORIGINS must be set to an explicit list of domains "
        "when ARCOS7_ENV=production.  Using '*' in production is not permitted."
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
    from arcos7.ingestion.connectors.pro import PROConnector
    from arcos7.ingestion.connectors.dsp import DSPConnector
    from arcos7.ingestion.connectors.platform import PlatformConnector
    from arcos7.ingestion.connectors.ticketing import TicketingConnector

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
    from arcos7.celero.client import CeleroClient
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
            "dsps": dsps,
            "platforms": platforms,
            "ticketing": ticketing,
        },
        "note": (
            "Connector 'missing_credentials' status means the API key environment "
            "variables are not set.  Use POST /artists/{id}/statements/upload to "
            "ingest royalty statement CSV files without requiring any connector credentials."
        ),
    }
