from __future__ import annotations

from types import SimpleNamespace

from xr7_sdk.api.artists_api import ArtistsApi
from xr7_sdk.api.claims_api import ClaimsApi
from xr7_sdk.api.dashboard_api import DashboardApi
from xr7_sdk.api.default_api import DefaultApi
from xr7_sdk.api.ingestion_api import IngestionApi


class _DummyResponse:
    def __init__(self) -> None:
        self.response = {"ok": True}

    def read(self) -> None:
        return None


class _StubApiClient:
    def __init__(self) -> None:
        self.last_call: tuple | None = None

    def call_api(self, *args, **kwargs):
        self.last_call = (args, kwargs)
        return _DummyResponse()

    def response_deserialize(self, **kwargs):
        return SimpleNamespace(data={"ok": True})

    def select_header_accept(self, values):
        return values[0] if values else None

    def select_header_content_type(self, values):
        return values[0] if values else None

    def param_serialize(
        self,
        method,
        resource_path,
        path_params=None,
        query_params=None,
        header_params=None,
        body=None,
        post_params=None,
        files=None,
        auth_settings=None,
        collection_formats=None,
        _host=None,
        _request_auth=None,
    ):
        url = f"http://localhost:8000{resource_path}"
        if path_params:
            for key, value in path_params.items():
                url = url.replace("{" + str(key) + "}", str(value))
        return method, url, header_params or {}, body, post_params or []


def test_default_api_health_and_readiness_smoke() -> None:
    api = DefaultApi(api_client=_StubApiClient())
    assert api.health_health_get() == {"ok": True}
    assert api.readiness_health_readiness_get() == {"ok": True}


def test_artists_api_summary_and_create_smoke() -> None:
    client = _StubApiClient()
    api = ArtistsApi(api_client=client)

    result = api.artist_summary_artists_artist_id_summary_get("artist-1")
    assert result == {"ok": True}
    assert client.last_call is not None
    assert client.last_call[0][0] == "GET"
    assert "/artists/artist-1/summary" in client.last_call[0][1]

    result = api.create_artist_artists_post({"name": "Smoke Artist", "email": "smoke@example.com"})
    assert result == {"ok": True}
    assert client.last_call is not None
    assert client.last_call[0][0] == "POST"
    assert "/artists" in client.last_call[0][1]


def test_claims_api_core_methods_smoke() -> None:
    client = _StubApiClient()
    api = ClaimsApi(api_client=client)

    result = api.activate_negotiator_agent_claims_claim_id_activate_agent_post("claim-1")
    assert result == {"ok": True}
    assert client.last_call is not None
    assert client.last_call[0][0] == "POST"
    assert "/claims/claim-1/activate-agent" in client.last_call[0][1]

    result = api.create_claim_for_artist_artists_artist_id_claims_post(
        "artist-1",
        {"anomaly_id": "anomaly-1", "claim_type": "RECOVERY"},
    )
    assert result == {"ok": True}
    assert client.last_call is not None
    assert client.last_call[0][0] == "POST"
    assert "/artists/artist-1/claims" in client.last_call[0][1]


def test_ingestion_api_list_and_upload_smoke() -> None:
    client = _StubApiClient()
    api = IngestionApi(api_client=client)

    result = api.list_statements_artists_artist_id_statements_get("artist-1")
    assert result == {"ok": True}
    assert client.last_call is not None
    assert client.last_call[0][0] == "GET"
    assert "/artists/artist-1/statements" in client.last_call[0][1]

    result = api.upload_statement_artists_artist_id_statements_upload_post("artist-1", file="/tmp/statement.csv")
    assert result == {"ok": True}
    assert client.last_call is not None
    assert client.last_call[0][0] == "POST"
    assert "/artists/artist-1/statements/upload" in client.last_call[0][1]


def test_dashboard_api_benchmarks_smoke() -> None:
    client = _StubApiClient()
    api = DashboardApi(api_client=client)

    result = api.dashboard_benchmarks_artists_artist_id_benchmarks_get("artist-1")
    assert result == {"ok": True}
    assert client.last_call is not None
    assert client.last_call[0][0] == "GET"
    assert "/artists/artist-1/benchmarks" in client.last_call[0][1]
