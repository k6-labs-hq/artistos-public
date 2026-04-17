"""
Data residency enforcement middleware.

Reads the optional ``X-Data-Region`` request header and rejects requests
that specify a region not permitted by the ``DATA_RESIDENCY_ALLOWED_REGIONS``
environment variable.

Environment variables
---------------------
DATA_RESIDENCY_ALLOWED_REGIONS
    Comma-separated list of allowed region codes (case-insensitive).
    Defaults to ``"US,EU,GLOBAL"``.

Examples
--------
    X-Data-Region: US       → allowed (default config)
    X-Data-Region: APAC     → 422 Unprocessable Entity
    (header absent)         → request passes through unchanged
"""

from __future__ import annotations

import json
import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

_HEADER = "x-data-region"
_ENV_VAR = "DATA_RESIDENCY_ALLOWED_REGIONS"
_DEFAULT_REGIONS = {"US", "EU", "GLOBAL"}


def _allowed_regions() -> frozenset[str]:
    """Return the set of allowed region codes from the environment."""
    raw = os.environ.get(_ENV_VAR, "")
    if raw.strip():
        return frozenset(r.strip().upper() for r in raw.split(",") if r.strip())
    return frozenset(_DEFAULT_REGIONS)


class DataResidencyMiddleware(BaseHTTPMiddleware):
    """Reject requests whose ``X-Data-Region`` header names a disallowed region."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        region_header = request.headers.get(_HEADER)
        if region_header is not None:
            region = region_header.strip().upper()
            allowed = _allowed_regions()
            if region not in allowed:
                body = json.dumps(
                    {
                        "detail": (
                            f"Data region '{region_header}' is not permitted. "
                            f"Allowed regions: {sorted(allowed)}"
                        )
                    }
                ).encode()
                return Response(
                    content=body,
                    status_code=422,
                    media_type="application/json",
                    headers={"X-Data-Region-Rejected": region},
                )
        return await call_next(request)
