import importlib.util
import json
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Register claim status audit event listener
import XR7.services.claim_status_audit  # noqa: F401
from XR7.api.middleware.data_residency import DataResidencyMiddleware
from XR7.api.middleware.idempotency import IdempotencyMiddleware
from XR7.api.middleware.limit_upload_size import LimitUploadSizeMiddleware
from XR7.api.middleware.logging import RequestIDMiddleware, configure_structured_logging
from XR7.api.middleware.request_deduplication import RequestDeduplicationMiddleware
from XR7.api.middleware.security_headers import SecurityHeadersMiddleware
from XR7.api.middleware.tenant_enforcement import TenantEnforcementMiddleware
from XR7.api.middleware.timeout import TimeoutMiddleware
from XR7.api.middleware.versioning import APIVersioningMiddleware
from XR7.api.routers import admin_console as admin_console_router
from XR7.api.routers import advance_governance as advance_governance_router
from XR7.api.routers import (
    anomalies,
    artists,
    billing,
    claims,
    earnings,
    ingestion,
    recovery,
    widget,
)
from XR7.api.routers import audit_rights as audit_rights_router
from XR7.api.routers import auth as auth_router
from XR7.api.routers import b2b as b2b_router
from XR7.api.routers import batch_ingestion as batch_ingestion_router
from XR7.api.routers import benchmarks as benchmarks_router
from XR7.api.routers import black_box_countdown as black_box_countdown_router
from XR7.api.routers import blackbox as blackbox_router
from XR7.api.routers import branding as branding_router
from XR7.api.routers import case_rooms as case_rooms_router
from XR7.api.routers import catalog_health as catalog_health_router
from XR7.api.routers import catalog_value as catalog_value_router
from XR7.api.routers import charts as charts_router
from XR7.api.routers import class_action as class_action_router
from XR7.api.routers import collaborator_share as collaborator_share_router
from XR7.api.routers import concierge as concierge_router
from XR7.api.routers import config as config_router
from XR7.api.routers import connect as connect_router
from XR7.api.routers import connector_reliability as connector_reliability_router
from XR7.api.routers import contract_drift as contract_drift_router
from XR7.api.routers import copilot as copilot_router
from XR7.api.routers import creator_economy as creator_economy_router
from XR7.api.routers import dashboard as dashboard_router
from XR7.api.routers import data_residency as data_residency_router
from XR7.api.routers import earnings_time_machine as earnings_time_machine_router
from XR7.api.routers import enterprise_analysis as enterprise_analysis_router
from XR7.api.routers import expansion as expansion_router
from XR7.api.routers import exports as exports_router
from XR7.api.routers import fetchers as fetchers_router
from XR7.api.routers import fingerprinting as fingerprinting_router
from XR7.api.routers import forensic as forensic_router
from XR7.api.routers import gdpr as gdpr_router
from XR7.api.routers import ghost_catalog as ghost_catalog_router
from XR7.api.routers import governance as governance_router
from XR7.api.routers import health as health_router
from XR7.api.routers import identity as identity_router
from XR7.api.routers import intelligence as intelligence_router
from XR7.api.routers import invites as invites_router
from XR7.api.routers import llm_recovery as llm_recovery_router
from XR7.api.routers import messages as messages_router
from XR7.api.routers import ml_suite as ml_suite_router
from XR7.api.routers import notifications as notifications_router
from XR7.api.routers import oauth_connectors as oauth_connectors_router
from XR7.api.routers import observability as observability_router
from XR7.api.routers import onboarding as onboarding_router
from XR7.api.routers import payer_health as payer_health_router
from XR7.api.routers import payers as payers_router
from XR7.api.routers import postmark_webhooks as postmark_webhooks_router
from XR7.api.routers import public as public_router
from XR7.api.routers import recovery_credit_score as recovery_credit_score_router
from XR7.api.routers import referrals as referrals_router
from XR7.api.routers import review_queue as review_queue_router
from XR7.api.routers import royalty_dna as royalty_dna_router
from XR7.api.routers import slo as slo_router
from XR7.api.routers import sovereignty as sovereignty_router
from XR7.api.routers import support as support_router
from XR7.api.routers import team as team_router
from XR7.api.routers import team_management as team_management_router
from XR7.api.routers import terms as terms_router
from XR7.api.routers import transparency as transparency_router
from XR7.api.routers import trolley as trolley_router
from XR7.api.routers import trust as trust_router
from XR7.api.routers import tvfilm as tvfilm_router
from XR7.api.routers import ugc_scanner as ugc_scanner_router
from XR7.api.routers import vip as vip_router
from XR7.api.routers import vip_referrals as vip_referrals_router
from XR7.api.routers import workflow as workflow_router
from XR7.api.routers import workspace as workspace_router
from XR7.api.routers import xr7_forensics as xr7_forensics_router
from XR7.api.routers import xr7_metadata as xr7_metadata_router
from XR7.api.routers import xr7_ugc as xr7_ugc_router
from XR7.api.routers import xr7_valuation as xr7_valuation_router
from XR7.models.base import Base, engine
from XR7.observability.tracing import configure_tracing
from XR7.services.hubspot_client import HubSpotClient
from XR7.services.live_updates import live_updates_manager
from xr7_common.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import models to ensure all tables are registered before create_all
    import XR7.models.admin_audit_log  # noqa: F401
    import XR7.models.advance_approval  # noqa: F401
    import XR7.models.advance_offer  # noqa: F401
    import XR7.models.advance_opportunity  # noqa: F401
    import XR7.models.advance_recovery_packet  # noqa: F401
    import XR7.models.artist_message  # noqa: F401
    import XR7.models.artist_referral  # noqa: F401
    import XR7.models.batch_ingestion_job  # noqa: F401
    import XR7.models.benchmark_aggregate  # noqa: F401
    import XR7.models.blackbox_match  # noqa: F401
    import XR7.models.branding_profile  # noqa: F401
    import XR7.models.case_room  # noqa: F401
    import XR7.models.catalog_confirmation  # noqa: F401
    import XR7.models.catalog_fix_issue  # noqa: F401
    import XR7.models.catalog_graph  # noqa: F401
    import XR7.models.catalog_graph_adj  # noqa: F401
    import XR7.models.catalog_segment  # noqa: F401
    import XR7.models.class_action_signal  # noqa: F401
    import XR7.models.collaborator_share_lead  # noqa: F401
    import XR7.models.connector_sync_cursor  # noqa: F401
    import XR7.models.data_residency  # noqa: F401
    import XR7.models.evidence_anchor  # noqa: F401
    import XR7.models.feature_flag  # noqa: F401
    import XR7.models.fingerprint_job  # noqa: F401
    import XR7.models.fingerprint_match  # noqa: F401
    import XR7.models.forensic_universal_event  # noqa: F401
    import XR7.models.identity_match  # noqa: F401
    import XR7.models.immutable_ledger_entry  # noqa: F401
    import XR7.models.invite  # noqa: F401
    import XR7.models.legal_defensibility_event  # noqa: F401
    import XR7.models.liquidity_advance  # noqa: F401
    import XR7.models.metadata_issue  # noqa: F401
    import XR7.models.ml_feedback  # noqa: F401
    import XR7.models.model_registry  # noqa: F401
    import XR7.models.notification_delivery_log  # noqa: F401
    import XR7.models.notification_preference  # noqa: F401
    import XR7.models.oauth_connector  # noqa: F401
    import XR7.models.parser_plugin  # noqa: F401
    import XR7.models.platform_config  # noqa: F401
    import XR7.models.recovery_intelligence  # noqa: F401
    import XR7.models.review_queue  # noqa: F401
    import XR7.models.rights_scan  # noqa: F401
    import XR7.models.slo_metric  # noqa: F401
    import XR7.models.society_signal_log  # noqa: F401
    import XR7.models.support_message  # noqa: F401
    import XR7.models.sync_job  # noqa: F401
    import XR7.models.team_access  # noqa: F401
    import XR7.models.terms_acceptance  # noqa: F401
    import XR7.models.trolley_transaction  # noqa: F401
    import XR7.models.trust_trace  # noqa: F401
    import XR7.models.tvfilm_portfolio_job  # noqa: F401
    import XR7.models.ugc_opportunity  # noqa: F401
    import XR7.models.universal_royalty_event  # noqa: F401
    import XR7.models.vip  # noqa: F401
    import XR7.models.webhook_event  # noqa: F401
    import XR7.models.work_identity_cache  # noqa: F401
    import XR7.models.isrc_resolution_cache  # noqa: F401
    import XR7.models.xr7_idempotency  # noqa: F401
    import XR7.models.xr7_royalty  # noqa: F401

    # In deployed environments (qa, production), alembic migrations are the
    # source of truth for schema; create_all() would conflict with the enum
    # types alembic already created (Postgres CREATE TYPE doesn't honor
    # SQLAlchemy's checkfirst — known quirk). Local dev / test still uses
    # create_all() for fast SQLite bootstrap without running migrations.
    xr7_env = os.environ.get("XR7_ENV", "development").strip().lower()
    if xr7_env in {"development", "test"}:
        Base.metadata.create_all(bind=engine)
    configure_structured_logging()
    configure_tracing(app)
    # Sentry error monitoring — no-ops without SENTRY_DSN, so local dev
    # and tests stay quiet.
    from XR7.observability.sentry import configure_sentry  # noqa: PLC0415

    configure_sentry(app)

    # Ensure the object-storage bucket exists at startup. Lazy-creation on
    # first upload was racy and silently swallowed by the upload handler's
    # broad except — every QA + local install ran for weeks without the
    # bucket actually existing, so source statement bytes were never
    # persisted. Doing it once at boot makes it deterministic and surfaces
    # config errors (wrong endpoint, bad creds) before the first request.
    try:
        from XR7.services.storage_service import ObjectStorageService  # noqa: PLC0415

        ObjectStorageService().ensure_bucket()
    except Exception:  # noqa: BLE001
        # Don't block the API from starting — local dev without MinIO running
        # should still come up — but log loudly so the failure isn't
        # invisible the way it has been.
        import logging  # noqa: PLC0415

        logging.getLogger(__name__).exception(
            "Object-storage bucket ensure failed at startup; statement source "
            "bytes will not be persisted until this is fixed.",
        )

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


def _security_gate_status(env: str | None = None) -> dict[str, object]:
    current_env = (env or _env or "development").lower()
    signing_mode = os.environ.get("XR7_EVIDENCE_SIGNING_MODE", "hmac").strip().lower()
    rsa_private_set = bool(os.environ.get("XR7_EVIDENCE_PRIVATE_KEY_PEM"))
    rsa_public_set = bool(os.environ.get("XR7_EVIDENCE_PUBLIC_KEY_PEM"))
    trolley_webhook_secret_set = bool(os.environ.get("TROLLEY_SECRET_KEY"))

    if current_env == "production":
        evidence_signing_policy_ok = signing_mode == "rsa" and rsa_private_set and rsa_public_set
        trolley_webhook_policy_ok = trolley_webhook_secret_set
    else:
        evidence_signing_policy_ok = True
        trolley_webhook_policy_ok = True

    return {
        "environment": current_env,
        "evidence_signing_mode": signing_mode,
        "rsa_private_key_configured": rsa_private_set,
        "rsa_public_key_configured": rsa_public_set,
        "trolley_webhook_secret_configured": trolley_webhook_secret_set,
        "evidence_signing_policy_ok": evidence_signing_policy_ok,
        "trolley_webhook_policy_ok": trolley_webhook_policy_ok,
        "all_required_gates_passed": evidence_signing_policy_ok and trolley_webhook_policy_ok,
    }


def _optional_module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _llm_feature_status() -> dict[str, object]:
    provider = os.environ.get("LLM_PROVIDER", "openai").strip().lower()
    model = os.environ.get(
        "LLM_MODEL",
        "grok-beta" if provider in {"xai", "xai-grok", "grok"} else "gpt-4o-mini",
    )

    llm_api_key_configured = bool(os.environ.get("LLM_API_KEY"))
    openai_api_key_configured = bool(os.environ.get("OPENAI_API_KEY"))
    xai_api_key_configured = bool(os.environ.get("XAI_API_KEY"))

    langchain_core_available = _optional_module_available("langchain_core")
    langchain_openai_available = _optional_module_available("langchain_openai")
    langchain_xai_available = _optional_module_available("langchain_xai")

    provider_runtime_available = (
        langchain_xai_available
        if provider in {"xai", "xai-grok", "grok"}
        else langchain_openai_available
    )
    shared_llm_ready = bool(
        llm_api_key_configured and langchain_core_available and provider_runtime_available
    )
    advisor_ready = bool(
        langchain_core_available
        and (
            (openai_api_key_configured and langchain_openai_available)
            or (xai_api_key_configured and langchain_xai_available)
        )
    )

    features = {
        "vip_copilot": {
            "available": advisor_ready,
            "fallback_enabled": True,
            "credential_source": "OPENAI_API_KEY or XAI_API_KEY",
        },
        "claim_drafting": {
            "available": shared_llm_ready,
            "fallback_enabled": True,
            "credential_source": "LLM_API_KEY",
        },
        "negotiation_script": {
            "available": shared_llm_ready,
            "fallback_enabled": True,
            "credential_source": "LLM_API_KEY",
        },
        "gap_explainer": {
            "available": shared_llm_ready,
            "fallback_enabled": True,
            "credential_source": "LLM_API_KEY",
        },
    }
    available_count = sum(1 for feature in features.values() if feature["available"])

    return {
        "provider": provider,
        "model": model,
        "credentials": {
            "llm_api_key_configured": llm_api_key_configured,
            "openai_api_key_configured": openai_api_key_configured,
            "xai_api_key_configured": xai_api_key_configured,
        },
        "dependencies": {
            "langchain_core_available": langchain_core_available,
            "langchain_openai_available": langchain_openai_available,
            "langchain_xai_available": langchain_xai_available,
        },
        "features": features,
        "status": (
            "ready"
            if available_count == len(features)
            else ("partial" if available_count else "fallback_only")
        ),
        "available_feature_count": available_count,
        "total_feature_count": len(features),
    }


def _runtime_setting(env_name: str, fallback: object | None = None) -> object | None:
    value = os.environ.get(env_name)
    if value is not None:
        return value
    return fallback


def _running_under_pytest() -> bool:
    return "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") is not None


def _health_probe_timeout_seconds() -> float:
    raw_value = os.environ.get("XR7_HEALTH_PROBE_TIMEOUT_SECONDS")
    if raw_value is not None:
        try:
            return max(float(raw_value), 0.01)
        except ValueError:
            pass

    if _running_under_pytest():
        return 0.02

    return 2.0


_security_gates = _security_gate_status()

if _env == "production" and _allowed_origins_raw == "*":
    raise RuntimeError(
        "WIDGET_ALLOWED_ORIGINS must be set to an explicit list of domains "
        "when XR7_ENV=production.  Using '*' in production is not permitted."
    )

if _env == "production" and not bool(_security_gates["all_required_gates_passed"]):
    raise RuntimeError(
        "Production security gates failed. Require XR7_EVIDENCE_SIGNING_MODE=rsa with "
        "XR7_EVIDENCE_PRIVATE_KEY_PEM + XR7_EVIDENCE_PUBLIC_KEY_PEM, and TROLLEY_SECRET_KEY set."
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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Admin-Key",
        "X-Admin-Actor",
        "X-Analyst-Key",
        "X-Analyst-Email",
        "X-Actor-Email",
        "X-Actor-Role",
        "X-Trolley-Signature",
        "X-Request-ID",
        "X-Tenant-ID",
        "Idempotency-Key",
    ],
    expose_headers=["X-Request-ID", "X-Tenant-ID"],
)

# Limit upload size to 100MB to prevent OOM from large file uploads
# This middleware checks Content-Length before body is read into memory
app.add_middleware(LimitUploadSizeMiddleware, max_upload_size=104857600)

# Global request timeout: 30 s safety net for all routes.
# Long-running endpoints (file uploads, LLM calls, sync jobs) override this
# via @with_timeout(N) on the handler together with TimeoutRoute on their router.
app.add_middleware(TimeoutMiddleware, timeout=30)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TenantEnforcementMiddleware)
app.add_middleware(IdempotencyMiddleware)
app.add_middleware(APIVersioningMiddleware)
app.add_middleware(DataResidencyMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestDeduplicationMiddleware)

app.include_router(health_router.router)  # Health checks for K8s probes
app.include_router(earnings.router)
app.include_router(anomalies.router)
app.include_router(claims.router)
app.include_router(billing.router)
app.include_router(recovery.router)
app.include_router(widget.router)
app.include_router(ingestion.router)
app.include_router(trolley_router.router)
app.include_router(postmark_webhooks_router.router)
app.include_router(dashboard_router.router)
app.include_router(terms_router.router)
app.include_router(intelligence_router.router)
app.include_router(expansion_router.router)
app.include_router(connect_router.router)
app.include_router(artists.router)
app.include_router(onboarding_router.router)
app.include_router(forensic_router.router)
app.include_router(review_queue_router.router)
app.include_router(admin_console_router.router)
app.include_router(payers_router.router)
app.include_router(workspace_router.router)
app.include_router(llm_recovery_router.router)
app.include_router(notifications_router.router)
app.include_router(public_router.router)
app.include_router(transparency_router.router)
app.include_router(b2b_router.router)
app.include_router(team_router.router)
app.include_router(fetchers_router.router)
app.include_router(workflow_router.router)
app.include_router(support_router.router)
app.include_router(branding_router.router)
app.include_router(config_router.router)
app.include_router(xr7_forensics_router.router)
app.include_router(xr7_metadata_router.router)
app.include_router(xr7_ugc_router.router)
app.include_router(xr7_valuation_router.router)
app.include_router(auth_router.router)
app.include_router(identity_router.router)
app.include_router(trust_router.router)
app.include_router(referrals_router.router)
app.include_router(creator_economy_router.router)
app.include_router(sovereignty_router.router)
app.include_router(messages_router.router)
app.include_router(class_action_router.router)
app.include_router(ml_suite_router.router)
app.include_router(governance_router.router)
app.include_router(advance_governance_router.router)
app.include_router(tvfilm_router.router)
app.include_router(invites_router.router)
app.include_router(vip_router.router)
app.include_router(concierge_router.router)
app.include_router(copilot_router.router)
app.include_router(vip_referrals_router.router)
app.include_router(case_rooms_router.router)
app.include_router(data_residency_router.router)
app.include_router(gdpr_router.router)
app.include_router(connector_reliability_router.router)
app.include_router(slo_router.router)
app.include_router(batch_ingestion_router.router)
app.include_router(enterprise_analysis_router.router)
app.include_router(fingerprinting_router.router)
app.include_router(catalog_health_router.router)
app.include_router(benchmarks_router.router)
app.include_router(blackbox_router.router)
app.include_router(ugc_scanner_router.router)
app.include_router(earnings_time_machine_router.router)
app.include_router(ghost_catalog_router.router)
app.include_router(black_box_countdown_router.router)
app.include_router(royalty_dna_router.router)
app.include_router(payer_health_router.router)
app.include_router(contract_drift_router.router)
app.include_router(catalog_value_router.router)
app.include_router(recovery_credit_score_router.router)
app.include_router(collaborator_share_router.router)
app.include_router(observability_router.router)
app.include_router(exports_router.router)
app.include_router(charts_router.router)
app.include_router(oauth_connectors_router.router)
app.include_router(team_management_router.router)
app.include_router(audit_rights_router.router)


@app.get(
    "/health",
    openapi_extra={
        "responses": {
            "200": {
                "description": "Platform is healthy",
                "content": {"application/json": {"example": {"status": "ok", "version": "2.0.0"}}},
            },
            "503": {
                "description": "Platform is unhealthy - dependencies unreachable",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "unhealthy",
                            "version": "2.0.0",
                            "checks": {
                                "database": {"status": "fail", "error": "connection refused"},
                                "redis": {"status": "ok", "latency_ms": 2.3},
                                "s3": {"status": "fail", "error": "timeout"},
                            },
                        }
                    }
                },
            },
        }
    },
)
def health():
    """
    Health check with actual connectivity tests for critical dependencies.

    Returns 200 OK only if ALL core dependencies (PostgreSQL, Redis, S3) are reachable.
    Returns 503 Service Unavailable if any dependency check fails.

    This prevents deployments from proceeding when dependencies are misconfigured
    or unreachable, catching issues before they reach production traffic.
    """
    import time

    from sqlalchemy import text
    from starlette.responses import JSONResponse

    probe_timeout_seconds = _health_probe_timeout_seconds()
    use_runtime_only_dependency_config = _running_under_pytest()
    redis_url = _runtime_setting(
        "REDIS_URL", None if use_runtime_only_dependency_config else settings.redis_url
    )
    s3_endpoint_url = _runtime_setting(
        "S3_ENDPOINT_URL", None if use_runtime_only_dependency_config else settings.s3_endpoint_url
    )
    s3_access_key_id = _runtime_setting(
        "S3_ACCESS_KEY_ID",
        None if use_runtime_only_dependency_config else settings.s3_access_key_id,
    )
    s3_secret_access_key = _runtime_setting(
        "S3_SECRET_ACCESS_KEY",
        None if use_runtime_only_dependency_config else settings.s3_secret_access_key,
    )
    s3_bucket = _runtime_setting(
        "S3_BUCKET", None if use_runtime_only_dependency_config else settings.s3_bucket
    )
    s3_region = _runtime_setting(
        "S3_REGION", None if use_runtime_only_dependency_config else settings.s3_region
    )

    checks = {}
    all_healthy = True

    # PostgreSQL connectivity check
    try:
        start = time.perf_counter()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start) * 1000
        checks["database"] = {"status": "ok", "latency_ms": round(latency, 2)}
    except Exception as exc:
        checks["database"] = {"status": "fail", "error": str(exc)[:200]}
        all_healthy = False

    # Redis connectivity check
    try:
        if redis_url:
            import redis

            start = time.perf_counter()
            r = redis.Redis.from_url(
                str(redis_url),
                socket_connect_timeout=probe_timeout_seconds,
                socket_timeout=probe_timeout_seconds,
            )
            r.ping()
            latency = (time.perf_counter() - start) * 1000
            checks["redis"] = {"status": "ok", "latency_ms": round(latency, 2)}
        else:
            checks["redis"] = {"status": "not_configured"}
            all_healthy = False
    except Exception as exc:
        checks["redis"] = {"status": "fail", "error": str(exc)[:200]}
        all_healthy = False

    # S3 connectivity check
    try:
        if s3_endpoint_url and s3_access_key_id:
            import boto3
            from botocore.config import Config

            start = time.perf_counter()
            s3 = boto3.client(
                "s3",
                region_name=str(s3_region or "us-east-1"),
                endpoint_url=str(s3_endpoint_url),
                aws_access_key_id=str(s3_access_key_id),
                aws_secret_access_key=str(s3_secret_access_key or ""),
                config=Config(
                    connect_timeout=probe_timeout_seconds,
                    read_timeout=probe_timeout_seconds,
                    retries={"max_attempts": 0},
                ),
            )
            # Test connectivity with head_bucket or list_buckets
            try:
                s3.head_bucket(Bucket=str(s3_bucket))
            except Exception:
                # If bucket doesn't exist, test with list_buckets to verify credentials
                s3.list_buckets()
            latency = (time.perf_counter() - start) * 1000
            checks["s3"] = {"status": "ok", "latency_ms": round(latency, 2)}
        else:
            checks["s3"] = {"status": "not_configured"}
            all_healthy = False
    except Exception as exc:
        checks["s3"] = {"status": "fail", "error": str(exc)[:200]}
        all_healthy = False

    response_data = {
        "status": "ok" if all_healthy else "unhealthy",
        "version": "2.0.0",
        "checks": checks,
        "llm": _llm_feature_status(),
    }

    if all_healthy:
        return response_data
    else:
        return JSONResponse(status_code=503, content=response_data)


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
    from XR7.celery_app import celery_app
    from XR7.ingestion.connectors.distributor import DistributorConnector
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
    from XR7.ingestion.statement_parser import SUPPORTED_FORMATS
    from XR7.services.market_readiness_architecture import evaluate_architecture_readiness

    redis_url = _runtime_setting("REDIS_URL", settings.redis_url)
    celery_broker_url = _runtime_setting("CELERY_BROKER_URL", settings.celery_broker_url)
    celery_result_backend = _runtime_setting(
        "CELERY_RESULT_BACKEND", settings.celery_result_backend
    )
    s3_endpoint_url = _runtime_setting("S3_ENDPOINT_URL", settings.s3_endpoint_url)
    s3_access_key_id = _runtime_setting("S3_ACCESS_KEY_ID", settings.s3_access_key_id)
    s3_secret_access_key = _runtime_setting("S3_SECRET_ACCESS_KEY", settings.s3_secret_access_key)

    def _connector_status(connector_cls, name: str, **kwargs) -> dict:
        try:
            c = connector_cls(config={}, **kwargs)
            connected = c.connect()
            return {
                "name": name,
                "configured": connected,
                "status": "ready" if connected else "missing_credentials",
            }
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

    # Trolley payouts
    trolley_api_configured = bool(
        os.environ.get("TROLLEY_ACCESS_KEY") and os.environ.get("TROLLEY_SECRET_KEY")
    )
    trolley_webhook_secret_set = bool(os.environ.get("TROLLEY_SECRET_KEY"))

    redis_ready = bool(redis_url)
    celery_ready = bool(celery_broker_url and celery_result_backend)
    storage_ready = bool(s3_endpoint_url and s3_access_key_id and s3_secret_access_key)
    plugin_signature_ready = bool(settings.plugin_signature_secret)
    hubspot_client = HubSpotClient()

    ml_components = {
        "anomaly_detector": "ready",
        "forecaster": "ready",
        "catalog_scorer": "ready",
        "confidence_calibrator": "ready",
    }

    security_gates = _security_gate_status(_env)
    architecture = evaluate_architecture_readiness(environment=_env)

    # Core readiness for production also requires security gates.
    core_ready = bool(security_gates["all_required_gates_passed"]) if _env == "production" else True

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
        "ingestion": {
            "supported_format_count": len(SUPPORTED_FORMATS),
            "explicit_format_count": len(
                [k for k, v in SUPPORTED_FORMATS.items() if v.get("type") != "generic"]
            ),
            "batch_upload": "ready",
            "status": "ready",
        },
        "queues": {
            "redis_configured": redis_ready,
            "celery_broker_url": celery_broker_url,
            "celery_result_backend": celery_result_backend,
            "celery_registered_tasks": sorted(celery_app.tasks.keys())[:50],
            "status": "ready" if redis_ready and celery_ready else "missing_credentials",
        },
        "storage": {
            "provider": "s3-compatible",
            "endpoint": s3_endpoint_url,
            "bucket": settings.s3_bucket,
            "region": settings.s3_region,
            "configured": storage_ready,
            "status": "ready" if storage_ready else "missing_credentials",
        },
        "ml": {
            "status": "ready",
            "components": ml_components,
        },
        "plugins": {
            "allowed_prefixes": list(settings.plugin_allowed_prefixes),
            "blocked_prefixes": list(settings.plugin_blocked_prefixes),
            "signature_enforced": plugin_signature_ready,
            "status": "ready" if plugin_signature_ready else "signature_optional",
        },
        "webhooks": {
            "trolley_webhook_secret_configured": trolley_webhook_secret_set,
            "status": "ready" if trolley_webhook_secret_set else "missing_credentials",
        },
        "security_gates": security_gates,
        "architecture": architecture,
        "crm": {
            "hubspot": {
                "enabled": hubspot_client.enabled,
                "base_url": settings.hubspot_base_url,
                "auth_mode": (
                    "private_app_token"
                    if settings.hubspot_private_app_token
                    else ("api_key" if settings.hubspot_api_key else "none")
                ),
                "status": "ready" if hubspot_client.enabled else "disabled_or_missing_credentials",
            }
        },
        "trolley_payouts": {
            "provider": "Trolley",
            "api_configured": trolley_api_configured,
            "webhook_secret_configured": trolley_webhook_secret_set,
            "status": (
                "ready"
                if trolley_api_configured and trolley_webhook_secret_set
                else "missing_credentials"
            ),
        },
        "notifications": {
            "sms_twilio": "ready" if twilio_ready else "missing_credentials",
            "email_smtp": "ready" if smtp_ready else "missing_credentials",
        },
        "global_social": {
            "simulated": os.environ.get("XR7_GLOBAL_SOCIAL_SIMULATED", "1").strip().lower()
            in {"1", "true", "yes"},
            "api_key_configured": bool(os.environ.get("XR7_GLOBAL_SOCIAL_API_KEY")),
            "status": "ready",
        },
        "white_label": {
            "enabled": settings.white_label_enabled,
            "status": "ready" if settings.white_label_enabled else "disabled",
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


@app.websocket("/ws/live-updates")
async def live_updates_socket(websocket: WebSocket):
    raw_cursor = websocket.query_params.get("after_event_id", "").strip()
    after_event_id = None
    if raw_cursor:
        try:
            after_event_id = max(int(raw_cursor), 0)
        except ValueError:
            after_event_id = None

    replayed = await live_updates_manager.connect(websocket, after_event_id=after_event_id)
    try:
        if replayed:
            await websocket.send_text(
                json.dumps({"event_type": "replay_complete", "payload": {"replayed": replayed}})
            )
        while True:
            msg = await websocket.receive_text()
            if msg.strip().lower() in {"ping", "heartbeat"}:
                await websocket.send_text(json.dumps({"event_type": "pong", "payload": {}}))
    except WebSocketDisconnect:
        await live_updates_manager.disconnect(websocket)
