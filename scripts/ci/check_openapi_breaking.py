#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def _resolve_ref(doc: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        return {"$ref": ref}
    node: Any = doc
    for part in ref[2:].split("/"):
        if not isinstance(node, dict):
            return {"$ref": ref}
        node = node.get(part)
    return node if isinstance(node, dict) else {"$ref": ref}


def _materialize_schema(doc: dict[str, Any], schema: dict[str, Any] | None) -> dict[str, Any]:
    if not schema:
        return {}
    if "$ref" in schema and isinstance(schema["$ref"], str):
        return _materialize_schema(doc, _resolve_ref(doc, schema["$ref"]))
    return schema


def _schema_type(schema: dict[str, Any]) -> str | None:
    value = schema.get("type")
    return str(value) if value is not None else None


def _compare_schema(
    old_doc: dict[str, Any],
    new_doc: dict[str, Any],
    old_schema: dict[str, Any] | None,
    new_schema: dict[str, Any] | None,
    path: str,
    issues: list[str],
) -> None:
    old = _materialize_schema(old_doc, old_schema)
    new = _materialize_schema(new_doc, new_schema)

    old_type = _schema_type(old)
    new_type = _schema_type(new)
    if old_type and new_type and old_type != new_type:
        issues.append(f"{path}: schema type changed from {old_type} to {new_type}")
        return

    old_enum = old.get("enum") if isinstance(old.get("enum"), list) else None
    new_enum = new.get("enum") if isinstance(new.get("enum"), list) else None
    if old_enum is not None and new_enum is not None:
        removed = sorted(set(map(str, old_enum)) - set(map(str, new_enum)))
        if removed:
            issues.append(f"{path}: enum values removed: {', '.join(removed)}")

    if (old_type == "object") or ("properties" in old) or ("properties" in new):
        old_props = old.get("properties") if isinstance(old.get("properties"), dict) else {}
        new_props = new.get("properties") if isinstance(new.get("properties"), dict) else {}
        removed_props = sorted(set(old_props) - set(new_props))
        for prop in removed_props:
            issues.append(f"{path}: property removed: {prop}")

        old_required = set(old.get("required") or [])
        new_required = set(new.get("required") or [])
        added_required = sorted(new_required - old_required)
        for prop in added_required:
            issues.append(f"{path}: property became required: {prop}")

        for prop in sorted(set(old_props) & set(new_props)):
            _compare_schema(
                old_doc,
                new_doc,
                old_props.get(prop),
                new_props.get(prop),
                f"{path}.{prop}",
                issues,
            )
        return

    if (old_type == "array") or ("items" in old) or ("items" in new):
        _compare_schema(old_doc, new_doc, old.get("items"), new.get("items"), f"{path}[]", issues)


def _parameter_key(param: dict[str, Any]) -> tuple[str, str]:
    return (str(param.get("in") or ""), str(param.get("name") or ""))


def _compare_parameters(old_params: list[dict[str, Any]], new_params: list[dict[str, Any]], path: str, issues: list[str]) -> None:
    old_map = {_parameter_key(p): p for p in old_params}
    new_map = {_parameter_key(p): p for p in new_params}

    for key in sorted(set(old_map) - set(new_map)):
        issues.append(f"{path}: parameter removed: {key[0]}:{key[1]}")

    for key in sorted(set(old_map) & set(new_map)):
        old_param = old_map[key]
        new_param = new_map[key]
        if not bool(old_param.get("required")) and bool(new_param.get("required")):
            issues.append(f"{path}: parameter became required: {key[0]}:{key[1]}")


def _success_codes(responses: dict[str, Any]) -> set[str]:
    return {code for code in responses if str(code).startswith("2")}


def _compare_operation(
    old_doc: dict[str, Any],
    new_doc: dict[str, Any],
    old_op: dict[str, Any],
    new_op: dict[str, Any],
    path: str,
    issues: list[str],
) -> None:
    old_operation_id = str(old_op.get("operationId") or "")
    new_operation_id = str(new_op.get("operationId") or "")
    if old_operation_id and new_operation_id and old_operation_id != new_operation_id:
        issues.append(f"{path}: operationId changed from {old_operation_id} to {new_operation_id}")

    _compare_parameters(
        list(old_op.get("parameters") or []),
        list(new_op.get("parameters") or []),
        path,
        issues,
    )

    old_request = old_op.get("requestBody") if isinstance(old_op.get("requestBody"), dict) else None
    new_request = new_op.get("requestBody") if isinstance(new_op.get("requestBody"), dict) else None
    if old_request is None and new_request is not None and bool(new_request.get("required")):
        issues.append(f"{path}: required request body was added")
    elif old_request is not None and new_request is None:
        issues.append(f"{path}: request body was removed")
    elif old_request and new_request:
        if not bool(old_request.get("required")) and bool(new_request.get("required")):
            issues.append(f"{path}: request body became required")
        old_content = old_request.get("content") if isinstance(old_request.get("content"), dict) else {}
        new_content = new_request.get("content") if isinstance(new_request.get("content"), dict) else {}
        removed_types = sorted(set(old_content) - set(new_content))
        for content_type in removed_types:
            issues.append(f"{path}: request content type removed: {content_type}")
        for content_type in sorted(set(old_content) & set(new_content)):
            _compare_schema(
                old_doc,
                new_doc,
                (old_content.get(content_type) or {}).get("schema"),
                (new_content.get(content_type) or {}).get("schema"),
                f"{path}.requestBody[{content_type}]",
                issues,
            )

    old_responses = old_op.get("responses") if isinstance(old_op.get("responses"), dict) else {}
    new_responses = new_op.get("responses") if isinstance(new_op.get("responses"), dict) else {}
    removed_success = sorted(_success_codes(old_responses) - _success_codes(new_responses))
    for status in removed_success:
        issues.append(f"{path}: success response removed: {status}")

    for status in sorted(_success_codes(old_responses) & _success_codes(new_responses)):
        old_content = (old_responses.get(status) or {}).get("content") if isinstance((old_responses.get(status) or {}).get("content"), dict) else {}
        new_content = (new_responses.get(status) or {}).get("content") if isinstance((new_responses.get(status) or {}).get("content"), dict) else {}
        removed_types = sorted(set(old_content) - set(new_content))
        for content_type in removed_types:
            issues.append(f"{path}: response content type removed for {status}: {content_type}")
        for content_type in sorted(set(old_content) & set(new_content)):
            _compare_schema(
                old_doc,
                new_doc,
                (old_content.get(content_type) or {}).get("schema"),
                (new_content.get(content_type) or {}).get("schema"),
                f"{path}.responses[{status}][{content_type}]",
                issues,
            )


def find_breaking_changes(old_doc: dict[str, Any], new_doc: dict[str, Any]) -> list[str]:
    issues: list[str] = []

    old_paths = old_doc.get("paths") if isinstance(old_doc.get("paths"), dict) else {}
    new_paths = new_doc.get("paths") if isinstance(new_doc.get("paths"), dict) else {}

    for path in sorted(set(old_paths) - set(new_paths)):
        issues.append(f"paths: removed path {path}")

    http_methods = {"get", "post", "put", "patch", "delete", "options", "head"}
    for path in sorted(set(old_paths) & set(new_paths)):
        old_item = old_paths.get(path) if isinstance(old_paths.get(path), dict) else {}
        new_item = new_paths.get(path) if isinstance(new_paths.get(path), dict) else {}
        old_methods = {m for m in old_item if m.lower() in http_methods}
        new_methods = {m for m in new_item if m.lower() in http_methods}

        for method in sorted(old_methods - new_methods):
            issues.append(f"paths: removed operation {method.upper()} {path}")

        for method in sorted(old_methods & new_methods):
            _compare_operation(
                old_doc,
                new_doc,
                old_item.get(method) or {},
                new_item.get(method) or {},
                f"{method.upper()} {path}",
                issues,
            )

    old_schemas = (((old_doc.get("components") or {}).get("schemas")) if isinstance((old_doc.get("components") or {}).get("schemas"), dict) else {})
    new_schemas = (((new_doc.get("components") or {}).get("schemas")) if isinstance((new_doc.get("components") or {}).get("schemas"), dict) else {})

    for schema_name in sorted(set(old_schemas) - set(new_schemas)):
        issues.append(f"components: removed schema {schema_name}")

    for schema_name in sorted(set(old_schemas) & set(new_schemas)):
        _compare_schema(
            old_doc,
            new_doc,
            old_schemas.get(schema_name),
            new_schemas.get(schema_name),
            f"components.schemas.{schema_name}",
            issues,
        )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect breaking OpenAPI changes.")
    parser.add_argument("old_schema", type=Path)
    parser.add_argument("new_schema", type=Path)
    args = parser.parse_args()

    old_doc = _load_json(args.old_schema)
    new_doc = _load_json(args.new_schema)
    issues = find_breaking_changes(old_doc, new_doc)

    if issues:
        print("Breaking OpenAPI changes detected:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("No breaking OpenAPI changes detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
