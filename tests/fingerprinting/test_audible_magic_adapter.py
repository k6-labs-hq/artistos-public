"""Unit tests for the Audible Magic provider adapter."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from XR7.fingerprinting.adapters.audible_magic import AudibleMagicAdapter
from XR7.fingerprinting.config import AudibleMagicConfig
from XR7.fingerprinting.schema import MatchType, ProviderStatus


@pytest.fixture
def am_config():
    return AudibleMagicConfig(
        enabled=True,
        api_key="am-test-key",
        endpoint="https://api.audiblemagic.com/v2",
        timeout_seconds=10.0,
        max_retries=1,
    )


@pytest.fixture
def adapter(am_config):
    return AudibleMagicAdapter(config=am_config)


class TestAudibleMagicIdentity:
    def test_provider_name(self, adapter):
        assert adapter.provider_name == "audible_magic"


class TestAudibleMagicNormalize:
    def test_normalize_success_response(self, adapter):
        raw = {
            "status": "success",
            "results": [
                {
                    "track_id": "am-001",
                    "isrc": "USAT12345678",
                    "iswc": "T-111111111-1",
                    "title": "AM Track",
                    "artist": "AM Artist",
                    "confidence": 0.97,
                    "match_type": "broadcast",
                    "territory": "US",
                }
            ],
        }
        results = adapter.normalize_provider_response(raw)
        assert len(results) == 1
        r = results[0]
        assert r.provider == "audible_magic"
        assert r.isrc == "USAT12345678"
        assert r.iswc == "T-111111111-1"
        assert r.confidence_score == pytest.approx(0.97)
        assert r.match_type == MatchType.BROADCAST
        assert r.territory == "US"

    def test_normalize_non_success_returns_empty(self, adapter):
        raw = {"status": "error", "results": []}
        results = adapter.normalize_provider_response(raw)
        assert results == []

    def test_normalize_empty_results(self, adapter):
        raw = {"status": "success", "results": []}
        results = adapter.normalize_provider_response(raw)
        assert results == []

    def test_normalize_confidence_caps_at_1(self, adapter):
        raw = {
            "status": "success",
            "results": [{"confidence": 2.5, "match_type": "stream"}],
        }
        results = adapter.normalize_provider_response(raw)
        assert results[0].confidence_score <= 1.0


class TestAudibleMagicMatchAudio:
    @pytest.mark.asyncio
    async def test_match_audio_calls_synchronous_endpoint(self, adapter):
        raw_response = {
            "status": "success",
            "results": [
                {
                    "track_id": "am-sync-001",
                    "isrc": "GBZZZ9876543",
                    "title": "Sync Result",
                    "artist": "Sync Artist",
                    "confidence": 0.88,
                    "match_type": "ugc",
                    "territory": "GB",
                }
            ],
        }
        mock_response = MagicMock()
        mock_response.json.return_value = raw_response
        mock_response.raise_for_status = MagicMock()

        with patch.object(adapter, "_client_") as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client

            results = await adapter.match_audio(b"audio")
            assert len(results) == 1
            assert results[0].isrc == "GBZZZ9876543"
            assert results[0].match_type == MatchType.UGC


class TestAudibleMagicHealthCheck:
    @pytest.mark.asyncio
    async def test_healthy_on_200(self, adapter):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(adapter, "_client_") as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client

            health = await adapter.get_provider_health()
            assert health.status == ProviderStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_down_on_exception(self, adapter):
        with patch.object(adapter, "_client_") as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("timeout"))
            mock_client_fn.return_value = mock_client

            health = await adapter.get_provider_health()
            assert health.status == ProviderStatus.DOWN
