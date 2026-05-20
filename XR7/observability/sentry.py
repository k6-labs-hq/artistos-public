"""Sentry error monitoring + lightweight performance tracing.

Wired into the FastAPI startup. **No-ops when ``SENTRY_DSN`` is unset**
so local dev and tests don't require a Sentry account or any code path
change to disable.

Free-tier-friendly defaults (5K errors + 10K perf txn / month):
- ``traces_sample_rate=0.05`` — sample 5% of requests for performance,
  comfortably under the 10K monthly perf budget at our current volumes.
- ``profiles_sample_rate=0`` — profiling off; not needed and burns
  through the perf budget faster.
- Session Replay not initialized (heavy, optional).

Error sampling stays at 1.0 — errors are rare enough that capturing
all of them is the right tradeoff. Tune ``SENTRY_TRACES_SAMPLE_RATE``
env var if the perf bucket starts saturating.

PII safety:
- ``send_default_pii=False`` (Sentry's safe default). No IP, no
  cookies, no user identifiers unless we set them deliberately.
- ``before_send`` redacts ``Authorization`` / ``Cookie`` / ``X-Admin-Key``
  from any captured request headers as a belt-and-braces guard against
  a future config change accidentally turning PII on.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def _scrub_sensitive_headers(event: dict[str, Any], _hint: dict[str, Any]) -> dict[str, Any]:
    """Strip auth-bearing headers from any captured request before send."""
    try:
        request = event.get("request") or {}
        headers = request.get("headers") or {}
        if isinstance(headers, dict):
            for key in list(headers.keys()):
                if key.lower() in {"authorization", "cookie", "x-admin-key"}:
                    headers[key] = "[redacted]"
    except Exception:  # noqa: BLE001
        # Never let a scrubbing bug eat the event — Sentry's defaults
        # already redact the common cases; this is extra insurance.
        pass
    return event


def configure_sentry(app) -> None:  # noqa: ANN001 — app typed in caller
    """Initialise Sentry if ``SENTRY_DSN`` is set; otherwise log + return."""
    dsn = (os.environ.get("SENTRY_DSN") or "").strip()
    if not dsn:
        logger.info("Sentry: SENTRY_DSN unset — error monitoring disabled.")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration
    except ImportError:
        logger.warning(
            "Sentry: SENTRY_DSN is set but sentry-sdk isn't installed; "
            "monitoring disabled. Add sentry-sdk[fastapi] to requirements.txt.",
        )
        return

    environment = (
        os.environ.get("SENTRY_ENVIRONMENT")
        or os.environ.get("XR7_ENV")
        or "development"
    )
    traces_rate = float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.05"))

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=os.environ.get("XR7_RELEASE") or None,
        send_default_pii=False,
        traces_sample_rate=traces_rate,
        profiles_sample_rate=0.0,
        integrations=[
            FastApiIntegration(),
            StarletteIntegration(),
            SqlalchemyIntegration(),
        ],
        before_send=_scrub_sensitive_headers,
    )
    logger.info(
        "Sentry: initialised (environment=%s traces_sample_rate=%s)",
        environment,
        traces_rate,
    )
