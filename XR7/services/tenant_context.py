"""Tenant isolation context for multi-tenant data access.

Provides context variables to track the current tenant and actor (user)
for tenant isolation enforcement at the database query level.
"""

from contextvars import ContextVar
from typing import Optional

# Context variables for tenant isolation
_current_tenant_id: ContextVar[Optional[str]] = ContextVar("current_tenant_id", default=None)
_current_actor_sub: ContextVar[Optional[str]] = ContextVar("current_actor_sub", default=None)


def get_current_tenant_id() -> Optional[str]:
    """
    Get the current tenant ID from context.
    
    Returns:
        Current tenant ID if set, None otherwise
    """
    return _current_tenant_id.get()


def set_current_tenant_id(tenant_id: Optional[str]) -> None:
    """
    Set the current tenant ID in context.
    
    Args:
        tenant_id: Tenant ID to set (e.g., artist ID, organization ID)
    """
    _current_tenant_id.set(tenant_id)


def get_current_actor_sub() -> Optional[str]:
    """
    Get the current actor subject (user ID) from context.
    
    Returns:
        Current actor subject if set, None otherwise
    """
    return _current_actor_sub.get()


def set_current_actor_sub(actor_sub: Optional[str]) -> None:
    """
    Set the current actor subject in context.
    
    Args:
        actor_sub: Actor subject (user ID) to set
    """
    _current_actor_sub.set(actor_sub)


def clear_tenant_context() -> None:
    """Clear both tenant ID and actor subject from context."""
    _current_tenant_id.set(None)
    _current_actor_sub.set(None)
