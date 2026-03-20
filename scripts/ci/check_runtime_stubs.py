#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

INCLUDE_DIRS = [
    REPO_ROOT / "XR7",
    REPO_ROOT / "xr7_common",
]

EXCLUDE_PATH_PARTS = {
    "/.git/",
    "/.venv/",
    "/node_modules/",
    "/sdk/",
    "/tests/",
    "/alembic/",
    "/__pycache__/",
}

# Allowed emergency placeholders in runtime code by exact relative path and regex snippets.
# Keep this list intentionally small.
ALLOWLIST: dict[str, list[str]] = {
    "XR7/llm/claim_drafter.py": [r"use placeholders if not present"],
}

RULES = [
    ("not_implemented", re.compile(r"\braise\s+NotImplementedError\b")),
    ("todo", re.compile(r"\bTODO\b")),
    ("fixme", re.compile(r"\bFIXME\b")),
    ("placeholder_marker", re.compile(r"pdf_placeholder|placeholder implementation|stubbed", re.IGNORECASE)),
]


def _is_excluded(path: Path) -> bool:
    posix = "/" + str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    return any(part in posix for part in EXCLUDE_PATH_PARTS)


def _is_allowed(rel_path: str, line: str) -> bool:
    allowed = ALLOWLIST.get(rel_path, [])
    return any(re.search(pattern, line, flags=re.IGNORECASE) for pattern in allowed)


def main() -> int:
    violations: list[tuple[str, int, str, str]] = []

    for root in INCLUDE_DIRS:
        if not root.exists():
            continue
        for py_file in root.rglob("*.py"):
            if _is_excluded(py_file):
                continue

            rel = str(py_file.relative_to(REPO_ROOT)).replace("\\", "/")
            try:
                lines = py_file.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                continue

            for idx, line in enumerate(lines, start=1):
                if _is_allowed(rel, line):
                    continue
                for rule_name, pattern in RULES:
                    if pattern.search(line):
                        violations.append((rel, idx, rule_name, line.strip()))
                        break

    if violations:
        print("Runtime stub policy violations found:")
        for rel, line_no, rule_name, line in violations:
            print(f"- {rel}:{line_no} [{rule_name}] {line}")
        return 1

    print("Runtime stub policy check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
