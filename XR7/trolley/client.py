from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
import time
from dataclasses import dataclass
from typing import Any

import requests


class TrolleyException(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


_CB_LOCK = threading.Lock()
_CB_STATE: dict[str, dict[str, float | int | None]] = {}


def _reset_trolley_circuit_breaker_state() -> None:
    """Testing helper: clear in-memory circuit breaker state."""
    with _CB_LOCK:
        _CB_STATE.clear()


@dataclass
class TrolleyClient:
    access_key: str
    secret_key: str
    base_url: str = "https://api.trolley.com"
    circuit_breaker_threshold: int = 5
    circuit_breaker_recovery_seconds: int = 60

    @classmethod
    def from_env(cls) -> "TrolleyClient":
        access_key = os.environ.get("TROLLEY_ACCESS_KEY", "").strip()
        secret_key = os.environ.get("TROLLEY_SECRET_KEY", "").strip()
        if not access_key or not secret_key:
            raise TrolleyException(
                "MISSING_CREDENTIALS", "TROLLEY_ACCESS_KEY and TROLLEY_SECRET_KEY must be set"
            )
        return cls(access_key=access_key, secret_key=secret_key)

    def _headers(self, method: str, path: str, body: str = "") -> dict[str, str]:
        ts = str(int(time.time()))
        canonical = f"{method.upper()}\n{path}\n{ts}\n{body}"
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            canonical.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return {
            "Content-Type": "application/json",
            "X-Access-Key": self.access_key,
            "X-Timestamp": ts,
            "X-Signature": signature,
        }

    def _cb_key(self) -> str:
        return self.base_url.rstrip("/")

    def _get_cb_state(self) -> dict[str, float | int | None]:
        key = self._cb_key()
        with _CB_LOCK:
            return _CB_STATE.setdefault(
                key,
                {
                    "consecutive_failures": 0,
                    "opened_at": None,
                },
            )

    def _fail_fast_if_open(self) -> None:
        state = self._get_cb_state()
        opened_at = state.get("opened_at")
        if opened_at is None:
            return

        now = time.time()
        elapsed = now - float(opened_at)
        if elapsed < self.circuit_breaker_recovery_seconds:
            retry_in = int(self.circuit_breaker_recovery_seconds - elapsed)
            raise TrolleyException(
                "CIRCUIT_OPEN",
                (
                    "Trolley circuit breaker is OPEN after repeated upstream failures. "
                    f"Failing fast; retry in ~{retry_in}s."
                ),
            )

    def _record_success(self) -> None:
        state = self._get_cb_state()
        with _CB_LOCK:
            state["consecutive_failures"] = 0
            state["opened_at"] = None

    def _record_failure(self) -> None:
        state = self._get_cb_state()
        with _CB_LOCK:
            failures = int(state.get("consecutive_failures") or 0) + 1
            state["consecutive_failures"] = failures
            if failures >= self.circuit_breaker_threshold:
                state["opened_at"] = time.time()

    def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        self._fail_fast_if_open()

        body = json.dumps(payload or {}, separators=(",", ":")) if payload is not None else ""
        headers = self._headers(method, path, body)
        try:
            response = requests.request(
                method=method.upper(),
                url=f"{self.base_url}{path}",
                headers=headers,
                data=body if payload is not None else None,
                timeout=20,
            )
        except requests.RequestException as exc:
            self._record_failure()
            raise TrolleyException("REQUEST_ERROR", f"Trolley request failed: {exc}") from exc

        if response.status_code >= 400:
            try:
                err = response.json()
            except Exception:  # noqa: BLE001
                err = {"message": response.text}

            if response.status_code >= 500:
                self._record_failure()
            raise TrolleyException(str(response.status_code), f"Trolley API error: {err}")

        self._record_success()
        if not response.text:
            return {}
        return response.json()

    def create_recipient(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/v1/recipients", payload)

    def get_recipient(self, recipient_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/recipients/{recipient_id}")

    def get_recipient_widget_url(self, recipient_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/recipients/{recipient_id}/widget-url")

    def get_payments_by_external_id(self, external_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/payments?externalId={external_id}")

    def create_payment(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/v1/payments", payload)

    def get_payment(self, payment_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/payments/{payment_id}")


def verify_trolley_signature(body: bytes, signature: str | None, secret_key: str) -> bool:
    if not signature:
        return False
    expected = hmac.new(secret_key.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
