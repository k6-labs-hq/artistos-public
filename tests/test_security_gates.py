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
