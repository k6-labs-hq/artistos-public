"""Integration/unit tests for the fingerprinting FastAPI router.

Uses TestClient with a mock FingerprintingOrchestrator so no real
provider HTTP calls are made.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.fingerprinting.schema import (
    AnomalyType,
    MatchType,
    NormalizedMatchResult,
    ProviderHealthStatus,
    ProviderStatus,
    RoyaltyStatus,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

client = TestClient(app)

_ARTIST_ID = f"artist-fp-{uuid.uuid4()}"
_JOB_ID = str(uuid.uuid4())

_SAMPLE_MATCH = NormalizedMatchResult(
    track_id="fp-001",
    isrc="USAT12345678",
    iswc="T-123456789-0",
    confidence_score=0.92,
    match_type=MatchType.STREAM,
    platform="spotify",
    territory="US",
    timestamp=datetime.now(timezone.utc),
    provider="acrcloud",
    royalty_status=RoyaltyStatus.UNKNOWN,
    anomaly_type=AnomalyType.NONE,
    title="Test Track",
    artist_name="Test Artist",
)


def _fake_audio() -> bytes:
    return b"RIFF" + b"\x00" * 44  # minimal WAV-like bytes


# ---------------------------------------------------------------------------
# POST /artists/{artist_id}/fingerprints/identify
# ---------------------------------------------------------------------------


class TestIdentifySync:
    def test_returns_200_with_matches(self):
        with patch("XR7.api.routers.fingerprinting.FingerprintingOrchestrator") as MockOrch:
            instance = MagicMock()
            instance.identify = AsyncMock(return_value=[_SAMPLE_MATCH])
            MockOrch.return_value = instance

            response = client.post(
                f"/artists/{_ARTIST_ID}/fingerprints/identify",
                files={"audio": ("test.wav", _fake_audio(), "audio/wav")},
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["isrc"] == "USAT12345678"
        assert data[0]["provider"] == "acrcloud"

    def test_empty_audio_returns_400(self):
        response = client.post(
            f"/artists/{_ARTIST_ID}/fingerprints/identify",
            files={"audio": ("test.wav", b"", "audio/wav")},
        )
        assert response.status_code == 400

    def test_oversized_audio_returns_413(self):
        big_audio = b"X" * (11 * 1024 * 1024)
        response = client.post(
            f"/artists/{_ARTIST_ID}/fingerprints/identify",
            files={"audio": ("test.wav", big_audio, "audio/wav")},
        )
        assert response.status_code == 413

    def test_provider_error_returns_502(self):
        with patch("XR7.api.routers.fingerprinting.FingerprintingOrchestrator") as MockOrch:
            instance = MagicMock()
            instance.identify = AsyncMock(side_effect=RuntimeError("provider down"))
            MockOrch.return_value = instance

            response = client.post(
                f"/artists/{_ARTIST_ID}/fingerprints/identify",
                files={"audio": ("test.wav", _fake_audio(), "audio/wav")},
            )

        assert response.status_code == 502

    def test_providers_form_field_parsed(self):
        with patch("XR7.api.routers.fingerprinting.FingerprintingOrchestrator") as MockOrch:
            instance = MagicMock()
            instance.identify = AsyncMock(return_value=[_SAMPLE_MATCH])
            MockOrch.return_value = instance

            response = client.post(
                f"/artists/{_ARTIST_ID}/fingerprints/identify",
                files={"audio": ("test.wav", _fake_audio(), "audio/wav")},
                data={"providers": "acrcloud,bmat", "isrc": "USAT12345678"},
            )

        assert response.status_code == 200
        call_kwargs = instance.identify.call_args
        req = call_kwargs.kwargs["request"]
        assert req.providers == ["acrcloud", "bmat"]
        assert req.isrc == "USAT12345678"


# ---------------------------------------------------------------------------
# POST /artists/{artist_id}/fingerprints/identify/async
# ---------------------------------------------------------------------------


class TestIdentifyAsync:
    def test_returns_202_with_job_id(self):
        mock_task = MagicMock()
        mock_task.id = _JOB_ID

        with patch("XR7.fingerprinting.workers.realtime_fingerprint_audio") as mock_worker:
            mock_worker.delay = MagicMock(return_value=mock_task)
            response = client.post(
                f"/artists/{_ARTIST_ID}/fingerprints/identify/async",
                data={
                    "audio_url": "https://example.com/track.wav",
                    "isrc": "USAT12345678",
                },
            )

        assert response.status_code == 202
        data = response.json()
        assert data["job_id"] == _JOB_ID
        assert data["status"] == "queued"

    def test_missing_audio_source_returns_400(self):
        response = client.post(
            f"/artists/{_ARTIST_ID}/fingerprints/identify/async",
            data={},
        )
        assert response.status_code == 400

    def test_s3_key_accepted(self):
        mock_task = MagicMock()
        mock_task.id = "s3-job-abc"

        with patch("XR7.fingerprinting.workers.realtime_fingerprint_audio") as mock_worker:
            mock_worker.delay = MagicMock(return_value=mock_task)
            response = client.post(
                f"/artists/{_ARTIST_ID}/fingerprints/identify/async",
                data={"audio_s3_key": "bucket/tracks/song.wav"},
            )

        assert response.status_code == 202
        assert response.json()["job_id"] == "s3-job-abc"


# ---------------------------------------------------------------------------
# POST /artists/{artist_id}/fingerprints/references
# ---------------------------------------------------------------------------


class TestRegisterReference:
    def test_registers_and_returns_ref_id(self):
        mock_adapter = MagicMock()
        mock_adapter.provider_name = "acrcloud"
        mock_adapter.submit_reference_file = AsyncMock(return_value="ref-acrcloud-123")

        with patch("XR7.api.routers.fingerprinting.FingerprintingOrchestrator") as MockOrch:
            instance = MagicMock()
            instance._registry = {"acrcloud": mock_adapter}
            MockOrch.return_value = instance

            response = client.post(
                f"/artists/{_ARTIST_ID}/fingerprints/references",
                files={"audio": ("ref.wav", _fake_audio(), "audio/wav")},
                data={"isrc": "USAT12345678", "title": "My Song", "artist_name": "Artist"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["reference_id"] == "ref-acrcloud-123"
        assert data["provider"] == "acrcloud"
        assert data["isrc"] == "USAT12345678"

    def test_empty_audio_returns_400(self):
        response = client.post(
            f"/artists/{_ARTIST_ID}/fingerprints/references",
            files={"audio": ("ref.wav", b"", "audio/wav")},
        )
        assert response.status_code == 400

    def test_unknown_provider_returns_400(self):
        with patch("XR7.api.routers.fingerprinting.FingerprintingOrchestrator") as MockOrch:
            instance = MagicMock()
            instance._registry = {"acrcloud": MagicMock()}
            MockOrch.return_value = instance

            response = client.post(
                f"/artists/{_ARTIST_ID}/fingerprints/references",
                files={"audio": ("ref.wav", _fake_audio(), "audio/wav")},
                data={"provider": "nonexistent_provider"},
            )

        assert response.status_code == 400


# ---------------------------------------------------------------------------
# GET /artists/{artist_id}/fingerprints/jobs
# ---------------------------------------------------------------------------


class TestListJobs:
    def test_returns_paginated_response(self):
        from tests.conftest import TestSession

        db = TestSession()
        from XR7.models.artist import Artist
        from XR7.models.fingerprint_job import (
            FingerprintJob,
            FingerprintJobMode,
            FingerprintJobStatus,
        )

        artist_id = f"fp-list-{uuid.uuid4()}"
        artist = Artist(id=artist_id, name="FP List Artist")
        db.add(artist)

        job = FingerprintJob(
            id=str(uuid.uuid4()),
            artist_id=artist_id,
            status=FingerprintJobStatus.COMPLETED,
            mode=FingerprintJobMode.REALTIME,
            provider="acrcloud",
            isrc="USAT12345678",
        )
        db.add(job)
        db.commit()
        db.close()

        response = client.get(f"/artists/{artist_id}/fingerprints/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_invalid_status_returns_400(self):
        response = client.get(f"/artists/{_ARTIST_ID}/fingerprints/jobs?status=totally_invalid")
        assert response.status_code == 400

    def test_page_and_page_size_accepted(self):
        response = client.get(f"/artists/{_ARTIST_ID}/fingerprints/jobs?page=1&page_size=5")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /artists/{artist_id}/fingerprints/jobs/{job_id}
# ---------------------------------------------------------------------------


class TestGetJob:
    def test_returns_404_when_not_found(self):
        response = client.get(f"/artists/{_ARTIST_ID}/fingerprints/jobs/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_returns_job_with_matches(self):
        from tests.conftest import TestSession

        db = TestSession()
        from XR7.models.artist import Artist
        from XR7.models.fingerprint_job import (
            FingerprintJob,
            FingerprintJobMode,
            FingerprintJobStatus,
        )
        from XR7.models.fingerprint_match import FingerprintMatch

        artist_id = f"fp-detail-{uuid.uuid4()}"
        artist = Artist(id=artist_id, name="FP Detail Artist")
        db.add(artist)

        job_id = str(uuid.uuid4())
        job = FingerprintJob(
            id=job_id,
            artist_id=artist_id,
            status=FingerprintJobStatus.COMPLETED,
            mode=FingerprintJobMode.REALTIME,
        )
        db.add(job)

        match = FingerprintMatch(
            id=str(uuid.uuid4()),
            job_id=job_id,
            provider="acrcloud",
            isrc="USAT12345678",
            confidence_score=0.93,
            match_type="stream",
        )
        db.add(match)
        db.commit()
        db.close()

        response = client.get(f"/artists/{artist_id}/fingerprints/jobs/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert isinstance(data["matches"], list)
        assert len(data["matches"]) == 1
        assert data["matches"][0]["isrc"] == "USAT12345678"


# ---------------------------------------------------------------------------
# POST /artists/{artist_id}/fingerprints/reconcile
# ---------------------------------------------------------------------------


class TestReconcile:
    def test_queues_task_and_returns_202(self):
        mock_task = MagicMock()
        mock_task.id = "reconcile-task-001"

        with patch("XR7.fingerprinting.workers.matching_engine_reconcile") as mock_worker:
            mock_worker.delay = MagicMock(return_value=mock_task)
            response = client.post(
                f"/artists/{_ARTIST_ID}/fingerprints/reconcile",
                json={},
            )

        assert response.status_code == 202
        data = response.json()
        assert data["task_id"] == "reconcile-task-001"
        assert data["status"] == "queued"

    def test_accepts_providers_filter(self):
        mock_task = MagicMock()
        mock_task.id = "reconcile-task-002"

        with patch("XR7.fingerprinting.workers.matching_engine_reconcile") as mock_worker:
            mock_worker.delay = MagicMock(return_value=mock_task)
            response = client.post(
                f"/artists/{_ARTIST_ID}/fingerprints/reconcile",
                json={"providers": ["acrcloud", "bmat"]},
            )

        assert response.status_code == 202
        mock_worker.delay.assert_called_once_with(
            artist_id=_ARTIST_ID, providers=["acrcloud", "bmat"]
        )


# ---------------------------------------------------------------------------
# GET /fingerprints/providers/health
# ---------------------------------------------------------------------------


class TestProviderHealth:
    def test_returns_list_of_health_statuses(self):
        mock_status = ProviderHealthStatus(
            provider="acrcloud",
            status=ProviderStatus.HEALTHY,
            latency_ms=42.0,
            checked_at=datetime.now(timezone.utc),
        )

        with patch("XR7.api.routers.fingerprinting.FingerprintingOrchestrator") as MockOrch:
            instance = MagicMock()
            instance.health_check_all = AsyncMock(return_value=[mock_status])
            MockOrch.return_value = instance

            response = client.get("/fingerprints/providers/health")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["provider"] == "acrcloud"
        assert data[0]["status"] == "healthy"


# ---------------------------------------------------------------------------
# GET /fingerprints/providers/circuit-breakers
# ---------------------------------------------------------------------------


class TestCircuitBreakers:
    def test_returns_cb_status_list(self):
        mock_statuses = {
            "acrcloud": {"state": "closed", "failure_count": 0, "last_failure_time": None},
            "bmat": {"state": "open", "failure_count": 5, "last_failure_time": 1234567890.0},
        }

        with patch("XR7.api.routers.fingerprinting.FingerprintingOrchestrator") as MockOrch:
            instance = MagicMock()
            instance.circuit_breaker_status = MagicMock(return_value=mock_statuses)
            MockOrch.return_value = instance

            response = client.get("/fingerprints/providers/circuit-breakers")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        providers = {item["provider"] for item in data}
        assert "acrcloud" in providers
        assert "bmat" in providers
        bmat = next(i for i in data if i["provider"] == "bmat")
        assert bmat["state"] == "open"
        assert bmat["failure_count"] == 5
