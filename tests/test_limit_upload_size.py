"""Tests for LimitUploadSizeMiddleware."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from XR7.api.middleware.limit_upload_size import LimitUploadSizeMiddleware


@pytest.fixture
def app():
    """Create test FastAPI app with LimitUploadSizeMiddleware."""
    app = FastAPI()
    # Set limit to 10MB for testing
    app.add_middleware(LimitUploadSizeMiddleware, max_upload_size=10 * 1024 * 1024)

    @app.post("/upload")
    async def upload_endpoint():
        return {"status": "success"}

    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app, raise_server_exceptions=False)


def test_request_under_limit_allowed(client):
    """Test that requests under the size limit are allowed."""
    # 5MB payload
    headers = {"Content-Length": str(5 * 1024 * 1024)}
    response = client.post("/upload", headers=headers, content=b"test")
    assert response.status_code == 200


def test_request_at_limit_allowed(client):
    """Test that requests exactly at the limit are allowed."""
    # Exactly 10MB
    headers = {"Content-Length": str(10 * 1024 * 1024)}
    response = client.post("/upload", headers=headers, content=b"test")
    assert response.status_code == 200


def test_request_over_limit_rejected(client):
    """Test that requests over the limit are rejected with 413."""
    # 11MB payload (over 10MB limit)
    headers = {"Content-Length": str(11 * 1024 * 1024)}
    response = client.post("/upload", headers=headers, content=b"test")
    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()
    assert "10.0 MB" in response.json()["detail"]
    assert "11.0 MB" in response.json()["detail"]


def test_request_without_content_length_allowed(client):
    """Test that requests without Content-Length header pass through."""
    # No Content-Length header
    response = client.post("/upload", content=b"test")
    # Should succeed (or fail for other reasons, but not 413)
    # TestClient may add Content-Length automatically, so we check it's not 413
    assert response.status_code != 413


def test_request_with_invalid_content_length_allowed(client):
    """Test that requests with invalid Content-Length are allowed to pass."""
    # Invalid Content-Length
    headers = {"Content-Length": "not-a-number"}
    response = client.post("/upload", headers=headers, content=b"test")
    # Should not be rejected by our middleware (may fail later)
    assert response.status_code != 413


def test_default_100mb_limit():
    """Test that default limit is 100MB."""
    app = FastAPI()
    app.add_middleware(LimitUploadSizeMiddleware)  # No max_upload_size specified

    @app.post("/upload")
    async def upload_endpoint():
        return {"status": "success"}

    client = TestClient(app)

    # Just under 100MB should pass
    headers = {"Content-Length": str(99 * 1024 * 1024)}
    response = client.post("/upload", headers=headers, content=b"test")
    assert response.status_code == 200

    # Just over 100MB should fail
    headers = {"Content-Length": str(101 * 1024 * 1024)}
    response = client.post("/upload", headers=headers, content=b"test")
    assert response.status_code == 413
    assert "100.0 MB" in response.json()["detail"]


def test_helpful_error_message(client):
    """Test that error message provides helpful guidance."""
    headers = {"Content-Length": str(15 * 1024 * 1024)}
    response = client.post("/upload", headers=headers, content=b"test")
    assert response.status_code == 413
    detail = response.json()["detail"]
    assert "Maximum allowed" in detail
    assert "multipart upload" in detail or "contact support" in detail
