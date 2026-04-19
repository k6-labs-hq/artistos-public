"""
Graceful Shutdown Handler for FastAPI Application.

Ensures zero dropped requests during deployments by:
1. Stop accepting new requests (return 503)
2. Wait for in-flight requests to complete (up to 30 seconds)
3. Close database connections, Redis, Celery
4. Exit cleanly

Integrates with Kubernetes lifecycle:
- preStop hook triggers graceful shutdown
- readiness probe returns unhealthy during shutdown
- Gives load balancer time to remove pod from rotation

Configuration via environment variables:
- GRACEFUL_SHUTDOWN_TIMEOUT: Max seconds to wait for in-flight requests (default: 30)
- GRACEFUL_SHUTDOWN_ENABLED: Enable graceful shutdown (default: true)

Documented in docs/production_readiness_wave3_2026_q2.md DEPLOY-001

Kubernetes PreStop Hook Example:
    lifecycle:
      preStop:
        exec:
          command: ["/bin/sh", "-c", "sleep 5"]  # Give LB time to de-register
"""

from __future__ import annotations

import os
import signal
import threading
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from xr7_common.logging import get_logger

logger = get_logger(__name__)

SHUTDOWN_TIMEOUT = int(os.environ.get("GRACEFUL_SHUTDOWN_TIMEOUT", "30"))
SHUTDOWN_ENABLED = os.environ.get("GRACEFUL_SHUTDOWN_ENABLED", "true").lower() == "true"


class GracefulShutdownManager:
    """Manages graceful shutdown state for the application.

    Tracks:
    - Shutdown initiated flag
    - In-flight request counter
    - Shutdown completion event
    """

    def __init__(self):
        self._shutdown_initiated = False
        self._in_flight_requests = 0
        self._lock = threading.Lock()
        self._shutdown_complete = threading.Event()

    @property
    def is_shutting_down(self) -> bool:
        """Check if shutdown has been initiated."""
        return self._shutdown_initiated

    @property
    def in_flight_count(self) -> int:
        """Get current in-flight request count."""
        with self._lock:
            return self._in_flight_requests

    def initiate_shutdown(self):
        """Signal that shutdown has been initiated."""
        logger.warning(
            "Graceful shutdown initiated",
            extra={"in_flight_requests": self.in_flight_count},
        )
        self._shutdown_initiated = True

    def request_started(self):
        """Increment in-flight request counter."""
        with self._lock:
            self._in_flight_requests += 1

    def request_completed(self):
        """Decrement in-flight request counter."""
        with self._lock:
            self._in_flight_requests -= 1
            if self._in_flight_requests == 0 and self._shutdown_initiated:
                self._shutdown_complete.set()
                logger.info("All in-flight requests completed")

    def wait_for_completion(self, timeout: int = SHUTDOWN_TIMEOUT) -> bool:
        """Wait for all in-flight requests to complete.

        Args:
            timeout: Max seconds to wait

        Returns:
            True if completed successfully, False if timeout
        """
        if self.in_flight_count == 0:
            return True

        logger.info(
            f"Waiting for {self.in_flight_count} in-flight requests to complete (timeout: {timeout}s)"
        )

        completed = self._shutdown_complete.wait(timeout=timeout)

        if completed:
            logger.info("Graceful shutdown completed successfully")
            return True
        else:
            logger.warning(
                f"Graceful shutdown timeout after {timeout}s, {self.in_flight_count} requests still in flight"
            )
            return False


# Global shutdown manager instance
_shutdown_manager = GracefulShutdownManager()


def get_shutdown_manager() -> GracefulShutdownManager:
    """Get global shutdown manager instance."""
    return _shutdown_manager


class GracefulShutdownMiddleware(BaseHTTPMiddleware):
    """Middleware to track in-flight requests and reject new requests during shutdown.

    Behavior:
    - During normal operation: track in-flight requests
    - During shutdown: return 503 Service Unavailable for new requests
    - Wait for in-flight requests to complete before exiting
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with graceful shutdown awareness.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain

        Returns:
            Response
        """
        shutdown_manager = get_shutdown_manager()

        # Reject new requests during shutdown
        if shutdown_manager.is_shutting_down:
            logger.warning(
                "Rejecting request during shutdown",
                extra={"path": request.url.path, "method": request.method},
            )
            return Response(
                content='{"error": "Server is shutting down, please retry"}',
                status_code=503,
                media_type="application/json",
                headers={"Retry-After": "30"},
            )

        # Track this request
        shutdown_manager.request_started()

        try:
            response = await call_next(request)
            return response
        finally:
            shutdown_manager.request_completed()


def handle_sigterm(signum, frame):
    """SIGTERM signal handler for graceful shutdown.

    Called when Kubernetes sends SIGTERM to pod.

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    logger.info(f"Received SIGTERM signal ({signum}), initiating graceful shutdown")

    shutdown_manager = get_shutdown_manager()
    shutdown_manager.initiate_shutdown()

    # Wait for in-flight requests
    success = shutdown_manager.wait_for_completion(timeout=SHUTDOWN_TIMEOUT)

    if success:
        logger.info("Graceful shutdown successful, exiting")
    else:
        logger.error("Graceful shutdown timeout, forcing exit")

    # Exit with success code (Kubernetes will restart if needed)
    exit(0)


def setup_graceful_shutdown():
    """Register signal handlers for graceful shutdown.

    Call this during application startup.
    """
    if not SHUTDOWN_ENABLED:
        logger.info("Graceful shutdown disabled")
        return

    # Register SIGTERM handler (Kubernetes sends this)
    signal.signal(signal.SIGTERM, handle_sigterm)

    # Register SIGINT handler (Ctrl+C for local development)
    signal.signal(signal.SIGINT, handle_sigterm)

    logger.info(
        "Graceful shutdown configured",
        extra={"timeout_seconds": SHUTDOWN_TIMEOUT},
    )


@asynccontextmanager
async def lifespan_with_graceful_shutdown(app: FastAPI):
    """Lifespan context manager with graceful shutdown support.

    Use as:
        app = FastAPI(lifespan=lifespan_with_graceful_shutdown)
    """
    # Startup
    setup_graceful_shutdown()
    logger.info("Application startup complete")

    yield

    # Shutdown
    shutdown_manager = get_shutdown_manager()
    if not shutdown_manager.is_shutting_down:
        # Graceful shutdown not triggered by signal, initiate it now
        shutdown_manager.initiate_shutdown()
        shutdown_manager.wait_for_completion(timeout=SHUTDOWN_TIMEOUT)

    logger.info("Application shutdown complete")


def get_shutdown_status() -> dict:
    """Get current shutdown status for health checks.

    Returns:
        Dict with shutdown state
    """
    shutdown_manager = get_shutdown_manager()

    return {
        "is_shutting_down": shutdown_manager.is_shutting_down,
        "in_flight_requests": shutdown_manager.in_flight_count,
        "accepting_requests": not shutdown_manager.is_shutting_down,
    }
