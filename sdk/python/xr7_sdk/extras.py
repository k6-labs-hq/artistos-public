"""
xr7_sdk.extras — retry policy and pagination cursor helpers.

These utilities are hand-written additions on top of the auto-generated SDK
and should not be overwritten by ``openapi-generator``.

Retry
-----
``with_retry(api_callable, *args, **kwargs)`` wraps any SDK API method call
with exponential backoff on transient errors (429, 5xx, and network failures).

    from xr7_sdk.extras import with_retry
    from xr7_sdk.api.artists_api import ArtistsApi

    api = ArtistsApi()
    artists = with_retry(api.get_artists)

Pagination
----------
``paginate(api_callable, *args, **kwargs)`` is a generator that iterates through
all pages of an offset-based endpoint that returns a ``{"items": [...],
"total": N, "limit": L, "offset": O}`` envelope.

    from xr7_sdk.extras import paginate

    for artist in paginate(api.get_artists, limit=50):
        process(artist)

``cursor_paginate(api_callable, *args, **kwargs)`` is a variant for endpoints
that return a ``next_cursor`` field.  Not all endpoints support this; check
the route documentation before using.
"""

from __future__ import annotations

import random
import time
from typing import Any, Callable, Generator

from xr7_sdk.exceptions import ApiException

# ---------------------------------------------------------------------------
# Retry configuration constants (all overridable via kwargs)
# ---------------------------------------------------------------------------
_DEFAULT_MAX_RETRIES = 3
_DEFAULT_BASE_DELAY_S = 1.0  # first retry after ~1 s
_DEFAULT_MAX_DELAY_S = 30.0  # cap per attempt
_DEFAULT_JITTER = 0.25  # ±25 % random jitter
# HTTP status codes that are considered transient
_RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})


def with_retry(
    api_callable: Callable[..., Any],
    /,
    *args: Any,
    _max_retries: int = _DEFAULT_MAX_RETRIES,
    _base_delay: float = _DEFAULT_BASE_DELAY_S,
    _max_delay: float = _DEFAULT_MAX_DELAY_S,
    _jitter: float = _DEFAULT_JITTER,
    **kwargs: Any,
) -> Any:
    """Call ``api_callable(*args, **kwargs)`` with exponential backoff.

    Retries on:
    - ``ApiException`` with a status in ``_RETRYABLE_STATUSES`` (429, 5xx)
    - ``OSError`` / ``ConnectionError`` (network blip)

    Parameters
    ----------
    api_callable:
        Any generated SDK method, e.g. ``ArtistsApi().get_artists``.
    _max_retries:
        Total number of retry attempts after the first failure (default 3).
    _base_delay:
        Base sleep duration in seconds before the first retry (default 1.0).
    _max_delay:
        Maximum sleep duration per attempt (default 30.0).
    _jitter:
        Fractional jitter applied to each delay (default 0.25 = ±25 %).
    """
    attempt = 0
    while True:
        try:
            return api_callable(*args, **kwargs)
        except ApiException as exc:
            if exc.status not in _RETRYABLE_STATUSES or attempt >= _max_retries:
                raise
        except (OSError, ConnectionError):
            if attempt >= _max_retries:
                raise

        delay = min(_base_delay * (2**attempt), _max_delay)
        jitter_amount = delay * _jitter * (2 * random.random() - 1)
        time.sleep(max(0.0, delay + jitter_amount))
        attempt += 1


def paginate(
    api_callable: Callable[..., Any],
    /,
    *args: Any,
    limit: int = 100,
    _start_offset: int = 0,
    **kwargs: Any,
) -> Generator[Any, None, None]:
    """Yield every item from a paginated offset-based endpoint.

    The endpoint must return a dict (or object with attributes) conforming to::

        {"items": [...], "total": int, "limit": int, "offset": int}

    Parameters
    ----------
    api_callable:
        Any generated SDK list method, e.g. ``AdminApi().admin_artists_get``.
    limit:
        Page size to request per call (default 100).
    _start_offset:
        Offset to begin from (default 0).

    Yields
    ------
    Individual items from each page's ``items`` list.
    """
    offset = _start_offset
    while True:
        result = api_callable(*args, limit=limit, offset=offset, **kwargs)

        # Support both dict responses and model objects
        if isinstance(result, dict):
            items: list = result.get("items") or []
            total: int = int(result.get("total", 0))
        else:
            items = list(getattr(result, "items", None) or [])
            total = int(getattr(result, "total", 0))

        yield from items

        offset += len(items)
        if not items or offset >= total:
            return


def cursor_paginate(
    api_callable: Callable[..., Any],
    /,
    *args: Any,
    limit: int = 100,
    **kwargs: Any,
) -> Generator[Any, None, None]:
    """Yield every item from a cursor-based paginated endpoint.

    The endpoint must return a dict conforming to::

        {"items": [...], "next_cursor": str | None}

    Parameters
    ----------
    api_callable:
        Any generated SDK list method that accepts a ``cursor`` query param.
    limit:
        Page size to request per call (default 100).

    Yields
    ------
    Individual items from each page's ``items`` list.
    """
    cursor: str | None = None
    while True:
        call_kwargs = dict(kwargs)
        call_kwargs["limit"] = limit
        if cursor is not None:
            call_kwargs["cursor"] = cursor

        result = api_callable(*args, **call_kwargs)

        if isinstance(result, dict):
            items: list = result.get("items") or []
            next_cursor: str | None = result.get("next_cursor")
        else:
            items = list(getattr(result, "items", None) or [])
            next_cursor = getattr(result, "next_cursor", None)

        yield from items

        if not items or not next_cursor:
            return
        cursor = next_cursor
