from __future__ import annotations

from scripts.ci.check_openapi_breaking import find_breaking_changes


def _doc(paths=None, schemas=None):
    return {
        "openapi": "3.1.0",
        "info": {"title": "t", "version": "1"},
        "paths": paths or {},
        "components": {"schemas": schemas or {}},
    }


def test_removed_path_is_breaking():
    old = _doc(paths={"/items": {"get": {"responses": {"200": {"description": "ok"}}}}})
    new = _doc(paths={})
    issues = find_breaking_changes(old, new)
    assert any("removed path /items" in issue for issue in issues)


def test_parameter_becomes_required_is_breaking():
    old = _doc(
        paths={
            "/items": {
                "get": {
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                        },
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        }
    )
    new = _doc(
        paths={
            "/items": {
                "get": {
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        }
    )
    issues = find_breaking_changes(old, new)
    assert any("parameter became required: query:limit" in issue for issue in issues)


def test_removed_schema_property_is_breaking():
    old = _doc(
        schemas={
            "Item": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                },
            }
        }
    )
    new = _doc(
        schemas={
            "Item": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                },
            }
        }
    )
    issues = find_breaking_changes(old, new)
    assert any("property removed: name" in issue for issue in issues)


def test_added_optional_property_is_not_breaking():
    old = _doc(schemas={"Item": {"type": "object", "properties": {"id": {"type": "string"}}}})
    new = _doc(
        schemas={
            "Item": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                },
            }
        }
    )
    issues = find_breaking_changes(old, new)
    assert issues == []
