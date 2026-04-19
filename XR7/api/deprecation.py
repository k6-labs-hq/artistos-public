"""
API Deprecation Headers for XR7 Engine.

Implements RFC 8594 (Sunset header) and deprecation best practices.

Usage in routers:
    from XR7.api.deprecation import deprecation_headers

    @router.get("/old-endpoint", deprecated=True)
    def old_handler():
        return deprecation_headers(
            response={"data": "..."},
            sunset_date="2026-12-31",
            deprecation_date="2026-06-01",
            replacement_url="/api/v2/new-endpoint",
            documentation_url="https://docs.artistos.io/migration/v2",
        )

Environment variables:
- API_DEPRECATION_POLICY_DAYS: Default deprecation notice period (default: 180 days)
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Response
from fastapi.responses import JSONResponse

DEFAULT_DEPRECATION_DAYS = int(os.environ.get("API_DEPRECATION_POLICY_DAYS", "180"))


def deprecation_headers(
    response: dict[str, Any] | Response,
    *,
    sunset_date: str | None = None,
    deprecation_date: str | None = None,
    replacement_url: str | None = None,
    documentation_url: str | None = None,
) -> Response:
    """Add deprecation headers to an API response.

    Args:
        response: Response data (dict) or FastAPI Response object
        sunset_date: ISO 8601 date when endpoint will be removed (YYYY-MM-DD)
        deprecation_date: ISO 8601 date when deprecation was announced (YYYY-MM-DD)
        replacement_url: URL of replacement endpoint
        documentation_url: URL to migration guide

    Returns:
        JSONResponse with deprecation headers

    Headers added:
        Sunset: HTTP date when endpoint will be removed (RFC 8594)
        Deprecation: HTTP date when deprecation was announced (draft RFC)
        Link: Relation to replacement endpoint and documentation
        X-API-Warn: Human-readable deprecation warning

    Example:
        return deprecation_headers(
            response={"artist_id": "abc"},
            sunset_date="2027-01-01",
            replacement_url="/api/v2/artists/{id}",
            documentation_url="https://docs.artistos.io/migration/v2",
        )
    """
    # Convert dict to JSONResponse if needed
    if isinstance(response, dict):
        response_obj = JSONResponse(content=response)
    else:
        response_obj = response

    # Sunset header (RFC 8594): date when endpoint will be removed
    if sunset_date:
        sunset_dt = datetime.fromisoformat(sunset_date).replace(tzinfo=timezone.utc)
        response_obj.headers["Sunset"] = sunset_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Deprecation header (draft RFC): date when deprecation was announced
    if deprecation_date:
        deprecation_dt = datetime.fromisoformat(deprecation_date).replace(tzinfo=timezone.utc)
        response_obj.headers["Deprecation"] = deprecation_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
    elif sunset_date:
        # If no explicit deprecation date, assume it was announced N days before sunset
        deprecation_dt = sunset_dt - timedelta(days=DEFAULT_DEPRECATION_DAYS)
        response_obj.headers["Deprecation"] = deprecation_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Link header: point to replacement and documentation
    link_parts = []
    if replacement_url:
        link_parts.append(f'<{replacement_url}>; rel="successor-version"')
    if documentation_url:
        link_parts.append(f'<{documentation_url}>; rel="deprecation"')
    if link_parts:
        response_obj.headers["Link"] = ", ".join(link_parts)

    # Custom warning header for client-side logging
    warning_msg = "This endpoint is deprecated."
    if sunset_date:
        warning_msg += f" It will be removed on {sunset_date}."
    if replacement_url:
        warning_msg += f" Use {replacement_url} instead."
    response_obj.headers["X-API-Warn"] = warning_msg

    return response_obj


def deprecated_endpoint(
    *,
    sunset_date: str,
    replacement_url: str | None = None,
    documentation_url: str | None = None,
):
    """Decorator to mark an entire endpoint as deprecated.

    Args:
        sunset_date: ISO 8601 date when endpoint will be removed
        replacement_url: URL of replacement endpoint
        documentation_url: URL to migration guide

    Returns:
        Decorator function that adds deprecation headers

    Example:
        @router.get("/old-endpoint")
        @deprecated_endpoint(
            sunset_date="2027-01-01",
            replacement_url="/api/v2/new-endpoint",
        )
        def old_handler():
            return {"data": "..."}
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return deprecation_headers(
                response=result,
                sunset_date=sunset_date,
                replacement_url=replacement_url,
                documentation_url=documentation_url,
            )

        return wrapper

    return decorator
