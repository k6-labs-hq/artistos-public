"""Tests for /health endpoint with dependency connectivity checks."""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from XR7.api.app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_env_settings():
    """Mock environment settings for tests."""
    with (
        patch.dict(
            os.environ,
            {
                "REDIS_URL": "redis://localhost:6379/0",
                "S3_ENDPOINT_URL": "http://localhost:9000",
                "S3_ACCESS_KEY_ID": "test-key",
                "S3_SECRET_ACCESS_KEY": "test-secret",
                "S3_BUCKET": "test-bucket",
            },
        ),
    ):
        yield


def test_health_all_dependencies_healthy(client, mock_env_settings):
    """Test /health returns 200 when all dependencies are reachable."""
    with (
        patch("sqlalchemy.engine.base.Engine.connect") as mock_db,
        patch("redis.Redis.from_url") as mock_redis,
        patch("boto3.client") as mock_s3,
    ):
        # Mock successful database connection
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = None

        # Mock successful Redis connection
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance

        # Mock successful S3 connection
        mock_s3_instance = MagicMock()
        mock_s3_instance.head_bucket.return_value = {}
        mock_s3.return_value = mock_s3_instance

        response = client.get("/health")

        data = response.json()
        assert response.status_code == 200
        assert data["status"] == "ok"
        assert data["version"] == "2.0.0"
        assert "checks" in data
        assert data["checks"]["database"]["status"] == "ok"
        assert data["checks"]["redis"]["status"] == "ok"
        assert data["checks"]["s3"]["status"] == "ok"
        assert "latency_ms" in data["checks"]["database"]
        assert "latency_ms" in data["checks"]["redis"]
        assert "latency_ms" in data["checks"]["s3"]


def test_health_database_failure(client, mock_env_settings):
    """Test /health returns 503 when database is unreachable."""
    with (
        patch("sqlalchemy.engine.base.Engine.connect") as mock_db,
        patch("redis.Redis.from_url") as mock_redis,
        patch("boto3.client") as mock_s3,
    ):
        # Mock database connection failure
        mock_db.side_effect = Exception("Connection refused")

        # Mock other services as healthy
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance

        mock_s3_instance = MagicMock()
        mock_s3_instance.head_bucket.return_value = {}
        mock_s3.return_value = mock_s3_instance

        response = client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["checks"]["database"]["status"] == "fail"
        assert "Connection refused" in data["checks"]["database"]["error"]
        assert data["checks"]["redis"]["status"] == "ok"
        assert data["checks"]["s3"]["status"] == "ok"


def test_health_redis_failure(client, mock_env_settings):
    """Test /health returns 503 when Redis is unreachable."""
    with (
        patch("sqlalchemy.engine.base.Engine.connect") as mock_db,
        patch("redis.Redis.from_url") as mock_redis,
        patch("boto3.client") as mock_s3,
    ):
        # Mock database as healthy
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = None

        # Mock Redis connection failure
        mock_redis.side_effect = Exception("Connection timeout")

        # Mock S3 as healthy
        mock_s3_instance = MagicMock()
        mock_s3_instance.head_bucket.return_value = {}
        mock_s3.return_value = mock_s3_instance

        response = client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["checks"]["database"]["status"] == "ok"
        assert data["checks"]["redis"]["status"] == "fail"
        assert "Connection timeout" in data["checks"]["redis"]["error"]
        assert data["checks"]["s3"]["status"] == "ok"


def test_health_s3_failure(client, mock_env_settings):
    """Test /health returns 503 when S3 is unreachable."""
    with (
        patch("sqlalchemy.engine.base.Engine.connect") as mock_db,
        patch("redis.Redis.from_url") as mock_redis,
        patch("boto3.client") as mock_s3,
    ):
        # Mock database as healthy
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = None

        # Mock Redis as healthy
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance

        # Mock S3 connection failure
        mock_s3_instance = MagicMock()
        mock_s3_instance.head_bucket.side_effect = Exception("Network unreachable")
        mock_s3_instance.list_buckets.side_effect = Exception("Network unreachable")
        mock_s3.return_value = mock_s3_instance

        response = client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["checks"]["database"]["status"] == "ok"
        assert data["checks"]["redis"]["status"] == "ok"
        assert data["checks"]["s3"]["status"] == "fail"
        assert "Network unreachable" in data["checks"]["s3"]["error"]


def test_health_multiple_failures(client, mock_env_settings):
    """Test /health returns 503 when multiple dependencies fail."""
    with (
        patch("sqlalchemy.engine.base.Engine.connect") as mock_db,
        patch("redis.Redis.from_url") as mock_redis,
        patch("boto3.client") as mock_s3,
    ):
        # Mock all services as failing
        mock_db.side_effect = Exception("Database connection error")
        mock_redis.side_effect = Exception("Redis connection error")
        mock_s3_instance = MagicMock()
        mock_s3_instance.head_bucket.side_effect = Exception("S3 connection error")
        mock_s3_instance.list_buckets.side_effect = Exception("S3 connection error")
        mock_s3.return_value = mock_s3_instance

        response = client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["checks"]["database"]["status"] == "fail"
        assert data["checks"]["redis"]["status"] == "fail"
        assert data["checks"]["s3"]["status"] == "fail"


def test_health_latency_measured(client, mock_env_settings):
    """Test that latency is measured for each dependency check."""
    with (
        patch("sqlalchemy.engine.base.Engine.connect") as mock_db,
        patch("redis.Redis.from_url") as mock_redis,
        patch("boto3.client") as mock_s3,
    ):
        # Mock all services as healthy
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = None

        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance

        mock_s3_instance = MagicMock()
        mock_s3_instance.head_bucket.return_value = {}
        mock_s3.return_value = mock_s3_instance

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        # Latency should be a positive number
        assert data["checks"]["database"]["latency_ms"] >= 0
        assert data["checks"]["redis"]["latency_ms"] >= 0
        assert data["checks"]["s3"]["latency_ms"] >= 0


def test_health_redis_not_configured(client):
    """Test /health when Redis URL is not configured."""
    with (
        patch("sqlalchemy.engine.base.Engine.connect") as mock_db,
        patch("boto3.client") as mock_s3,
        patch.dict(os.environ, {"REDIS_URL": ""}),
    ):
        # Mock database as healthy
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = None

        # Mock S3 as healthy
        mock_s3_instance = MagicMock()
        mock_s3_instance.head_bucket.return_value = {}
        mock_s3.return_value = mock_s3_instance

        response = client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["checks"]["redis"]["status"] == "not_configured"


def test_health_s3_not_configured(client):
    """Test /health when S3 credentials are not configured."""
    with (
        patch("sqlalchemy.engine.base.Engine.connect") as mock_db,
        patch("redis.Redis.from_url") as mock_redis,
        patch.dict(os.environ, {"S3_ENDPOINT_URL": ""}),
    ):
        # Mock database as healthy
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = None

        # Mock Redis as healthy
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance

        response = client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["checks"]["s3"]["status"] == "not_configured"


def test_health_s3_bucket_missing_fallback_to_list(client, mock_env_settings):
    """Test /health falls back to list_buckets when head_bucket fails."""
    with (
        patch("sqlalchemy.engine.base.Engine.connect") as mock_db,
        patch("redis.Redis.from_url") as mock_redis,
        patch("boto3.client") as mock_s3,
    ):
        # Mock database as healthy
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = None

        # Mock Redis as healthy
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance

        # Mock S3: head_bucket fails (bucket doesn't exist), but list_buckets succeeds
        mock_s3_instance = MagicMock()
        mock_s3_instance.head_bucket.side_effect = Exception("NoSuchBucket")
        mock_s3_instance.list_buckets.return_value = {"Buckets": []}
        mock_s3.return_value = mock_s3_instance

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["checks"]["s3"]["status"] == "ok"
        # Verify fallback was attempted
        mock_s3_instance.list_buckets.assert_called_once()


def test_health_error_message_truncation(client, mock_env_settings):
    """Test that error messages are truncated to 200 characters."""
    with (
        patch("sqlalchemy.engine.base.Engine.connect") as mock_db,
        patch("redis.Redis.from_url") as mock_redis,
        patch("boto3.client") as mock_s3,
    ):
        # Create a very long error message
        long_error = "x" * 500
        mock_db.side_effect = Exception(long_error)

        # Mock other services as healthy
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance

        mock_s3_instance = MagicMock()
        mock_s3_instance.head_bucket.return_value = {}
        mock_s3.return_value = mock_s3_instance

        response = client.get("/health")

        assert response.status_code == 503
        data = response.json()
        # Error message should be truncated
        assert len(data["checks"]["database"]["error"]) == 200
