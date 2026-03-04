import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from arcos7.models.base import Base, engine
from arcos7.api.routers import artists, earnings, anomalies, claims, billing, recovery, widget


@asynccontextmanager
async def lifespan(app: FastAPI):
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


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}
