"""
Global Circuit Breaker Registry for XR7 Engine.

Provides centralized tracking of all circuit breaker states across integrations:
- Trolley API (payment processing)
- Spotify API (catalog matching)
- DSP connectors (ingestion)
- LLM providers (contract analysis, anomaly detection)

Each circuit breaker has three states:
- CLOSED: Normal operation, requests pass through
- OPEN: Failures exceeded threshold, all requests fail fast
- HALF_OPEN: After recovery timeout, allow one test request

Circuit breaker pattern prevents cascading failures and gives
downstream services time to recover.

Documented in docs/production_readiness_wave2_2026_q2.md OPS-003
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, TypeVar

from xr7_common.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests immediately
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerMetrics:
    """Metrics tracked by circuit breaker."""

    failure_count: int = 0
    success_count: int = 0
    last_failure_time: datetime | None = None
    last_success_time: datetime | None = None
    opened_at: datetime | None = None
    half_opened_at: datetime | None = None
    state_changes: list[tuple[datetime, CircuitState]] = field(default_factory=list)


class CircuitBreaker:
    """Circuit breaker for external service calls.

    Tracks failures and opens circuit after threshold exceeded.
    Prevents cascading failures and allows service recovery time.

    Args:
        name: Circuit breaker identifier (e.g., "trolley_api")
        failure_threshold: Number of consecutive failures before opening (default: 5)
        recovery_timeout_seconds: Time to wait before trying again (default: 60)
        success_threshold: Consecutive successes needed to close from half-open (default: 2)

    Example:
        >>> breaker = CircuitBreaker(name="spotify_api", failure_threshold=3)
        >>> try:
        ...     result = breaker.call(lambda: spotify_client.search(query))
        ... except CircuitBreakerOpenError:
        ...     logger.error("Spotify API circuit is open, using fallback")
        ...     result = fallback_search(query)
    """

    def __init__(
        self,
        *,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout_seconds: int = 60,
        success_threshold: int = 2,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.success_threshold = success_threshold

        self._state = CircuitState.CLOSED
        self._metrics = CircuitBreakerMetrics()
        self._lock = threading.Lock()
        self._consecutive_successes = 0

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if self._state == CircuitState.OPEN and self._should_attempt_reset():
                self._transition_to(CircuitState.HALF_OPEN)
            return self._state

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try recovery."""
        if self._metrics.opened_at is None:
            return False
        elapsed = (datetime.now(timezone.utc) - self._metrics.opened_at).total_seconds()
        return elapsed >= self.recovery_timeout_seconds

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to new state and log change."""
        self._state = new_state

        now = datetime.now(timezone.utc)
        self._metrics.state_changes.append((now, new_state))

        if new_state == CircuitState.OPEN:
            self._metrics.opened_at = now
            logger.warning(
                f"Circuit breaker '{self.name}' opened",
                extra={
                    "circuit_name": self.name,
                    "failure_count": self._metrics.failure_count,
                    "threshold": self.failure_threshold,
                },
            )
        elif new_state == CircuitState.HALF_OPEN:
            self._metrics.half_opened_at = now
            self._consecutive_successes = 0
            logger.info(
                f"Circuit breaker '{self.name}' half-open, attempting recovery test",
                extra={"circuit_name": self.name},
            )
        elif new_state == CircuitState.CLOSED:
            self._metrics.opened_at = None
            self._metrics.half_opened_at = None
            logger.info(
                f"Circuit breaker '{self.name}' closed, service recovered",
                extra={
                    "circuit_name": self.name,
                    "success_count": self._consecutive_successes,
                },
            )

    def call(self, func: Callable[[], T]) -> T:
        """Execute function through circuit breaker.

        Args:
            func: Callable to execute (should be idempotent)

        Returns:
            Result from func()

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Any exception raised by func()
        """
        current_state = self.state

        if current_state == CircuitState.OPEN:
            raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is open, failing fast")

        try:
            result = func()
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Record successful call."""
        with self._lock:
            self._metrics.success_count += 1
            self._metrics.last_success_time = datetime.now(timezone.utc)
            self._metrics.failure_count = 0  # Reset failure counter
            self._consecutive_successes += 1

            # If half-open and enough successes, close circuit
            if (
                self._state == CircuitState.HALF_OPEN
                and self._consecutive_successes >= self.success_threshold
            ):
                self._transition_to(CircuitState.CLOSED)

    def _on_failure(self) -> None:
        """Record failed call."""
        with self._lock:
            self._metrics.failure_count += 1
            self._metrics.last_failure_time = datetime.now(timezone.utc)
            self._consecutive_successes = 0

            # If closed and failures exceed threshold, open circuit
            if (
                self._state == CircuitState.CLOSED
                and self._metrics.failure_count >= self.failure_threshold
            ):
                self._transition_to(CircuitState.OPEN)

            # If half-open and any failure, immediately reopen
            elif self._state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)

    def reset(self) -> None:
        """Manually reset circuit breaker to closed state."""
        with self._lock:
            self._transition_to(CircuitState.CLOSED)
            self._metrics.failure_count = 0
            self._consecutive_successes = 0
            logger.info(f"Circuit breaker '{self.name}' manually reset")

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics snapshot."""
        with self._lock:
            return {
                "name": self.name,
                "state": self._state.value,
                "failure_count": self._metrics.failure_count,
                "success_count": self._metrics.success_count,
                "last_failure_time": (
                    self._metrics.last_failure_time.isoformat()
                    if self._metrics.last_failure_time
                    else None
                ),
                "last_success_time": (
                    self._metrics.last_success_time.isoformat()
                    if self._metrics.last_success_time
                    else None
                ),
                "next_retry_time": (
                    (self._metrics.opened_at.timestamp() + self.recovery_timeout_seconds)
                    if self._metrics.opened_at and self._state == CircuitState.OPEN
                    else None
                ),
            }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreakerRegistry:
    """Global registry for all circuit breakers in the application.

    Singleton pattern provides centralized access to all breakers.
    Supports observability dashboard queries.

    Example:
        >>> registry = CircuitBreakerRegistry.get_instance()
        >>> trolley_breaker = registry.get_or_create("trolley_api")
        >>> all_states = registry.get_all_states()
    """

    _instance: CircuitBreakerRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._breakers: dict[str, CircuitBreaker] = {}
        self._breakers_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> CircuitBreakerRegistry:
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = CircuitBreakerRegistry()
        return cls._instance

    def get_or_create(
        self,
        name: str,
        *,
        failure_threshold: int = 5,
        recovery_timeout_seconds: int = 60,
        success_threshold: int = 2,
    ) -> CircuitBreaker:
        """Get existing breaker or create new one.

        Args:
            name: Circuit breaker identifier
            failure_threshold: Failures before opening
            recovery_timeout_seconds: Recovery wait time
            success_threshold: Successes needed to close

        Returns:
            CircuitBreaker instance
        """
        with self._breakers_lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(
                    name=name,
                    failure_threshold=failure_threshold,
                    recovery_timeout_seconds=recovery_timeout_seconds,
                    success_threshold=success_threshold,
                )
                logger.info(
                    f"Created circuit breaker '{name}'",
                    extra={
                        "circuit_name": name,
                        "failure_threshold": failure_threshold,
                        "recovery_timeout_seconds": recovery_timeout_seconds,
                    },
                )
            return self._breakers[name]

    def get_all_states(self) -> dict[str, dict[str, Any]]:
        """Get state of all registered circuit breakers.

        Returns:
            Dict mapping breaker name to metrics dict

        Example Response:
            {
                "trolley_api": {
                    "state": "closed",
                    "failure_count": 0,
                    "success_count": 150,
                    "last_failure_time": None,
                    "last_success_time": "2026-04-19T12:00:00Z",
                    "next_retry_time": None
                },
                "spotify_api": {
                    "state": "open",
                    "failure_count": 5,
                    "success_count": 42,
                    "last_failure_time": "2026-04-19T11:55:00Z",
                    "last_success_time": "2026-04-19T11:50:00Z",
                    "next_retry_time": 1713531300
                }
            }
        """
        with self._breakers_lock:
            return {name: breaker.get_metrics() for name, breaker in self._breakers.items()}

    def reset_all(self) -> None:
        """Reset all circuit breakers to closed state."""
        with self._breakers_lock:
            for breaker in self._breakers.values():
                breaker.reset()

    def reset(self, name: str) -> None:
        """Reset specific circuit breaker."""
        with self._breakers_lock:
            if name in self._breakers:
                self._breakers[name].reset()
            else:
                logger.warning(f"Circuit breaker '{name}' not found")


# Convenience function for global access
def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """Get circuit breaker from global registry.

    Args:
        name: Circuit breaker identifier
        **kwargs: Passed to get_or_create

    Returns:
        CircuitBreaker instance
    """
    return CircuitBreakerRegistry.get_instance().get_or_create(name, **kwargs)
