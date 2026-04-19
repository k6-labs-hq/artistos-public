"""
Domain exceptions for XR7 Engine.

Centralized exception hierarchy for domain-specific errors that require
special handling or audit logging (e.g., tenant isolation violations,
compliance violations, data integrity errors).

Closes: XR7-403
Domain: security
Scale-target: 10x tenant count with strict data plane isolation
Compliance: SOC 2 CC6.7 — Logical access (tenant isolation)
"""

from __future__ import annotations


class XR7Exception(Exception):
    """Base exception for all XR7-specific errors."""


class TenantIsolationViolation(XR7Exception):
    """Raised when an operation attempts to access data from another tenant.

    This is a critical security violation that indicates either:
    1. A malicious attempt to access cross-tenant data
    2. A code bug that bypassed tenant context setting
    3. An improperly scoped query

    All violations are logged for security audit.

    Attributes:
        current_tenant: The tenant ID from the current JWT/context
        target_tenant: The tenant ID that was attempted to be accessed
        operation: The type of operation (SELECT/INSERT/UPDATE/DELETE)
        model: The model class that was accessed
    """

    def __init__(
        self,
        current_tenant: str,
        target_tenant: str,
        operation: str,
        model: str | None = None,
        actor_sub: str | None = None,
    ):
        self.current_tenant = current_tenant
        self.target_tenant = target_tenant
        self.operation = operation
        self.model = model
        self.actor_sub = actor_sub

        super().__init__(
            f"Tenant isolation violation: Attempted to {operation} data from tenant "
            f"'{target_tenant}' while authenticated as tenant '{current_tenant}' "
            f"(model: {model or 'unknown'}, actor: {actor_sub or 'unknown'})"
        )


class DataIntegrityViolation(XR7Exception):
    """Raised when data violates business invariants or integrity constraints."""


class ComplianceViolation(XR7Exception):
    """Raised when an operation would violate compliance requirements (GDPR, SOC 2, etc.)."""
