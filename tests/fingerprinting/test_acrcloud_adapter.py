"""Unit tests for the ACRCloud provider adapter."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from XR7.fingerprinting.adapters.acrcloud import ACRCloudAdapter
from XR7.fingerprinting.config import ACRCloudConfig
from XR7.fingerprinting.schema import MatchType, ProviderStatus


@pytest.fixture
def acrcloud_config():
    return ACRCloudConfig(
        enabled=True,
        access_key="test-key",
        access_secret="test-secret",
        endpoint="https://identify-us-west-2.acrcloud.com",
        timeout_seconds=10.0,
        max_retries=1,
        rate_limit_per_minute=100,
        priority=1,
    )


@pytest.fixture
def adapter(acrcloud_config):
    return ACRCloudAdapter(config=acrcloud_config)


class TestACRCloudAdapterIdentity:
    def test_provider_name(self, adapter):
        assert adapter.provider_name == "acrcloud"


class TestACRCloudAdapterSignature:
    def test_sign_produces_base64_string(self, adapter):
        sig = adapter._sign("POST", "/v1/identify", "audio", "1700000000")
        assert isinstance(sig, str)
        assert len(sig) > 0

    def test_identify_params_has_required_keys(self, adapter):
        params = adapter._identify_params(1024, "1700000000")
        assert "access_key" in params
        assert "signature" in params
        assert "signature_version" in params
        assert "timestamp" in params
        assert params["sample_bytes"] == "1024"


class TestACRCloudNormalizeResponse:
    def test_no_match_code_returns_empty(self, adapter):
        raw = {"status": {"code": 1001, "msg": "No result"}}
        results = adapter.normalize_provider_response(raw)
        assert results == []

    def test_success_returns_normalized_results(self, adapter):
        raw = {
            "status": {"code": 0, "msg": "Success"},
            "metadata": {
                "music": [
                    {
                        "acrid": "abc123",
                        "title": "Test Song",
                        "score": 85,
                        "artists": [{"name": "Test Artist"}],
                        "external_ids": {"isrc": "USAT12345678"},
                        "duration_ms": 210000,
                        "album": {"name": "Test Album"},
                    }
                ]
            },
        }
        results = adapter.normalize_provider_response(raw)
        assert len(results) == 1
        r = results[0]
        assert r.provider == "acrcloud"
        assert r.isrc == "USAT12345678"
        assert r.confidence_score == pytest.approx(0.85)
        assert r.title == "Test Song"
        assert r.artist_name == "Test Artist"
        assert r.duration_seconds == pytest.approx(210.0)
        assert r.track_id == "abc123"
        assert r.match_type == MatchType.UNKNOWN

    def test_confidence_capped_at_1(self, adapter):
        raw = {
            "status": {"code": 0, "msg": "Success"},
            "metadata": {
                "music": [
                    {
                        "acrid": "x",
                        "title": "T",
                        "score": 120,  # over 100
                        "artists": [],
                        "external_ids": {},
                    }
                ]
            },
        }
        results = adapter.normalize_provider_response(raw)
        assert results[0].confidence_score <= 1.0

    def test_empty_music_list_returns_empty(self, adapter):
        raw = {"status": {"code": 0, "msg": "Success"}, "metadata": {"music": []}}
        results = adapter.normalize_provider_response(raw)
        assert results == []


class TestACRCloudHealthCheck:
    @pytest.mark.asyncio
    async def test_healthy_when_status_200(self, adapter):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(adapter, "_client_") as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.head = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client

            status = await adapter.get_provider_health()
            assert status.status == ProviderStatus.HEALTHY
            assert status.provider == "acrcloud"
            assert status.latency_ms is not None

    @pytest.mark.asyncio
    async def test_down_on_exception(self, adapter):
        with patch.object(adapter, "_client_") as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.head = AsyncMock(side_effect=Exception("connection refused"))
            mock_client_fn.return_value = mock_client

            status = await adapter.get_provider_health()
            assert status.status == ProviderStatus.DOWN
            assert "connection refused" in (status.error_message or "")


class TestACRCloudMatchAudio:
    @pytest.mark.asyncio
    async def test_match_audio_returns_normalized_results(self, adapter):
        raw_response = {
            "status": {"code": 0, "msg": "Success"},
            "metadata": {
                "music": [
                    {
                        "acrid": "test-acrid",
                        "title": "My Song",
                        "score": 90,
                        "artists": [{"name": "My Artist"}],
                        "external_ids": {"isrc": "USAT00000001"},
                        "duration_ms": 180000,
                    }
                ]
            },
        }

        mock_response = MagicMock()
        mock_response.json.return_value = raw_response
        mock_response.raise_for_status = MagicMock()

        with patch.object(adapter, "_client_") as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client

            results = await adapter.match_audio(b"fake_audio_bytes")
            assert len(results) == 1
            assert results[0].isrc == "USAT00000001"
            assert results[0].title == "My Song"
