"""Provider resilience primitives for the XR7 fingerprinting subsystem.

Provides two mechanisms:
    - ProviderCircuitBreaker  — per-provider circuit breaker (CLOSED / OPEN / HALF-OPEN)
    - TokenBucketRateLimiter  — async token bucket rate limiter per provider
    - CircuitBreakerRegistry  — module-level singleton registry (one CB per provider)

Integration pattern::

    registry = get_circuit_registry()
    cb = registry.get("acrcloud")

    if cb.is_open():
        raise ProviderCircuitOpenError("acrcloud")
    try:
        result = await adapter.match_audio(...)
        cb.record_success()
    except Exception:
        cb.record_failure()
        raise
"""

from __future__ import annotations

import asyncio
import enum
import time
from collections import defaultdict
from typing import Any

from xr7_common.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Circuit Breaker
# ---------------------------------------------------------------------------


class CircuitState(str, enum.Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing — reject all calls fast
    HALF_OPEN = "half_open"  # Probe — let one call through


class ProviderCircuitOpenError(Exception):
    """Raised when a provider's circuit is open and the call is fast-rejected."""

    def __init__(self, provider: str) -> None:
        super().__init__(f"Circuit breaker for provider '{provider}' is OPEN — call rejected.")
        self.provider = provider


class ProviderCircuitBreaker:
    """Per-provider circuit breaker.

    States
    ------
    CLOSED    Normal.  Tracks consecutive failures.  After ``failure_threshold``
              consecutive failures, transitions to OPEN.
    OPEN      All calls are fast-rejected without hitting the provider.
              After ``recovery_timeout`` seconds, transitions to HALF_OPEN.
    HALF_OPEN One probe call is allowed.  Success → CLOSED.  Failure → OPEN.
    """

    def __init__(
        self,
        provider: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ) -> None:
        self._provider = provider
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout

        self._state: CircuitState = CircuitState.CLOSED
        self._consecutive_failures: int = 0
        self._opened_at: float = 0.0
        self._probe_in_flight: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def state(self) -> CircuitState:
        self._maybe_transition_to_half_open()
        return self._state

    def is_open(self) -> bool:
        """Return True if this call should be fast-rejected."""
        state = self.state
        if state == CircuitState.OPEN:
            return True
        if state == CircuitState.HALF_OPEN and self._probe_in_flight:
            # A probe is already in flight — reject extra callers
            return True
        return False

    def allow_probe(self) -> bool:
        """Claim the HALF_OPEN probe slot. Returns True if probe is allowed."""
        self._maybe_transition_to_half_open()
        if self._state == CircuitState.HALF_OPEN and not self._probe_in_flight:
            self._probe_in_flight = True
            return True
        return False

    def record_success(self) -> None:
        """Record a successful call; close the circuit if it was half-open."""
        if self._state in (CircuitState.HALF_OPEN, CircuitState.OPEN):
            logger.info(
                "circuit_breaker provider=%s state=HALF_OPEN→CLOSED (probe succeeded)",
                self._provider,
            )
        self._state = CircuitState.CLOSED
        self._consecutive_failures = 0
        self._probe_in_flight = False

    def record_failure(self) -> None:
        """Record a failed call; open the circuit if threshold is reached."""
        self._probe_in_flight = False
        if self._state == CircuitState.HALF_OPEN:
            # Probe failed — back to OPEN with a fresh timer
            self._opened_at = time.monotonic()
            self._state = CircuitState.OPEN
            logger.warning(
                "circuit_breaker provider=%s state=HALF_OPEN→OPEN (probe failed)",
                self._provider,
            )
            return

        self._consecutive_failures += 1
        if self._consecutive_failures >= self._failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = time.monotonic()
            logger.error(
                "circuit_breaker provider=%s state=CLOSED→OPEN "
                "consecutive_failures=%d threshold=%d",
                self._provider,
                self._consecutive_failures,
                self._failure_threshold,
            )

    def reset(self) -> None:
        """Manually reset to CLOSED (e.g. after config reload)."""
        self._state = CircuitState.CLOSED
        self._consecutive_failures = 0
        self._probe_in_flight = False
        logger.info("circuit_breaker provider=%s manually reset to CLOSED", self._provider)

    def status(self) -> dict[str, Any]:
        """Return a health-check-friendly status dict."""
        return {
            "provider": self._provider,
            "state": self.state.value,
            "consecutive_failures": self._consecutive_failures,
            "failure_threshold": self._failure_threshold,
            "recovery_timeout_s": self._recovery_timeout,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _maybe_transition_to_half_open(self) -> None:
        if (
            self._state == CircuitState.OPEN
            and (time.monotonic() - self._opened_at) >= self._recovery_timeout
        ):
            self._state = CircuitState.HALF_OPEN
            logger.info(
                "circuit_breaker provider=%s state=OPEN→HALF-OPEN "
                "(recovery_timeout=%.0fs elapsed)",
                self._provider,
                self._recovery_timeout,
            )


# ---------------------------------------------------------------------------
# Circuit Breaker Registry (module-level singleton)
# ---------------------------------------------------------------------------


class CircuitBreakerRegistry:
    """Registry that lazily creates one ProviderCircuitBreaker per provider."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._breakers: dict[str, ProviderCircuitBreaker] = {}

    def get(self, provider: str) -> ProviderCircuitBreaker:
        if provider not in self._breakers:
            self._breakers[provider] = ProviderCircuitBreaker(
                provider=provider,
                failure_threshold=self._failure_threshold,
                recovery_timeout=self._recovery_timeout,
            )
        return self._breakers[provider]

    def all_statuses(self) -> list[dict[str, Any]]:
        return [cb.status() for cb in self._breakers.values()]

    def reset_all(self) -> None:
        for cb in self._breakers.values():
            cb.reset()


_registry: CircuitBreakerRegistry | None = None


def get_circuit_registry() -> CircuitBreakerRegistry:
    """Return the module-level circuit breaker registry (lazy init)."""
    global _registry
    if _registry is None:
        import os

        threshold = int(os.getenv("XR7_FP_CB_FAILURE_THRESHOLD", "5"))
        recovery = float(os.getenv("XR7_FP_CB_RECOVERY_TIMEOUT", "60"))
        _registry = CircuitBreakerRegistry(
            failure_threshold=threshold,
            recovery_timeout=recovery,
        )
    return _registry


# ---------------------------------------------------------------------------
# Token-Bucket Rate Limiter
# ---------------------------------------------------------------------------


class TokenBucketRateLimiter:
    """Async token-bucket rate limiter.

    Allows up to ``rate_per_minute`` calls per 60-second window.  Callers
    ``await limiter.acquire()`` which sleeps only if the bucket is empty.

    Thread/task safe via asyncio.Lock.
    """

    def __init__(self, rate_per_minute: int) -> None:
        if rate_per_minute <= 0:
            rate_per_minute = 1_000_000  # effectively unlimited
        self._rate_per_second: float = rate_per_minute / 60.0
        self._tokens: float = self._rate_per_second
        self._max_tokens: float = max(self._rate_per_second * 10, 10.0)
        self._last_refill: float = time.monotonic()
        self._lock: asyncio.Lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Block until a token is available, then consume one."""
        async with self._lock:
            self._refill()
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return
            # Calculate wait time for one token to become available
            wait = (1.0 - self._tokens) / self._rate_per_second
        await asyncio.sleep(wait)
        async with self._lock:
            self._refill()
            self._tokens = max(0.0, self._tokens - 1.0)

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._max_tokens, self._tokens + elapsed * self._rate_per_second)
        self._last_refill = now


# ---------------------------------------------------------------------------
# Rate Limiter Registry (module-level singleton)
# ---------------------------------------------------------------------------

_rate_limiters: dict[str, TokenBucketRateLimiter] = defaultdict(
    lambda: TokenBucketRateLimiter(1_000_000)
)


def get_rate_limiter(provider: str, rate_per_minute: int) -> TokenBucketRateLimiter:
    """Return (or create) a rate limiter for a provider."""
    if provider not in _rate_limiters or isinstance(
        _rate_limiters[provider],
        type(_rate_limiters.default_factory()),  # type: ignore[misc]
    ):
        _rate_limiters[provider] = TokenBucketRateLimiter(rate_per_minute)
    return _rate_limiters[provider]
