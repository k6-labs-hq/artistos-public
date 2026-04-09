#!/usr/bin/env python3
"""
smoke_test.py
─────────────
Lightweight smoke test suite for post-deployment validation.

Verifies that the deployed XR7 API:
  1. Responds to the health endpoint
  2. Returns the expected OpenAPI schema root
  3. Correctly rejects unauthenticated requests with 401
  4. Returns 200 with a valid auth token on a read-only endpoint
  5. Confirms expected response shape for /artists list

Environment variables (required):
  SMOKE_TEST_BASE_URL     — e.g. https://staging.xr7.artistos.io
  SMOKE_TEST_API_KEY      — valid API key for the deployed environment

Exit code 0  = all checks passed.
Exit code 1  = one or more checks failed.

Run:  python scripts/smoke_test.py
"""

import os
import sys
from typing import Any

try:
    import httpx
except ImportError:
    print("httpx is required: pip install httpx")
    sys.exit(1)

BASE_URL = os.environ.get("SMOKE_TEST_BASE_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.environ.get("SMOKE_TEST_API_KEY", "")
TIMEOUT = 15.0

failures: list[str] = []
passes: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        passes.append(name)
        print(f"  PASS  {name}")
    else:
        failures.append(name)
        print(f"  FAIL  {name}" + (f" — {detail}" if detail else ""))


def get(path: str, headers: dict | None = None, expected_status: int = 200) -> tuple[int, Any]:
    try:
        r = httpx.get(f"{BASE_URL}{path}", headers=headers or {}, timeout=TIMEOUT)
        return r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text
    except Exception as e:
        return -1, str(e)


def main() -> int:
    if not BASE_URL:
        print("SMOKE_TEST_BASE_URL is not set.")
        return 1

    auth_headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

    print(f"\nSmoke test: {BASE_URL}\n")

    # Check 1: Health endpoint
    status, body = get("/healthz")
    check("healthz-responds", status == 200, f"HTTP {status}")

    # Check 2: OpenAPI schema accessible
    status, body = get("/openapi.json")
    check("openapi-accessible", status == 200, f"HTTP {status}")
    if isinstance(body, dict):
        check("openapi-has-paths", "paths" in body, "missing 'paths' key")
        check("openapi-version-31", body.get("openapi", "").startswith("3.1"), f"got {body.get('openapi')}")

    # Check 3: Unauthenticated request rejected
    status, body = get("/artists", headers={})
    check("unauth-returns-401", status == 401, f"got HTTP {status}")

    # Check 4: Authenticated request succeeds
    if API_KEY:
        status, body = get("/artists", headers=auth_headers)
        check("auth-artists-200", status == 200, f"HTTP {status}")
        if isinstance(body, (dict, list)):
            items = body if isinstance(body, list) else body.get("items", body.get("data", []))
            check("artists-returns-list", isinstance(items, list), f"got type {type(items).__name__}")
    else:
        print("  SKIP  auth checks (SMOKE_TEST_API_KEY not set)")

    # Summary
    print(f"\nResults: {len(passes)} passed, {len(failures)} failed\n")
    if failures:
        print(f"Failed checks: {', '.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
