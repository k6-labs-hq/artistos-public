from __future__ import annotations

import requests

from XR7.trolley.client import TrolleyClient, TrolleyException, _reset_trolley_circuit_breaker_state


class _FakeResponse:
    def __init__(self, status_code: int, body: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._body = body or {}
        self.text = text

    def json(self):
        return self._body


def test_trolley_circuit_breaker_opens_after_5_failures(monkeypatch):
    _reset_trolley_circuit_breaker_state()
    calls = {"count": 0}

    def _boom(*args, **kwargs):
        calls["count"] += 1
        raise requests.Timeout("simulated timeout")

    monkeypatch.setattr("XR7.trolley.client.requests.request", _boom)

    c = TrolleyClient(access_key="a", secret_key="b")

    for _ in range(5):
        try:
            c.create_payment({"externalId": "x"})
        except TrolleyException as exc:
            assert exc.code == "REQUEST_ERROR"

    # 6th call should fail fast before making an HTTP request.
    try:
        c.create_payment({"externalId": "x"})
        assert False, "Expected circuit breaker to fail fast"
    except TrolleyException as exc:
        assert exc.code == "CIRCUIT_OPEN"

    assert calls["count"] == 5


def test_trolley_circuit_breaker_recovers_after_60_seconds(monkeypatch):
    _reset_trolley_circuit_breaker_state()

    # Control clock deterministically.
    now = {"t": 1000.0}

    def _time():
        return now["t"]

    monkeypatch.setattr("XR7.trolley.client.time.time", _time)

    call_count = {"n": 0}

    def _request(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] <= 5:
            raise requests.ConnectionError("trolley down")
        return _FakeResponse(200, {"payment": {"id": "pay_1"}}, '{"payment":{"id":"pay_1"}}')

    monkeypatch.setattr("XR7.trolley.client.requests.request", _request)

    c = TrolleyClient(access_key="a", secret_key="b")

    for _ in range(5):
        try:
            c.create_payment({"externalId": "y"})
        except TrolleyException:
            pass

    # Circuit open inside 60s window.
    try:
        c.create_payment({"externalId": "y"})
        assert False, "Expected circuit to be open"
    except TrolleyException as exc:
        assert exc.code == "CIRCUIT_OPEN"

    # Advance beyond recovery window; next call should be attempted and succeed.
    now["t"] += 61
    response = c.create_payment({"externalId": "y"})
    assert response["payment"]["id"] == "pay_1"
    assert call_count["n"] == 6


def test_trolley_4xx_does_not_trip_circuit_breaker(monkeypatch):
    _reset_trolley_circuit_breaker_state()
    calls = {"count": 0}

    def _bad_request(*args, **kwargs):
        calls["count"] += 1
        return _FakeResponse(400, {"message": "invalid payload"}, '{"message":"invalid payload"}')

    monkeypatch.setattr("XR7.trolley.client.requests.request", _bad_request)

    c = TrolleyClient(access_key="a", secret_key="b")

    # Repeated 4xx should not open circuit (these are client-side errors).
    for _ in range(7):
        try:
            c.create_payment({"externalId": "z"})
            assert False, "Expected 400 error"
        except TrolleyException as exc:
            assert exc.code == "400"

    # All calls should still hit upstream, proving no circuit-open fail-fast.
    assert calls["count"] == 7
