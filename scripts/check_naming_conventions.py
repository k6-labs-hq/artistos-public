#!/usr/bin/env python3
"""
check_naming_conventions.py
───────────────────────────
Enforces the XR7 domain naming standard across the codebase.

The full standard is documented in docs/developer_onboarding.md.

Category A violations detected (must fix before merge):
  - track_title / track_count  → use work_title / work_count
  - song_id / song_title       → use isrc / work_title
  - "entity": "track"          → use "entity": "recording"
  - "entity": "song"           → use "entity": "recording"
  - royalty_type: "sync"       → use royalty_type: "master_sync" or "pub_sync"

Allowed exceptions:
  - Parser/adapter files that read external CSV/JSON with these foreign field
    names are exempt (files matching */parsers/*, */adapters/*, */ingestion/*).
  - Migration files (*/versions/*.py, */alembic/*) are exempt.
  - Test fixtures are exempt (tests/fixtures/*, tests/data/*).
  - Comments are NOT exempt — they indicate confusion, not legacy data.

Exit code 0  = all rules pass.
Exit code 1  = one or more violations found (CI fails).

Run:  python scripts/check_naming_conventions.py
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files in these path segments are exempt from naming convention checks
EXEMPT_SEGMENTS = {
    "parsers",
    "adapters",
    "ingestion",
    "alembic",
    "versions",
    "fixtures",
}

# Files with these name patterns are exempt
EXEMPT_FILENAME_PATTERNS = [
    re.compile(r"test_data"),
    re.compile(r"conftest"),
]

# (pattern, description, allowed_in_exempt_paths)
RULES: list[tuple[re.Pattern, str, bool]] = [
    (
        re.compile(r"\btrack_title\b"),
        "Use 'work_title' (not 'track_title') — PPRD/DDEX domain term",
        False,
    ),
    (
        re.compile(r"\btrack_count\b"),
        "Use 'work_count' (not 'track_count') — PPRD/DDEX domain term",
        False,
    ),
    (
        re.compile(r"\bsong_id\b"),
        "Use 'isrc' or 'iswc' (not 'song_id') — PPRD/DDEX domain term",
        False,
    ),
    (
        re.compile(r"\bsong_title\b"),
        "Use 'work_title' (not 'song_title') — PPRD/DDEX domain term",
        False,
    ),
    (
        re.compile(r'"entity"\s*:\s*"track"'),
        'Use "entity": "recording" (not "entity": "track")',
        False,
    ),
    (
        re.compile(r'"entity"\s*:\s*"song"'),
        'Use "entity": "recording" (not "entity": "song")',
        False,
    ),
    (
        re.compile(r"'entity'\s*:\s*'track'"),
        "Use 'entity': 'recording' (not 'entity': 'track')",
        False,
    ),
    (
        re.compile(r"royalty_type\s*[=:]\s*['\"]sync['\"]"),
        "Use 'master_sync' or 'pub_sync' (not bare 'sync') for royalty_type",
        True,  # allow in parsers/adapters reading external data
    ),
]

SCAN_GLOBS = [
    "XR7/**/*.py",
    "shared/**/*.py",
    "xr7_common/**/*.py",
    "tests/**/*.py",
]

SKIP_GLOBS = [
    "alembic/**",
    "**/__pycache__/**",
    "**/*.pyc",
]


def is_exempt(filepath: Path) -> bool:
    parts = set(filepath.parts)
    if parts & EXEMPT_SEGMENTS:
        return True
    for pattern in EXEMPT_FILENAME_PATTERNS:
        if pattern.search(filepath.stem):
            return True
    return False


def is_parser_path(filepath: Path) -> bool:
    return bool(set(filepath.parts) & {"parsers", "adapters", "ingestion"})


def scan_file(
    filepath: Path, violations: list[str]
) -> None:
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
    except OSError:
        return

    exempt = is_exempt(filepath)
    parser_path = is_parser_path(filepath)
    relative = filepath.relative_to(REPO_ROOT)

    for rule_pattern, rule_desc, allows_in_parsers in RULES:
        if exempt and not allows_in_parsers:
            continue
        if parser_path and allows_in_parsers:
            continue

        for line_no, line in enumerate(lines, start=1):
            # Skip pure comments — but still flag them (they indicate confusion)
            stripped = line.lstrip()
            if rule_pattern.search(line):
                context = line.strip()[:80]
                violations.append(
                    f"{relative}:{line_no}: {rule_desc}\n"
                    f"    found: {context}"
                )


def main() -> int:
    print("Checking naming conventions...\n")

    # Collect candidate files
    all_files: set[Path] = set()
    for glob in SCAN_GLOBS:
        all_files.update(REPO_ROOT.glob(glob))

    # Remove skipped
    skip_files: set[Path] = set()
    for glob in SKIP_GLOBS:
        skip_files.update(REPO_ROOT.glob(glob))
    candidate_files = sorted(all_files - skip_files)

    violations: list[str] = []
    for filepath in candidate_files:
        scan_file(filepath, violations)

    if violations:
        print(f"FAIL — {len(violations)} naming convention violation(s) found:\n")
        for v in violations:
            print(f"  {v}\n")
        print(
            "See docs/developer_onboarding.md for the XR7 naming standard.\n"
            "Parser/adapter files that read external data are exempt automatically."
        )
        return 1

    print(
        f"PASS — naming conventions satisfied "
        f"(scanned {len(candidate_files)} files)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
