"""Idempotency decorator for FastAPI endpoints."""

from __future__ import annotations

import functools
from typing import Any, Callable

from fastapi import Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from XR7.models.xr7_idempotency import IdempotencyService
from xr7_common.logging import get_logger

logger = get_logger(__name__)


def with_idempotency_key(
    func: Callable[..., Any],
    db_kwarg_name: str = "db",
    tenant_id_kwarg_name: str | None = None,
    artist_id_kwarg_name: str | None = None,
) -> Callable[..., Any]:
    """Decorator to add idempotency key support to a FastAPI endpoint.

    The endpoint handler will accept an optional `idempotency_key: str | None = Header(None)`
    parameter. If the same key is used twice, the cached response from the first call
    is returned instead of re-executing the handler.

    Args:
        func: The endpoint handler function
        db_kwarg_name: Name of the db parameter (default "db")
        tenant_id_kwarg_name: Name of the tenant_id parameter (or None to use "default")
        artist_id_kwarg_name: Name of the artist_id parameter (optional)

    Returns:
        Decorated function that handles idempotency
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Extract key parameters
        idempotency_key = kwargs.pop("idempotency_key", None)
        db: Session | None = kwargs.get(db_kwarg_name)

        if not db:
            logger.warning("Idempotency decorator: no DB session found")
            return func(*args, **kwargs)

        if not idempotency_key:
            # No idempotency key provided; execute normally
            return func(*args, **kwargs)

        # Extract tenant and artist IDs
        tenant_id = "default"
        if tenant_id_kwarg_name and tenant_id_kwarg_name in kwargs:
            tenant_id = str(kwargs[tenant_id_kwarg_name])

        artist_id = None
        if artist_id_kwarg_name and artist_id_kwarg_name in kwargs:
            artist_id = str(kwargs[artist_id_kwarg_name])

        # Check if we've seen this key before
        service = IdempotencyService(db)
        is_duplicate, cached_response = service.check_and_record(
            idempotency_key=idempotency_key,
            tenant_id=tenant_id,
            artist_id=artist_id,
            request_path=None,  # Could be populated from request context if available
            request_method=None,  # Could be populated from request context if available
            response_status=0,  # Will be set after calling the function
            response_body=None,  # Will be set after calling the function
        )

        if is_duplicate:
            logger.info(
                f"Idempotency key reuse detected",
                extra={"idempotency_key": idempotency_key, "tenant_id": tenant_id, "artist_id": artist_id},
            )
            # Return cached response
            return cached_response

        # Execute the handler
        result = func(*args, **kwargs)

        # Record successful response
        service.check_and_record(
            idempotency_key=idempotency_key,
            tenant_id=tenant_id,
            artist_id=artist_id,
            request_path=None,
            request_method=None,
            response_status=200,
            response_body=result,
        )

        return result

    # Update function signature to include idempotency_key parameter
    original_annotations = getattr(func, "__annotations__", {})
    wrapper.__annotations__ = {
        **original_annotations,
        "idempotency_key": "str | None",
    }

    return wrapper


def require_idempotency_key(
    func: Callable[..., Any],
    db_kwarg_name: str = "db",
) -> Callable[..., Any]:
    """Decorator that requires an idempotency key for a write operation.

    Raises 400 Bad Request if the Idempotency-Key header is missing.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        idempotency_key = kwargs.get("idempotency_key")
        if not idempotency_key:
            raise HTTPException(
                status_code=400,
                detail="Idempotency-Key header is required for write operations",
            )
        return with_idempotency_key(func, db_kwarg_name)(*args, **kwargs)

    original_annotations = getattr(func, "__annotations__", {})
    wrapper.__annotations__ = {
        **original_annotations,
        "idempotency_key": "str",
    }

    return wrapper
