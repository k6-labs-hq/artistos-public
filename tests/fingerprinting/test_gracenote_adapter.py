"""Unit tests for the Gracenote provider adapter."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from XR7.fingerprinting.adapters.gracenote import GracenoteAdapter
from XR7.fingerprinting.config import GracenoteConfig
from XR7.fingerprinting.schema import MatchType, ProviderStatus


@pytest.fixture
def gn_config():
    return GracenoteConfig(
        enabled=True,
        client_id="gn-client-id",
        user_id="gn-user-id",
        api_key="gn-api-key",
        endpoint="https://c12345.web.cddbp.net/webapi/json/1.0",
        timeout_seconds=10.0,
    )


@pytest.fixture
def adapter(gn_config):
    return GracenoteAdapter(config=gn_config)


class TestGracenoteIdentity:
    def test_provider_name(self, adapter):
        assert adapter.provider_name == "gracenote"


class TestGracenoteNormalize:
    def test_normalize_ok_response(self, adapter):
        raw = {
            "status": "OK",
            "results": [
                {
                    "gn_id": "gn-001",
                    "isrc": "USRC12300001",
                    "title": "GN Track",
                    "artist": "GN Artist",
                    "confidence": 0.93,
                    "match_type": "BROADCAST",
                    "territory": "US",
                }
            ],
        }
        results = adapter.normalize_provider_response(raw)
        assert len(results) == 1
        r = results[0]
        assert r.track_id == "gn-001"
        assert r.isrc == "USRC12300001"
        assert r.confidence_score == pytest.approx(0.93)
        assert r.match_type == MatchType.BROADCAST
        assert r.provider == "gracenote"

    def test_non_ok_returns_empty(self, adapter):
        raw = {"status": "ERROR", "results": []}
        results = adapter.normalize_provider_response(raw)
        assert results == []

    def test_normalize_stream_type(self, adapter):
        raw = {
            "status": "OK",
            "results": [{"gn_id": "gn-002", "confidence": 0.8, "match_type": "STREAM"}],
        }
        results = adapter.normalize_provider_response(raw)
        assert results[0].match_type == MatchType.STREAM


class TestGracenoteMatchAudio:
    @pytest.mark.asyncio
    async def test_match_audio_parses_response(self, adapter):
        raw = {
            "status": "OK",
            "results": [
                {
                    "gn_id": "gn-xyz",
                    "isrc": "DEABC9876543",
                    "title": "German Track",
                    "artist": "DE Artist",
                    "confidence": 0.91,
                    "match_type": "RADIO",
                    "territory": "DE",
                }
            ],
        }
        mock_response = MagicMock()
        mock_response.json.return_value = raw
        mock_response.raise_for_status = MagicMock()

        with patch.object(adapter, "_client_") as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client

            results = await adapter.match_audio(b"audio_data")
            assert len(results) == 1
            assert results[0].isrc == "DEABC9876543"
            assert results[0].match_type == MatchType.RADIO
            assert results[0].territory == "DE"


class TestGracenoteHealthCheck:
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
            mock_client.get = AsyncMock(side_effect=ConnectionError("refused"))
            mock_client_fn.return_value = mock_client

            health = await adapter.get_provider_health()
            assert health.status == ProviderStatus.DOWN
