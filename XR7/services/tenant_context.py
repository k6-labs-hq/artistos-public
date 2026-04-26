from __future__ import annotations

_tenant_context: str | None = None


def set_tenant_context(tenant_id: str | None) -> None:
    global _tenant_context
    _tenant_context = tenant_id


def get_tenant_context() -> str | None:
    return _tenant_context


def get_current_tenant_id() -> str | None:
    """Get current tenant ID from context."""
    return _tenant_context


def get_current_actor_sub() -> str | None:
    """Get current actor subject (user identifier) from context."""
    return None


def reset_tenant_context() -> None:
    global _tenant_context
    _tenant_context = None
