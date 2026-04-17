from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass
class _BreakerState:
    failures: int = 0
    opened_at: float | None = None


class CircuitBreakerOpenError(RuntimeError):
    pass


class CircuitBreaker:
    """Small in-process circuit breaker for connector outbound operations."""

    def __init__(self, *, failure_threshold: int = 3, recovery_timeout_seconds: int = 60) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self._state = _BreakerState()
        self._lock = threading.Lock()

    def _is_open(self) -> bool:
        if self._state.opened_at is None:
            return False
        return (time.time() - self._state.opened_at) < self.recovery_timeout_seconds

    def run(self, func: Callable[[], T], *, operation_name: str) -> T:
        with self._lock:
            if self._is_open():
                raise CircuitBreakerOpenError(f"Circuit open for operation '{operation_name}'")

        try:
            result = func()
        except Exception:
            with self._lock:
                self._state.failures += 1
                if self._state.failures >= self.failure_threshold:
                    self._state.opened_at = time.time()
            raise

        with self._lock:
            self._state.failures = 0
            self._state.opened_at = None
        return result
