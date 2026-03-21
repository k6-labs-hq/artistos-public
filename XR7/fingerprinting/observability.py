"""Observability layer for the XR7 fingerprinting subsystem.

Provides:
- Structured logger helpers with consistent field names
- Provider-level error codes
- Metrics counters (lightweight, no external SDK required)
- Retry / backoff utilities
- Alert helpers for provider outages
- Matching Engine audit logging
"""

from __future__ import annotations

import functools
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Callable

from xr7_common.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Provider error codes
# ---------------------------------------------------------------------------

PROVIDER_ERROR_CODES: dict[str, str] = {
    # Generic
    "FP_001": "Provider request timeout",
    "FP_002": "Provider HTTP error (4xx)",
    "FP_003": "Provider HTTP error (5xx)",
    "FP_004": "Provider returned empty/no-match",
    "FP_005": "Provider authentication failure",
    "FP_006": "Provider rate limit exceeded",
    # ACRCloud-specific
    "ACR_001": "ACRCloud: invalid access key or signature",
    "ACR_002": "ACRCloud: audio sample too short",
    "ACR_003": "ACRCloud: no match found (code 1001)",
    # Audible Magic-specific
    "AM_001": "AudibleMagic: API key invalid or expired",
    "AM_002": "AudibleMagic: async job not ready",
    # Gracenote-specific
    "GN_001": "Gracenote: client ID or user ID invalid",
    "GN_002": "Gracenote: quota exceeded",
}


def log_provider_error(
    provider: str,
    error_code: str,
    detail: str = "",
    **extra: Any,
) -> None:
    """Emit a structured error log for a fingerprinting provider."""
    description = PROVIDER_ERROR_CODES.get(error_code, "Unknown provider error")
    logger.error(
        "fingerprinting.provider_error provider=%s code=%s description=%s detail=%s %s",
        provider,
        error_code,
        description,
        detail,
        " ".join(f"{k}={v}" for k, v in extra.items()),
    )


# ---------------------------------------------------------------------------
# In-process metrics (simple counters — replace with Prometheus in production)
# ---------------------------------------------------------------------------

_metrics: dict[str, int] = defaultdict(int)


def increment(metric: str, labels: dict[str, str] | None = None) -> None:
    """Increment a named counter metric."""
    key = metric
    if labels:
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        key = f"{metric}{{{label_str}}}"
    _metrics[key] += 1
    logger.debug("metric.increment %s=%d", key, _metrics[key])


def record_latency(metric: str, latency_ms: float, labels: dict[str, str] | None = None) -> None:
    """Record a latency observation (logged for now; wire to histogram in prod)."""
    label_str = ""
    if labels:
        label_str = " " + " ".join(f"{k}={v}" for k, v in labels.items())
    logger.debug("metric.latency %s=%.2fms%s", metric, latency_ms, label_str)


def get_metrics() -> dict[str, int]:
    """Return a snapshot of all current metric counters."""
    return dict(_metrics)


# ---------------------------------------------------------------------------
# Retry / backoff
# ---------------------------------------------------------------------------

def with_retry(
    max_attempts: int = 3,
    backoff_base: float = 1.0,
    retriable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """Decorator that retries an async function with exponential backoff.

    Example::

        @with_retry(max_attempts=3, backoff_base=2.0)
        async def call_provider(): ...
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            import asyncio

            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await fn(*args, **kwargs)
                except retriable_exceptions as exc:
                    last_exc = exc
                    if attempt < max_attempts:
                        wait = backoff_base * (2 ** (attempt - 1))
                        logger.warning(
                            "retry attempt=%d/%d fn=%s wait=%.1fs error=%s",
                            attempt,
                            max_attempts,
                            fn.__qualname__,
                            wait,
                            exc,
                        )
                        await asyncio.sleep(wait)
                    else:
                        logger.error(
                            "retry exhausted fn=%s attempts=%d error=%s",
                            fn.__qualname__,
                            max_attempts,
                            exc,
                        )
            raise last_exc  # type: ignore[misc]

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Provider outage alerts
# ---------------------------------------------------------------------------

def alert_provider_outage(provider: str, error_message: str) -> None:
    """Emit an outage alert for a fingerprinting provider.

    In production wire this to PagerDuty, OpsGenie, or Slack.
    """
    logger.critical(
        "PROVIDER_OUTAGE provider=%s error=%s ts=%s",
        provider,
        error_message,
        datetime.now(timezone.utc).isoformat(),
    )
    increment("fp.provider_outage", {"provider": provider})


# ---------------------------------------------------------------------------
# Matching Engine audit logs
# ---------------------------------------------------------------------------

def audit_matching_run(
    artist_id: str,
    fingerprint_count: int,
    catalog_match_count: int,
    royalty_gap_count: int,
    anomaly_count: int,
    duration_ms: float,
) -> None:
    """Emit a structured audit log for a Matching Engine reconciliation run."""
    logger.info(
        "matching_engine.audit artist_id=%s fingerprints=%d catalog_matches=%d "
        "royalty_gaps=%d anomalies=%d duration_ms=%.1f ts=%s",
        artist_id,
        fingerprint_count,
        catalog_match_count,
        royalty_gap_count,
        anomaly_count,
        duration_ms,
        datetime.now(timezone.utc).isoformat(),
    )
    increment("fp.matching_engine.runs", {"artist_id": artist_id})
    record_latency("fp.matching_engine.duration_ms", duration_ms, {"artist_id": artist_id})
