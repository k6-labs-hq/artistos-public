from __future__ import annotations

import ast
from pathlib import Path

ROUTER_ROOT = Path(__file__).resolve().parents[1] / "XR7" / "api" / "routers"
HTTP_DECORATORS = {"get", "post", "put", "patch", "delete"}
SKIP_FILES = {"admin_console.py"}


def _route_path(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    for dec in node.decorator_list:
        if not isinstance(dec, ast.Call):
            continue
        if not isinstance(dec.func, ast.Attribute):
            continue
        if dec.func.attr not in HTTP_DECORATORS:
            continue
        if not dec.args:
            continue
        first = dec.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
    return None


def _has_identity_dict_return(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[bool, bool]:
    has_identity = False
    has_branding_key = False
    for ret in ast.walk(node):
        if not isinstance(ret, ast.Return):
            continue
        value = ret.value
        if not isinstance(value, ast.Dict):
            continue
        for key in value.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                if key.value in {"artist_id", "org_id"}:
                    has_identity = True
                if key.value == "branding":
                    has_branding_key = True
    return has_identity, has_branding_key


def test_router_identity_payloads_use_branding_contract():
    violations: list[str] = []

    for path in sorted(ROUTER_ROOT.glob("*.py")):
        if path.name in SKIP_FILES:
            continue

        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            route_path = _route_path(node)
            if not route_path:
                continue
            if route_path.startswith("/admin"):
                continue

            has_identity_return, has_branding_key = _has_identity_dict_return(node)
            if not has_identity_return:
                continue

            segment = ast.get_source_segment(source, node) or ""
            has_injection = "inject_branding_metadata(" in segment
            has_branding_helper = "branding_metadata(" in segment

            if has_branding_key or has_injection or has_branding_helper:
                continue

            violations.append(f"{path.name}:{node.lineno} {node.name} {route_path}")

    assert not violations, "Branding contract violations found:\n" + "\n".join(violations)
