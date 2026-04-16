from __future__ import annotations

from typing import Any, Callable

import anyio
from fastapi import HTTPException
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response


def with_timeout(seconds: float) -> Callable:
    """Decorator that marks a route endpoint with a per-route request timeout.

    The timeout is enforced by ``TimeoutRoute.get_route_handler()``.  Routes
    that are not decorated fall back to the global ``TimeoutMiddleware``
    configured on the FastAPI application (default: 30 s).

    Usage::

        @router.post("/some/heavy/endpoint")
        @with_timeout(120)
        async def my_handler(...): ...
    """

    def decorator(func: Callable) -> Callable:
        func._route_timeout = float(seconds)
        return func

    return decorator


class TimeoutRoute(APIRoute):
    """APIRoute subclass that enforces per-endpoint timeouts.

    Set ``route_class=TimeoutRoute`` on any ``APIRouter`` whose endpoints
    may have ``@with_timeout(N)`` applied.  Endpoints without the decorator
    are passed through unchanged — the global ``TimeoutMiddleware`` still
    applies to them.
    """

    def get_route_handler(self) -> Callable[..., Any]:
        original_handler = super().get_route_handler()
        timeout = getattr(self.endpoint, "_route_timeout", None)

        if timeout is None:
            return original_handler

        _t = float(timeout)

        async def handler_with_timeout(request: Request) -> Response:
            try:
                with anyio.fail_after(_t):
                    return await original_handler(request)
            except TimeoutError:
                raise HTTPException(
                    status_code=504,
                    detail=f"Request timed out after {_t:.0f}s. Please retry or reduce payload size.",
                )

        return handler_with_timeout
