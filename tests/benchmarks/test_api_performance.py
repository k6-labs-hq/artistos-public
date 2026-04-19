"""
Performance benchmark tests for XR7 Engine.

These tests measure baseline performance for critical endpoints.
Run with: pytest tests/benchmarks/ -v --benchmark-only

Performance budgets:
- Health check: p95 < 50ms
- Artist lookup: p95 < 200ms
- Dashboard load: p95 < 1000ms
- Statement upload: p95 < 5000ms for 100KB file
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from XR7.api.app import app

client = TestClient(app)


@pytest.fixture
def sample_artist_id():
    """Create a test artist and return ID."""
    # In real implementation, create test data
    return "test-artist-123"


def test_health_endpoint_latency(benchmark):
    """Benchmark health check endpoint.

    Performance budget: p95 < 50ms
    """

    def run():
        response = client.get("/health")
        assert response.status_code == 200
        return response

    result = benchmark(run)
    assert result.status_code == 200


def test_readiness_endpoint_latency(benchmark):
    """Benchmark readiness check endpoint.

    Performance budget: p95 < 100ms
    """

    def run():
        response = client.get("/health/readiness")
        assert response.status_code == 200
        return response

    result = benchmark(run)
    assert result.status_code == 200


def test_openapi_spec_latency(benchmark):
    """Benchmark OpenAPI spec generation.

    Performance budget: p95 < 200ms
    """

    def run():
        response = client.get("/openapi.json")
        assert response.status_code == 200
        return response

    result = benchmark(run)
    assert result.status_code == 200


# Additional benchmark tests can be added here for:
# - Artist dashboard load
# - Claims list pagination
# - Statement upload processing
# - Anomaly detection runs
