"""Unit tests for the Soundmouse provider adapter."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from XR7.fingerprinting.adapters.soundmouse import SoundmouseAdapter
from XR7.fingerprinting.config import SoundmouseConfig
from XR7.fingerprinting.schema import MatchType, ProviderStatus


@pytest.fixture
def sm_config():
    return SoundmouseConfig(
        enabled=True,
        api_key="sm-test-key",
        endpoint="https://api.soundmouse.com/v1",
        timeout_seconds=10.0,
        max_retries=1,
        rate_limit_per_minute=100,
        priority=5,
    )


@pytest.fixture
def adapter(sm_config):
    return SoundmouseAdapter(config=sm_config)


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


class TestSoundmouseAdapterIdentity:
    def test_provider_name(self, adapter):
        assert adapter.provider_name == "soundmouse"


# ---------------------------------------------------------------------------
# normalize_provider_response
# ---------------------------------------------------------------------------


class TestSoundmouseNormalize:
    def test_empty_returns_empty(self, adapter):
        assert adapter.normalize_provider_response({}) == []

    def test_error_status_returns_empty(self, adapter):
        assert adapter.normalize_provider_response({"status": "error", "matches": []}) == []

    def test_success_with_matches_key(self, adapter):
        raw = {
            "status": "success",
            "matches": [
                {
                    "track_id": "sm-001",
                    "isrc": "USAT12345678",
                    "title": "SM Track",
                    "artist": "SM Artist",
                    "confidence": 0.91,
                    "detection_type": "broadcast",
                    "territory": "US",
                    "platform": "bbc_radio",
                    "duration_ms": 200000,
                }
            ],
        }
        results = adapter.normalize_provider_response(raw)
        assert len(results) == 1
        r = results[0]
        assert r.provider == "soundmouse"
        assert r.isrc == "USAT12345678"
        assert r.track_id == "sm-001"
        assert r.title == "SM Track"
        assert r.artist_name == "SM Artist"
        assert r.confidence_score == pytest.approx(0.91)
        assert r.match_type == MatchType.BROADCAST
        assert r.territory == "US"
        assert r.platform == "bbc_radio"
        assert r.duration_seconds == pytest.approx(200.0)

    def test_success_with_results_key(self, adapter):
        raw = {
            "status": "ok",
            "results": [
                {
                    "track_id": "sm-002",
                    "isrc": "GBZZZ1234567",
                    "confidence": 0.7,
                    "detection_type": "streaming",
                }
            ],
        }
        results = adapter.normalize_provider_response(raw)
        assert len(results) == 1
        assert results[0].match_type == MatchType.STREAM

    def test_confidence_capped_at_1(self, adapter):
        raw = {
            "status": "success",
            "matches": [{"track_id": "x", "confidence": 999.0}],
        }
        results = adapter.normalize_provider_response(raw)
        assert results[0].confidence_score == pytest.approx(1.0)

    def test_found_status_treated_as_success(self, adapter):
        raw = {
            "status": "found",
            "matches": [{"confidence": 0.8, "detection_type": "ugc"}],
        }
        results = adapter.normalize_provider_response(raw)
        assert len(results) == 1
        assert results[0].match_type == MatchType.UGC

    def test_empty_status_string_treated_as_success(self, adapter):
        raw = {"matches": [{"confidence": 0.6, "detection_type": "sync"}]}
        results = adapter.normalize_provider_response(raw)
        assert len(results) == 1

    def test_unknown_type_maps_to_unknown(self, adapter):
        raw = {
            "status": "success",
            "matches": [{"confidence": 0.6, "detection_type": "bogus"}],
        }
        results = adapter.normalize_provider_response(raw)
        assert results[0].match_type == MatchType.UNKNOWN


# ---------------------------------------------------------------------------
# match_audio
# ---------------------------------------------------------------------------


class TestSoundmouseMatchAudio:
    @pytest.mark.asyncio
    async def test_match_audio_posts_to_identify(self, adapter):
        raw_response = {
            "status": "success",
            "matches": [
                {
                    "track_id": "sm-live-001",
                    "isrc": "USAT99001234",
                    "title": "Radio Hit",
                    "artist": "Radio Star",
                    "confidence": 0.83,
                    "detection_type": "radio",
                }
            ],
        }
        mock_response = MagicMock()
        mock_response.json.return_value = raw_response
        mock_response.raise_for_status = MagicMock()

        with patch.object(adapter, "_client_") as mock_client_fn, \
             patch.object(adapter._cb, "is_open", return_value=False), \
             patch.object(adapter._cb, "record_success"):
            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client
            with patch.object(adapter._limiter, "acquire", AsyncMock()):
                results = await adapter.match_audio(b"audio-bytes")

        assert len(results) == 1
        assert results[0].isrc == "USAT99001234"
        assert results[0].match_type == MatchType.RADIO

    @pytest.mark.asyncio
    async def test_match_audio_open_circuit_raises(self, adapter):
        from XR7.fingerprinting._resilience import ProviderCircuitOpenError

        with patch.object(adapter._cb, "is_open", return_value=True):
            with pytest.raises(ProviderCircuitOpenError):
                await adapter.match_audio(b"audio")


# ---------------------------------------------------------------------------
# submit_reference_file
# ---------------------------------------------------------------------------


class TestSoundmouseSubmitReference:
    @pytest.mark.asyncio
    async def test_returns_reference_id(self, adapter):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "sm-ref-456", "status": "registered"}
        mock_response.raise_for_status = MagicMock()

        with patch.object(adapter, "_client_") as mock_client_fn, \
             patch.object(adapter._cb, "is_open", return_value=False), \
             patch.object(adapter._cb, "record_success"):
            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client
            with patch.object(adapter._limiter, "acquire", AsyncMock()):
                ref_id = await adapter.submit_reference_file(b"audio", isrc="USAT11112222")

        assert ref_id == "sm-ref-456"


# ---------------------------------------------------------------------------
# detect_usage
# ---------------------------------------------------------------------------


class TestSoundmouseDetectUsage:
    @pytest.mark.asyncio
    async def test_returns_detections(self, adapter):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "matches": [
                {
                    "track_id": "sm-ref-det-001",
                    "confidence": 0.77,
                    "detection_type": "user_generated",
                    "platform": "tiktok",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(adapter, "_client_") as mock_client_fn, \
             patch.object(adapter._cb, "is_open", return_value=False), \
             patch.object(adapter._cb, "record_success"):
            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client
            with patch.object(adapter._limiter, "acquire", AsyncMock()):
                results = await adapter.detect_usage("sm-ref-456")

        assert len(results) == 1
        assert results[0].match_type == MatchType.UGC
        assert results[0].platform == "tiktok"


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


class TestSoundmouseHealthCheck:
    @pytest.mark.asyncio
    async def test_healthy_on_200(self, adapter):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(adapter, "_client_") as mock_client_fn:
            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client

            status = await adapter.get_provider_health()

        assert status.provider == "soundmouse"
        assert status.status == ProviderStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_unhealthy_on_connection_error(self, adapter):
        import httpx

        with patch.object(adapter, "_client_") as mock_client_fn:
            mock_client = MagicMock()
            mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
            mock_client_fn.return_value = mock_client

            status = await adapter.get_provider_health()

        assert status.status == ProviderStatus.DOWN
        assert "refused" in (status.error_message or "")
