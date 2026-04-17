from __future__ import annotations

from contextvars import ContextVar, Token

_current_tenant_id: ContextVar[str] = ContextVar("current_tenant_id", default="")
_current_actor_sub: ContextVar[str] = ContextVar("current_actor_sub", default="")


def set_tenant_context(tenant_id: str, actor_sub: str | None = None) -> tuple[Token, Token]:
    tenant_token = _current_tenant_id.set((tenant_id or "").strip())
    actor_token = _current_actor_sub.set((actor_sub or "").strip())
    return tenant_token, actor_token


def reset_tenant_context(tokens: tuple[Token, Token]) -> None:
    tenant_token, actor_token = tokens
    _current_tenant_id.reset(tenant_token)
    _current_actor_sub.reset(actor_token)


def get_current_tenant_id() -> str:
    return _current_tenant_id.get("")


def get_current_actor_sub() -> str:
    return _current_actor_sub.get("")
