from __future__ import annotations

from XR7.api.app import _security_gate_status


def test_security_gate_status_production_requires_rsa_and_webhook(monkeypatch):
    monkeypatch.setenv("XR7_EVIDENCE_SIGNING_MODE", "hmac")
    monkeypatch.delenv("XR7_EVIDENCE_PRIVATE_KEY_PEM", raising=False)
    monkeypatch.delenv("XR7_EVIDENCE_PUBLIC_KEY_PEM", raising=False)
    monkeypatch.delenv("TROLLEY_SECRET_KEY", raising=False)

    status = _security_gate_status("production")
    assert status["all_required_gates_passed"] is False
    assert status["evidence_signing_policy_ok"] is False
    assert status["trolley_webhook_policy_ok"] is False


def test_security_gate_status_production_passes_with_rsa_and_webhook(monkeypatch):
    monkeypatch.setenv("XR7_EVIDENCE_SIGNING_MODE", "rsa")
    monkeypatch.setenv("XR7_EVIDENCE_PRIVATE_KEY_PEM", "-----BEGIN PRIVATE KEY-----x")
    monkeypatch.setenv("XR7_EVIDENCE_PUBLIC_KEY_PEM", "-----BEGIN PUBLIC KEY-----x")
    monkeypatch.setenv("TROLLEY_SECRET_KEY", "secret")

    status = _security_gate_status("production")
    assert status["all_required_gates_passed"] is True
    assert status["evidence_signing_policy_ok"] is True
    assert status["trolley_webhook_policy_ok"] is True


def test_security_gate_status_dev_passes_with_hmac(monkeypatch):
    """Dev/staging environments must not require RSA — local dev would break."""
    monkeypatch.setenv("XR7_EVIDENCE_SIGNING_MODE", "hmac")
    monkeypatch.delenv("XR7_EVIDENCE_PRIVATE_KEY_PEM", raising=False)
    monkeypatch.delenv("XR7_EVIDENCE_PUBLIC_KEY_PEM", raising=False)
    monkeypatch.delenv("TROLLEY_SECRET_KEY", raising=False)

    status = _security_gate_status("development")
    assert status["all_required_gates_passed"] is True
    assert status["evidence_signing_policy_ok"] is True


def test_security_gate_status_trolley_gate_is_isolated(monkeypatch):
    """Trolley webhook gate fails independently from the signing-mode gate."""
    monkeypatch.setenv("XR7_EVIDENCE_SIGNING_MODE", "rsa")
    monkeypatch.setenv("XR7_EVIDENCE_PRIVATE_KEY_PEM", "-----BEGIN PRIVATE KEY-----x")
    monkeypatch.setenv("XR7_EVIDENCE_PUBLIC_KEY_PEM", "-----BEGIN PUBLIC KEY-----x")
    monkeypatch.delenv("TROLLEY_SECRET_KEY", raising=False)

    status = _security_gate_status("production")
    assert status["evidence_signing_policy_ok"] is True
    assert status["trolley_webhook_policy_ok"] is False
    assert status["all_required_gates_passed"] is False


def test_security_gate_signing_only_fails_without_trolley_key(monkeypatch):
    """Signing gate fails independently from the Trolley webhook gate."""
    monkeypatch.setenv("XR7_EVIDENCE_SIGNING_MODE", "hmac")
    monkeypatch.delenv("XR7_EVIDENCE_PRIVATE_KEY_PEM", raising=False)
    monkeypatch.delenv("XR7_EVIDENCE_PUBLIC_KEY_PEM", raising=False)
    monkeypatch.setenv("TROLLEY_SECRET_KEY", "wh_live_secret")

    status = _security_gate_status("production")
    assert status["trolley_webhook_policy_ok"] is True
    assert status["evidence_signing_policy_ok"] is False
    assert status["all_required_gates_passed"] is False


def test_signing_mode_env_var_drives_orchestrator(monkeypatch):
    """ClaimsOrchestrator._signing_mode() must read XR7_EVIDENCE_SIGNING_MODE."""
    from XR7.recovery.orchestrator import ClaimsOrchestrator

    monkeypatch.setenv("XR7_EVIDENCE_SIGNING_MODE", "rsa")
    assert ClaimsOrchestrator._signing_mode() == "rsa"

    monkeypatch.setenv("XR7_EVIDENCE_SIGNING_MODE", "hmac")
    assert ClaimsOrchestrator._signing_mode() == "hmac"


def test_readiness_endpoint_exposes_security_gates():
    """GET /health/readiness must return a security_gates block with required keys."""
    from fastapi.testclient import TestClient
    from XR7.api.app import app

    client = TestClient(app)
    resp = client.get("/health/readiness")
    assert resp.status_code == 200
    data = resp.json()
    assert "security_gates" in data
    gates = data["security_gates"]
    for key in (
        "environment",
        "evidence_signing_mode",
        "rsa_private_key_configured",
        "rsa_public_key_configured",
        "trolley_webhook_secret_configured",
        "evidence_signing_policy_ok",
        "trolley_webhook_policy_ok",
        "all_required_gates_passed",
    ):
        assert key in gates, f"Missing security_gates key: {key}"


def test_readiness_endpoint_reports_trolley_webhook_status():
    """Readiness webhooks section must expose trolley_webhook_secret_configured."""
    from fastapi.testclient import TestClient
    from XR7.api.app import app

    client = TestClient(app)
    resp = client.get("/health/readiness")
    assert resp.status_code == 200
    data = resp.json()
    assert "webhooks" in data
    assert "trolley_webhook_secret_configured" in data["webhooks"]
