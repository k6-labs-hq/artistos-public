"""Unit tests for the BMAT Musiio provider adapter."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from XR7.fingerprinting.adapters.bmat import BMATAdapter
from XR7.fingerprinting.config import BMATConfig
from XR7.fingerprinting.schema import MatchType, ProviderStatus


@pytest.fixture
def bmat_config():
    return BMATConfig(
        enabled=True,
        api_key="bmat-test-key",
        endpoint="https://api.bmat.com/v1",
        timeout_seconds=10.0,
        max_retries=1,
        rate_limit_per_minute=100,
        priority=4,
    )


@pytest.fixture
def adapter(bmat_config):
    return BMATAdapter(config=bmat_config)


# ---------------------------------------------------------------------------
# Identity / metadata
# ---------------------------------------------------------------------------


class TestBMATAdapterIdentity:
    def test_provider_name(self, adapter):
        assert adapter.provider_name == "bmat"


# ---------------------------------------------------------------------------
# normalize_provider_response
# ---------------------------------------------------------------------------


class TestBMATNormalizeResponse:
    def test_empty_response_returns_empty_list(self, adapter):
        assert adapter.normalize_provider_response({}) == []

    def test_non_success_status_returns_empty(self, adapter):
        assert adapter.normalize_provider_response({"status": "error"}) == []

    def test_success_with_matches_key(self, adapter):
        raw = {
            "status": "success",
            "matches": [
                {
                    "track_id": "bmat-001",
                    "isrc": "USAT12345678",
                    "title": "Test Track",
                    "artist": "Test Artist",
                    "confidence": 0.92,
                    "detection_type": "broadcast",
                    "territory": "US",
                    "duration_ms": 215000,
                }
            ],
        }
        results = adapter.normalize_provider_response(raw)
        assert len(results) == 1
        r = results[0]
        assert r.provider == "bmat"
        assert r.isrc == "USAT12345678"
        assert r.track_id == "bmat-001"
        assert r.title == "Test Track"
        assert r.artist_name == "Test Artist"
        assert r.confidence_score == pytest.approx(0.92)
        assert r.match_type == MatchType.BROADCAST
        assert r.territory == "US"
        assert r.duration_seconds == pytest.approx(215.0)

    def test_success_with_results_key(self, adapter):
        raw = {
            "status": "ok",
            "results": [
                {
                    "track_id": "bmat-002",
                    "isrc": "GBZZZ1234567",
                    "confidence": 0.75,
                    "detection_type": "radio",
                }
            ],
        }
        results = adapter.normalize_provider_response(raw)
        assert len(results) == 1
        assert results[0].match_type == MatchType.RADIO
        assert results[0].isrc == "GBZZZ1234567"

    def test_success_with_detections_key(self, adapter):
        raw = {
            "status": "completed",
            "detections": [
                {
                    "track_id": "bmat-003",
                    "confidence": 0.81,
                    "detection_type": "ugc",
                }
            ],
        }
        results = adapter.normalize_provider_response(raw)
        assert len(results) == 1
        assert results[0].match_type == MatchType.UGC

    def test_confidence_capped_at_1(self, adapter):
        raw = {
            "status": "success",
            "matches": [{"track_id": "x", "confidence": 150.0}],
        }
        results = adapter.normalize_provider_response(raw)
        assert results[0].confidence_score == pytest.approx(1.0)

    def test_unknown_detection_type_maps_to_unknown(self, adapter):
        raw = {
            "status": "success",
            "matches": [{"track_id": "z", "confidence": 0.6, "detection_type": "zap"}],
        }
        results = adapter.normalize_provider_response(raw)
        assert results[0].match_type == MatchType.UNKNOWN

    def test_empty_status_treated_as_success(self, adapter):
        raw = {
            "matches": [{"track_id": "y", "confidence": 0.7}],
        }
        results = adapter.normalize_provider_response(raw)
        assert len(results) == 1

    def test_social_detection_type_maps_to_ugc(self, adapter):
        raw = {
            "status": "success",
            "matches": [{"confidence": 0.6, "detection_type": "social"}],
        }
        results = adapter.normalize_provider_response(raw)
        assert results[0].match_type == MatchType.UGC


# ---------------------------------------------------------------------------
# match_audio
# ---------------------------------------------------------------------------


class TestBMATMatchAudio:
    @pytest.mark.asyncio
    async def test_match_audio_returns_normalized_results(self, adapter):
        raw_response = {
            "status": "success",
            "matches": [
                {
                    "track_id": "bmat-live-001",
                    "isrc": "USAT98765432",
                    "title": "Live Song",
                    "artist": "Live Artist",
                    "confidence": 0.88,
                    "detection_type": "streaming",
                    "territory": "DE",
                }
            ],
        }
        mock_response = MagicMock()
        mock_response.json.return_value = raw_response
        mock_response.raise_for_status = MagicMock()

        with (
            patch.object(adapter, "_client_") as mock_client_fn,
            patch.object(adapter._cb, "is_open", return_value=False),
            patch.object(adapter._cb, "record_success"),
        ):
            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client
            with patch.object(adapter._limiter, "acquire", AsyncMock()):
                results = await adapter.match_audio(b"audio-data")

        assert len(results) == 1
        assert results[0].isrc == "USAT98765432"
        assert results[0].match_type == MatchType.STREAM

    @pytest.mark.asyncio
    async def test_match_audio_circuit_open_raises(self, adapter):
        from XR7.fingerprinting._resilience import ProviderCircuitOpenError

        with patch.object(adapter._cb, "is_open", return_value=True):
            with pytest.raises(ProviderCircuitOpenError):
                await adapter.match_audio(b"audio-data")


# ---------------------------------------------------------------------------
# submit_reference_file
# ---------------------------------------------------------------------------


class TestBMATSubmitReference:
    @pytest.mark.asyncio
    async def test_submit_reference_returns_track_id(self, adapter):
        mock_response = MagicMock()
        mock_response.json.return_value = {"track_id": "ref-bmat-999"}
        mock_response.raise_for_status = MagicMock()

        with (
            patch.object(adapter, "_client_") as mock_client_fn,
            patch.object(adapter._cb, "is_open", return_value=False),
            patch.object(adapter._cb, "record_success"),
        ):
            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client
            with patch.object(adapter._limiter, "acquire", AsyncMock()):
                ref_id = await adapter.submit_reference_file(b"audio", isrc="USAT00001111")

        assert ref_id == "ref-bmat-999"


# ---------------------------------------------------------------------------
# detect_usage
# ---------------------------------------------------------------------------


class TestBMATDetectUsage:
    @pytest.mark.asyncio
    async def test_detect_usage_returns_events(self, adapter):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "events": [
                {"type": "radio", "confidence": 0.79, "track_id": "bmat-ev-001"},
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with (
            patch.object(adapter, "_client_") as mock_client_fn,
            patch.object(adapter._cb, "is_open", return_value=False),
            patch.object(adapter._cb, "record_success"),
        ):
            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client
            with patch.object(adapter._limiter, "acquire", AsyncMock()):
                results = await adapter.detect_usage("bmat-ref-123")

        assert len(results) == 1
        assert results[0].match_type == MatchType.RADIO


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


class TestBMATHealthCheck:
    @pytest.mark.asyncio
    async def test_healthy_on_200(self, adapter):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(adapter, "_client_") as mock_client_fn:
            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client

            status = await adapter.get_provider_health()

        assert status.provider == "bmat"
        assert status.status == ProviderStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_unhealthy_on_exception(self, adapter):
        import httpx

        with patch.object(adapter, "_client_") as mock_client_fn:
            mock_client = MagicMock()
            mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
            mock_client_fn.return_value = mock_client

            status = await adapter.get_provider_health()

        assert status.status == ProviderStatus.DOWN
        assert status.error_message is not None
