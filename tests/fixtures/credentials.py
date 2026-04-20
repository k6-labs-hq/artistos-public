"""Test credential fixture system for integration tests.

Issue #13: Integration Test Credentials Management

Provides stubbed credentials for:
- Trolley payment gateway
- PRO (Performing Rights Organization) APIs
- OAuth platforms (Spotify, YouTube, SoundCloud)

Allows credential-gated tests to run in CI without real API keys.
"""

import os
from typing import Generator
import pytest


class StubCredentials:
    """Stubbed credential provider for testing."""
    
    def __init__(self):
        self.trolley_api_key = os.getenv("TROLLEY_API_KEY_TEST", "test_trolley_key_stub")
        self.trolley_secret_key = os.getenv("TROLLEY_SECRET_KEY_TEST", "test_trolley_secret_stub")
        self.spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID_TEST", "test_spotify_client_stub")
        self.spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET_TEST", "test_spotify_secret_stub")
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY_TEST", "test_youtube_key_stub")
        self.soundcloud_client_id = os.getenv("SOUNDCLOUD_CLIENT_ID_TEST", "test_soundcloud_client_stub")
        
        # PRO credentials
        self.ascap_api_key = os.getenv("ASCAP_API_KEY_TEST", "test_ascap_key_stub")
        self.bmi_api_key = os.getenv("BMI_API_KEY_TEST", "test_bmi_key_stub")
        self.sesac_api_key = os.getenv("SESAC_API_KEY_TEST", "test_sesac_key_stub")
    
    def is_real(self) -> bool:
        """Check if using real credentials (not stubs)."""
        return not self.trolley_api_key.endswith("_stub")


@pytest.fixture(scope="session")
def credentials() -> StubCredentials:
    """
    Provide test credentials for integration tests.
    
    Usage:
        ```python
        def test_trolley_payout(credentials):
            if credentials.is_real():
                # Run actual API test
                pass
            else:
                # Run stub test
                pass
        ```
    
    In CI: Uses stub credentials (no real API calls)
    Locally: Set real credentials in .env.test to run full integration tests
    """
    return StubCredentials()


@pytest.fixture(scope="function")
def mock_trolley_response():
    """Mock Trolley API response for payout creation."""
    return {
        "ok": True,
        "recipient": {
            "id": "R-test123",
            "email": "artist@example.com",
            "status": "active",
        },
        "payment": {
            "id": "P-test456",
            "amount": "1000.00",
            "currency": "USD",
            "status": "pending",
        },
    }


@pytest.fixture(scope="function")
def mock_spotify_auth_response():
    """Mock Spotify OAuth token response."""
    return {
        "access_token": "test_access_token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "test_refresh_token",
        "scope": "user-read-private streaming-analytics",
    }


@pytest.fixture(scope="function")
def mock_pro_royalty_data():
    """Mock PRO (ASCAP/BMI/SESAC) royalty statement data."""
    return {
        "statements": [
            {
                "period": "2025-Q4",
                "work_title": "Test Song",
                "iswc": "T-123.456.789-0",
                "performance_count": 1000,
                "royalty_amount": 250.00,
                "territory": "US",
                "usage_type": "streaming",
            }
        ],
        "total_royalties": 250.00,
        "currency": "USD",
    }


# Environment setup for test discovery
def pytest_configure(config):
    """Configure test environment with stub credentials if none provided."""
    # Only stub if not already set
    if not os.getenv("TROLLEY_API_KEY_TEST"):
        os.environ["TROLLEY_API_KEY_TEST"] = "test_trolley_key_stub"
    if not os.getenv("SPOTIFY_CLIENT_ID_TEST"):
        os.environ["SPOTIFY_CLIENT_ID_TEST"] = "test_spotify_client_stub"
    if not os.getenv("YOUTUBE_API_KEY_TEST"):
        os.environ["YOUTUBE_API_KEY_TEST"] = "test_youtube_key_stub"
