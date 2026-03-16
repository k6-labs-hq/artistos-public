from __future__ import annotations

import importlib
import hmac
import hashlib
from dataclasses import dataclass
from typing import Any, Callable

from XR7.ingestion.parser_engine import ParserOutput
from xr7_common.logging import get_logger
from xr7_common.settings import settings

logger = get_logger(__name__)


class ParserPluginError(RuntimeError):
    """Raised when parser plugin loading, validation, or execution fails."""


@dataclass
class PluginParseResult:
    parser_type: str
    event_count: int
    events: list[dict[str, Any]]
    warnings: list[str]


def _load_entrypoint(entrypoint: str) -> Callable[[bytes, str, str], Any]:
    if ":" not in entrypoint:
        raise ParserPluginError("Plugin entrypoint must be '<module.path>:<callable>'")
    module_name, callable_name = entrypoint.split(":", 1)

    allowed = settings.plugin_allowed_prefixes
    blocked = settings.plugin_blocked_prefixes
    if blocked and any(module_name == p or module_name.startswith(f"{p}.") for p in blocked):
        raise ParserPluginError("Plugin module prefix is blocked by sandbox policy")
    if allowed and not any(module_name == p or module_name.startswith(f"{p}.") for p in allowed):
        raise ParserPluginError("Plugin module prefix is not allowed by sandbox policy")

    module = importlib.import_module(module_name)
    fn = getattr(module, callable_name, None)
    if fn is None or not callable(fn):
        raise ParserPluginError(f"Plugin callable '{callable_name}' was not found")
    return fn


def verify_plugin_signature(*, entrypoint: str, plugin_signature: str | None) -> None:
    secret = settings.plugin_signature_secret
    if not secret:
        return
    if not plugin_signature:
        raise ParserPluginError("Plugin signature is required by policy")
    expected = hmac.new(secret.encode("utf-8"), entrypoint.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, plugin_signature):
        raise ParserPluginError("Plugin signature verification failed")


def parse_with_plugin(
    *,
    entrypoint: str,
    parser_type: str,
    content: bytes,
    artist_id: str,
    filename: str,
    plugin_signature: str | None = None,
) -> ParserOutput:
    try:
        verify_plugin_signature(entrypoint=entrypoint, plugin_signature=plugin_signature)
        fn = _load_entrypoint(entrypoint)
        result = fn(content, artist_id, filename)
    except ParserPluginError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ParserPluginError(f"Plugin execution failed: {exc}") from exc

    # Supported plugin contract options:
    # 1) return ParserOutput directly
    # 2) return dict with keys events/warnings/parser_type
    # 3) return list of event dicts
    if isinstance(result, ParserOutput):
        return result
    if isinstance(result, dict):
        events = result.get("events") or []
        warnings = result.get("warnings") or []
        resolved_type = str(result.get("parser_type") or parser_type)
        return ParserOutput(resolved_type, len(events), list(events), list(warnings))
    if isinstance(result, list):
        return ParserOutput(parser_type, len(result), list(result), [])

    raise ParserPluginError("Plugin returned unsupported payload type")
