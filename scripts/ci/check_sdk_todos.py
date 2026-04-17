#!/usr/bin/env python3
"""
CI check to detect TODO placeholders in SDK documentation.

This script scans Python and TypeScript SDK documentation files
for TODO placeholders that indicate missing or incomplete examples.
Exits with code 1 if placeholders are found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


TODO_PATTERNS = [
    r"#\s*TODO.*update.*JSON",  # Python: # TODO update the JSON string below
    r"//\s*TODO.*Update.*object",  # TypeScript: // TODO: Update the object below
    r'".*":\s*null',  # TypeScript/JSON: "email": null (placeholder values)
]


def check_file_for_todos(file_path: Path) -> list[tuple[int, str]]:
    """
    Check a single file for TODO placeholders.

    Args:
        file_path: Path to the documentation file

    Returns:
        List of (line_number, line_content) tuples for lines with TODOs
    """
    todos = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                for pattern in TODO_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        todos.append((line_num, line.rstrip()))
                        break  # Only report each line once
    except Exception as e:
        print(f"⚠️  Warning: Could not read {file_path}: {e}", file=sys.stderr)

    return todos


def check_sdk_docs(sdk_path: Path) -> dict[Path, list[tuple[int, str]]]:
    """
    Check all documentation files in an SDK directory.

    Args:
        sdk_path: Path to SDK directory (e.g., sdk/python or sdk/typescript)

    Returns:
        Dictionary mapping file paths to lists of TODO occurrences
    """
    docs_path = sdk_path / "docs"
    if not docs_path.exists():
        return {}

    results = {}

    for doc_file in docs_path.glob("*.md"):
        todos = check_file_for_todos(doc_file)
        if todos:
            results[doc_file] = todos

    return results


def main() -> int:
    """
    Main entry point for CI check.

    Returns:
        0 if no TODOs found, 1 if TODOs detected
    """
    root = Path(__file__).resolve().parents[2]  # Go up 2 levels from scripts/ci/
    sdk_root = root / "sdk"

    if not sdk_root.exists():
        print(f"❌ SDK directory not found at {sdk_root}", file=sys.stderr)
        return 1

    print("🔍 Checking SDK documentation for TODO placeholders...\n")

    all_results = {}
    total_files = 0
    total_todos = 0

    # Check Python SDK
    python_path = sdk_root / "python"
    if python_path.exists():
        python_results = check_sdk_docs(python_path)
        all_results["Python"] = python_results
        total_files += len(python_results)
        total_todos += sum(len(todos) for todos in python_results.values())

    # Check TypeScript SDK
    typescript_path = sdk_root / "typescript"
    if typescript_path.exists():
        typescript_results = check_sdk_docs(typescript_path)
        all_results["TypeScript"] = typescript_results
        total_files += len(typescript_results)
        total_todos += sum(len(todos) for todos in typescript_results.values())

    # Report findings
    if total_todos == 0:
        print("✅ No TODO placeholders found in SDK documentation!")
        return 0

    print(f"❌ Found TODO placeholders in {total_files} files:\n")

    for sdk_name, results in all_results.items():
        if not results:
            continue

        print(f"=== {sdk_name} SDK ===")
        for file_path, todos in sorted(results.items()):
            rel_path = file_path.relative_to(root)
            print(f"\n  {rel_path} ({len(todos)} issues):")
            for line_num, line_content in todos[:3]:  # Show first 3
                print(f"    Line {line_num}: {line_content[:80]}")
            if len(todos) > 3:
                print(f"    ... and {len(todos) - 3} more")

    print(f"\n📊 Summary: {total_todos} TODO placeholders in {total_files} files")
    print("\n💡 To fix: Run `make sdks` to regenerate SDK documentation with examples")

    return 1


if __name__ == "__main__":
    sys.exit(main())
