from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SPEC_PATH = Path("openapi/openapi.json")
OUT_PATH = Path("docs/api/reference.md")


def _schema_name(schema: dict[str, Any] | None) -> str:
    if not schema:
        return "-"
    ref = schema.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
        return ref.split("/")[-1]
    typ = schema.get("type")
    if isinstance(typ, str):
        return typ
    return "inline"


def _response_schema(op: dict[str, Any]) -> str:
    responses = op.get("responses") or {}
    for code in ("200", "201", "202", "204", "default"):
        if code not in responses:
            continue
        content = (responses[code] or {}).get("content") or {}
        app_json = content.get("application/json")
        if not app_json:
            if code == "204":
                return "none"
            continue
        schema = app_json.get("schema")
        return _schema_name(schema)
    return "-"


def _request_schema(op: dict[str, Any]) -> str:
    req = op.get("requestBody") or {}
    content = req.get("content") or {}
    app_json = content.get("application/json")
    if not app_json:
        return "-"
    return _schema_name(app_json.get("schema"))


def _tag_name(op: dict[str, Any]) -> str:
    tags = op.get("tags") or []
    if not tags:
        return "untagged"
    return str(tags[0])


def _sample_path(path: str, method: str, has_body: bool) -> str:
    base = "http://localhost:8000"
    sample = path
    for name in [
        "artist_id",
        "claim_id",
        "anomaly_id",
        "statement_id",
        "run_id",
        "job_id",
        "item_id",
        "id",
        "provider",
        "integration",
    ]:
        sample = sample.replace("{" + name + "}", f"<{name}>")
    if has_body:
        return f"curl -X {method.upper()} {base}{sample} -H 'Content-Type: application/json' -d '{{}}'"
    return f"curl -X {method.upper()} {base}{sample}"


def build_reference(spec: dict[str, Any]) -> str:
    paths = spec.get("paths") or {}
    rows: list[dict[str, str]] = []

    for path in sorted(paths.keys()):
        methods = paths[path] or {}
        for method in sorted(methods.keys()):
            if method.lower() not in {"get", "post", "put", "patch", "delete", "options", "head"}:
                continue
            op = methods[method] or {}
            summary = str(op.get("summary") or "-")
            operation_id = str(op.get("operationId") or "-")
            tag = _tag_name(op)
            req_schema = _request_schema(op)
            resp_schema = _response_schema(op)
            has_body = req_schema != "-"
            sample = _sample_path(path, method, has_body)
            rows.append(
                {
                    "Tag": tag,
                    "Method": method.upper(),
                    "Path": path,
                    "Summary": summary.replace("|", "\\|"),
                    "Operation ID": operation_id,
                    "Request": req_schema,
                    "Response": resp_schema,
                    "Example": sample.replace("|", "\\|").replace("\n", " "),
                }
            )

    lines: list[str] = []
    lines.append("# API Reference (OpenAPI Exhaustive)")
    lines.append("")
    lines.append("This file is generated from openapi/openapi.json. Do not hand-edit.")
    lines.append("")
    lines.append(f"Total endpoints: {len(rows)}")
    lines.append("")
    lines.append("## Endpoint Table")
    lines.append("")
    lines.append("| Tag | Method | Path | Summary | Operation ID | Request | Response | Example |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in rows:
        lines.append(
            f"| {row['Tag']} | {row['Method']} | {row['Path']} | {row['Summary']} | {row['Operation ID']} | {row['Request']} | {row['Response']} | {row['Example']} |"
        )

    lines.append("")
    lines.append("## Regeneration")
    lines.append("")
    lines.append("Run:")
    lines.append("")
    lines.append("```bash")
    lines.append("python scripts/export_openapi.py")
    lines.append("python scripts/generate_api_reference.py")
    lines.append("```")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    content = build_reference(spec)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(content, encoding="utf-8")
    print(f"Wrote exhaustive reference to {OUT_PATH}")


if __name__ == "__main__":
    main()
