from __future__ import annotations

from fastapi.testclient import TestClient

from XR7.api.app import app

client = TestClient(app)


def _bearer_scheme_names(spec: dict) -> set[str]:
    schemes = (spec.get("components") or {}).get("securitySchemes") or {}
    names: set[str] = set()
    for name, scheme in schemes.items():
        if (scheme or {}).get("type") == "http" and str((scheme or {}).get("scheme") or "").lower() == "bearer":
            names.add(name)
    return names


def _operation(spec: dict, path: str, method: str) -> dict:
    op = ((spec.get("paths") or {}).get(path) or {}).get(method)
    assert op is not None, f"missing operation {method.upper()} {path}"
    return op


def test_soft_guarded_endpoints_advertise_bearer_security_in_openapi():
    spec = client.get("/openapi.json").json()
    bearer_names = _bearer_scheme_names(spec)
    assert bearer_names, "expected at least one bearer security scheme in OpenAPI components"

    soft_guarded = [
        ("/artists/{artist_id}/earnings", "get"),
        ("/artists/{artist_id}/earnings/history", "get"),
        ("/artists/{artist_id}/anomalies", "get"),
        ("/artists/{artist_id}/claims", "get"),
    ]

    for path, method in soft_guarded:
        op = _operation(spec, path, method)
        sec = op.get("security") or []
        assert sec, f"expected security requirement on {method.upper()} {path}"
        has_bearer_req = any(any(name in req for name in bearer_names) for req in sec)
        assert has_bearer_req, f"expected bearer security requirement on {method.upper()} {path}"
