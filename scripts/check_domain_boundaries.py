#!/usr/bin/env python3
"""
check_domain_boundaries.py
──────────────────────────
Enforces architectural layer isolation rules for the XR7 codebase.

Rules enforced:
  1. XR7/core/**     — may NOT import from XR7.services, XR7.api, XR7.recovery,
                       XR7.fingerprinting, XR7.ml, or sqlalchemy.
  2. shared/utils/** — may NOT import from XR7.* (one-way dependency).
  3. XR7/api/**      — may NOT instantiate db.query() or db.execute() directly
                       (ORM access must go through service layer).
  4. XR7/ml/**       — may NOT import from XR7.recovery or XR7.blockchain.

Exit code 0  = all rules pass.
Exit code 1  = one or more violations found (CI fails).

Run:  python scripts/check_domain_boundaries.py
"""

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

RULES: list[dict] = [
    {
        "name": "core-isolation",
        "description": "XR7/core/ must not import from services, api, recovery, fingerprinting, ml, or sqlalchemy",
        "scan_glob": "XR7/core/**/*.py",
        "forbidden_prefixes": [
            "XR7.services",
            "XR7.api",
            "XR7.recovery",
            "XR7.fingerprinting",
            "XR7.ml",
            "sqlalchemy",
        ],
    },
    {
        "name": "shared-isolation",
        "description": "shared/utils/ must not import from XR7.*",
        "scan_glob": "shared/utils/**/*.py",
        "forbidden_prefixes": ["XR7"],
    },
    {
        "name": "ml-isolation",
        "description": "XR7/ml/ must not import from XR7.recovery or XR7.blockchain",
        "scan_glob": "XR7/ml/**/*.py",
        "forbidden_prefixes": ["XR7.recovery", "XR7.blockchain"],
    },
]

RAW_GREP_RULES: list[dict] = [
    {
        "name": "api-orm-direct",
        "description": "XR7/api/ routers must not call db.query() or db.execute() directly",
        "scan_glob": "XR7/api/**/*.py",
        "forbidden_patterns": [r"db\.query(", r"db\.execute("],
    },
]


def collect_imports(filepath: Path) -> list[str]:
    """Return all module names imported in a Python file."""
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def check_import_rules() -> list[str]:
    violations: list[str] = []
    for rule in RULES:
        files = list(REPO_ROOT.glob(rule["scan_glob"]))
        for filepath in files:
            relative = filepath.relative_to(REPO_ROOT)
            imports = collect_imports(filepath)
            for imp in imports:
                for prefix in rule["forbidden_prefixes"]:
                    if imp == prefix or imp.startswith(prefix + "."):
                        violations.append(
                            f"[{rule['name']}] {relative}: "
                            f"forbidden import '{imp}' (rule: {rule['description']})"
                        )
    return violations


def check_raw_grep_rules() -> list[str]:
    violations: list[str] = []
    for rule in RAW_GREP_RULES:
        files = list(REPO_ROOT.glob(rule["scan_glob"]))
        for filepath in files:
            relative = filepath.relative_to(REPO_ROOT)
            try:
                content = filepath.read_text(encoding="utf-8")
            except OSError:
                continue
            for line_no, line in enumerate(content.splitlines(), start=1):
                for pattern in rule["forbidden_patterns"]:
                    if pattern in line:
                        violations.append(
                            f"[{rule['name']}] {relative}:{line_no}: "
                            f"forbidden pattern '{pattern}' — {rule['description']}"
                        )
    return violations


def main() -> int:
    print("Checking domain boundaries...\n")
    violations = check_import_rules() + check_raw_grep_rules()

    if violations:
        print(f"FAIL — {len(violations)} domain boundary violation(s) found:\n")
        for v in violations:
            print(f"  {v}")
        print(
            "\nSee docs/developer_onboarding.md Section 9 for boundary rules."
        )
        return 1

    print("PASS — all domain boundary rules satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
