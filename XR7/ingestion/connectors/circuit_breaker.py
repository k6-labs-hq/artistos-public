"""Circuit breaker utilities for ingestion connectors.

Re-exports circuit breaker primitives from the fingerprinting subsystem
for use in ingestion connector resilience patterns.
"""

from XR7.fingerprinting._resilience import (
    CircuitBreakerRegistry,
    CircuitState,
    ProviderCircuitBreaker,
    ProviderCircuitOpenError,
    get_circuit_registry,
)

# Alias for backward compatibility with connector imports
CircuitBreaker = ProviderCircuitBreaker

__all__ = [
    "CircuitBreaker",
    "ProviderCircuitBreaker",
    "CircuitBreakerRegistry",
    "CircuitState",
    "ProviderCircuitOpenError",
    "get_circuit_registry",
]
