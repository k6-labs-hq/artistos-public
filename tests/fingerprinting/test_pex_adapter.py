"""Unit tests for the Pex provider adapter.

Covers:
    - provider_name identity
    - normalize_provider_response variations
    - match_audio with direct API-key auth
    - OAuth2 token refresh flow
    - submit_reference_file (2-step: POST /assets + PUT /assets/{id}/audio)
    - detect_usage via /assets/{id}/occurrences
    - health check (healthy + down)
    - circuit-breaker open guard
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from XR7.fingerprinting.adapters.pex import PexAdapter
from XR7.fingerprinting.config import PexConfig
from XR7.fingerprinting.schema import MatchType, ProviderStatus


@pytest.fixture
def pex_config_direct():
    """Config using direct API key (no OAuth2)."""
    return PexConfig(
        enabled=True,
        api_key="pex-direct-key",
        client_secret="",
        endpoint="https://api.pex.com/v1",
        timeout_seconds=10.0,
        max_retries=1,
        rate_limit_per_minute=60,
        priority=6,
    )


@pytest.fixture
def pex_config_oauth():
    """Config using OAuth2 client_credentials flow."""
    return PexConfig(
        enabled=True,
        api_key="pex-client-id",
        client_secret="pex-client-secret",
        endpoint="https://api.pex.com/v1",
        timeout_seconds=10.0,
        max_retries=1,
        rate_limit_per_minute=60,
        priority=6,
    )


@pytest.fixture
def adapter_direct(pex_config_direct):
    return PexAdapter(config=pex_config_direct)


@pytest.fixture
def adapter_oauth(pex_config_oauth):
    return PexAdapter(config=pex_config_oauth)


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


class TestPexAdapterIdentity:
    def test_provider_name(self, adapter_direct):
        assert adapter_direct.provider_name == "pex"


# ---------------------------------------------------------------------------
# Bearer token resolution
# ---------------------------------------------------------------------------


class TestPexBearerToken:
    @pytest.mark.asyncio
    async def test_direct_key_returns_api_key(self, adapter_direct):
        token = await adapter_direct._bearer_token()
        assert token == "pex-direct-key"

    @pytest.mark.asyncio
    async def test_oauth_mode_fetches_token(self, adapter_oauth):
        token_response = MagicMock()
        token_response.json.return_value = {"access_token": "oauth-token-123", "expires_in": 3600}
        token_response.raise_for_status = MagicMock()

        with patch.object(adapter_oauth, "_http_client") as mock_fn:
            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=token_response)
            mock_fn.return_value = mock_client

            token = await adapter_oauth._bearer_token()

        assert token == "oauth-token-123"

    @pytest.mark.asyncio
    async def test_oauth_mode_caches_token(self, adapter_oauth):
        """Second call must NOT make another network request."""
        token_response = MagicMock()
        token_response.json.return_value = {"access_token": "cached-token", "expires_in": 3600}
        token_response.raise_for_status = MagicMock()

        with patch.object(adapter_oauth, "_http_client") as mock_fn:
            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=token_response)
            mock_fn.return_value = mock_client

            t1 = await adapter_oauth._bearer_token()
            t2 = await adapter_oauth._bearer_token()

        # Should only have been called once
        assert mock_client.post.call_count == 1
        assert t1 == t2 == "cached-token"


# ---------------------------------------------------------------------------
# normalize_provider_response
# ---------------------------------------------------------------------------


class TestPexNormalizeResponse:
    def test_empty_returns_empty(self, adapter_direct):
        assert adapter_direct.normalize_provider_response({}) == []

    def test_error_status_returns_empty(self, adapter_direct):
        assert adapter_direct.normalize_provider_response({"status": "error"}) == []

    def test_success_with_matches_key(self, adapter_direct):
        raw = {
            "status": "success",
            "matches": [
                {
                    "asset_id": "pex-001",
                    "isrc": "USAT12345678",
                    "title": "Pex Track",
                    "artist": "Pex Artist",
                    "confidence": 0.94,
                    "match_type": "broadcast",
                    "territory": "US",
                    "platform": "youtube",
                    "duration_ms": 185000,
                }
            ],
        }
        results = adapter_direct.normalize_provider_response(raw)
        assert len(results) == 1
        r = results[0]
        assert r.provider == "pex"
        assert r.isrc == "USAT12345678"
        assert r.track_id == "pex-001"
        assert r.title == "Pex Track"
        assert r.artist_name == "Pex Artist"
        assert r.confidence_score == pytest.approx(0.94)
        assert r.match_type == MatchType.BROADCAST
        assert r.territory == "US"
        assert r.platform == "youtube"
        assert r.duration_seconds == pytest.approx(185.0)

    def test_matches_online_type_to_stream(self, adapter_direct):
        raw = {
            "status": "success",
            "matches": [{"asset_id": "x", "confidence": 0.6, "match_type": "online"}],
        }
        results = adapter_direct.normalize_provider_response(raw)
        assert results[0].match_type == MatchType.STREAM

    def test_matches_user_generated_to_ugc(self, adapter_direct):
        raw = {
            "status": "success",
            "matches": [{"asset_id": "y", "confidence": 0.7, "match_type": "user_generated"}],
        }
        results = adapter_direct.normalize_provider_response(raw)
        assert results[0].match_type == MatchType.UGC

    def test_confidence_capped_at_1(self, adapter_direct):
        raw = {
            "status": "success",
            "matches": [{"asset_id": "z", "confidence": 200.0}],
        }
        results = adapter_direct.normalize_provider_response(raw)
        assert results[0].confidence_score == pytest.approx(1.0)

    def test_occurrences_key_also_parsed(self, adapter_direct):
        raw = {
            "status": "success",
            "occurrences": [{"asset_id": "occ-001", "confidence": 0.8, "match_type": "radio"}],
        }
        results = adapter_direct.normalize_provider_response(raw)
        assert len(results) == 1
        assert results[0].match_type == MatchType.RADIO


# ---------------------------------------------------------------------------
# match_audio
# ---------------------------------------------------------------------------


class TestPexMatchAudio:
    @pytest.mark.asyncio
    async def test_match_audio_posts_to_identify(self, adapter_direct):
        raw_response = {
            "status": "success",
            "matches": [
                {
                    "asset_id": "pex-live-001",
                    "isrc": "USAT55556666",
                    "title": "Streaming Hit",
                    "artist": "Stream Star",
                    "confidence": 0.89,
                    "match_type": "streaming",
                }
            ],
        }
        mock_response = MagicMock()
        mock_response.json.return_value = raw_response
        mock_response.raise_for_status = MagicMock()

        with (
            patch.object(adapter_direct, "_http_client") as mock_client_fn,
            patch.object(adapter_direct._cb, "is_open", return_value=False),
            patch.object(adapter_direct._cb, "record_success"),
        ):
            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client
            with patch.object(adapter_direct._limiter, "acquire", AsyncMock()):
                results = await adapter_direct.match_audio(b"audio-bytes")

        assert len(results) == 1
        assert results[0].isrc == "USAT55556666"
        assert results[0].match_type == MatchType.STREAM

    @pytest.mark.asyncio
    async def test_circuit_open_raises(self, adapter_direct):
        from XR7.fingerprinting._resilience import ProviderCircuitOpenError

        with patch.object(adapter_direct._cb, "is_open", return_value=True):
            with pytest.raises(ProviderCircuitOpenError):
                await adapter_direct.match_audio(b"audio")


# ---------------------------------------------------------------------------
# submit_reference_file (2-step)
# ---------------------------------------------------------------------------


class TestPexSubmitReference:
    @pytest.mark.asyncio
    async def test_two_step_registration_returns_asset_id(self, adapter_direct):
        create_response = MagicMock()
        create_response.json.return_value = {"id": "pex-asset-777", "status": "created"}
        create_response.raise_for_status = MagicMock()

        upload_response = MagicMock()
        upload_response.raise_for_status = MagicMock()

        with (
            patch.object(adapter_direct, "_http_client") as mock_client_fn,
            patch.object(adapter_direct._cb, "is_open", return_value=False),
            patch.object(adapter_direct._cb, "record_success"),
            patch.object(adapter_direct, "_bearer_token", AsyncMock(return_value="tok")),
        ):
            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=create_response)
            mock_client.put = AsyncMock(return_value=upload_response)
            mock_client_fn.return_value = mock_client
            with patch.object(adapter_direct._limiter, "acquire", AsyncMock()):
                ref_id = await adapter_direct.submit_reference_file(b"audio", isrc="USAT00009999")

        assert ref_id == "pex-asset-777"


# ---------------------------------------------------------------------------
# detect_usage
# ---------------------------------------------------------------------------


class TestPexDetectUsage:
    @pytest.mark.asyncio
    async def test_returns_occurrences(self, adapter_direct):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "occurrences": [
                {
                    "asset_id": "pex-asset-777",
                    "match_type": "social",
                    "confidence": 0.75,
                    "platform": "instagram",
                    "territory": "US",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with (
            patch.object(adapter_direct, "_http_client") as mock_client_fn,
            patch.object(adapter_direct._cb, "is_open", return_value=False),
            patch.object(adapter_direct._cb, "record_success"),
            patch.object(adapter_direct, "_bearer_token", AsyncMock(return_value="tok")),
        ):
            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client
            with patch.object(adapter_direct._limiter, "acquire", AsyncMock()):
                results = await adapter_direct.detect_usage("pex-asset-777")

        assert len(results) == 1
        assert results[0].match_type == MatchType.UGC
        assert results[0].platform == "instagram"


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


class TestPexHealthCheck:
    @pytest.mark.asyncio
    async def test_healthy_on_200(self, adapter_direct):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(adapter_direct, "_http_client") as mock_client_fn:
            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_fn.return_value = mock_client

            status = await adapter_direct.get_provider_health()

        assert status.provider == "pex"
        assert status.status == ProviderStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_down_on_network_error(self, adapter_direct):
        import httpx

        with patch.object(adapter_direct, "_http_client") as mock_client_fn:
            mock_client = MagicMock()
            mock_client.get = AsyncMock(side_effect=httpx.ConnectError("timeout"))
            mock_client_fn.return_value = mock_client

            status = await adapter_direct.get_provider_health()

        assert status.status == ProviderStatus.DOWN
        assert status.error_message is not None

    @pytest.mark.asyncio
    async def test_aclose_clears_token(self, adapter_oauth):
        """aclose() should clear the cached OAuth2 access token."""
        adapter_oauth._access_token = "stale-token"
        adapter_oauth._token_expiry = 9999999999.0

        mock_client = AsyncMock()
        adapter_oauth._client = mock_client

        await adapter_oauth.aclose()

        assert adapter_oauth._access_token is None
        mock_client.aclose.assert_called_once()
