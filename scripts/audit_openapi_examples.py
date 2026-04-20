"""
Audit OpenAPI examples coverage across all routers.

Scans all router files for endpoints and checks if they have openapi_extra examples.
"""

from __future__ import annotations

import re
from pathlib import Path

ROUTER_DIR = Path("XR7/api/routers")


def scan_endpoints():
    """Scan all routers for endpoints and check OpenAPI coverage."""
    missing_examples = []
    has_examples = []

    for router_file in ROUTER_DIR.glob("**/*.py"):
        if router_file.name.startswith("_"):
            continue

        content = router_file.read_text(encoding="utf-8")

        # Find all @router.METHOD declarations
        endpoint_pattern = r'@router\.(get|post|put|delete|patch)\((.*?)\)'
        matches = re.finditer(endpoint_pattern, content, re.DOTALL)

        for match in matches:
            method = match.group(1).upper()
            args = match.group(2)

            # Extract path from first argument
            path_match = re.search(r'"([^"]+)"', args)
            if not path_match:
                path_match = re.search(r"'([^']+)'", args)

            if not path_match:
                continue

            path = path_match.group(1)

            # Check if openapi_extra is in the decorator arguments
            if "openapi_extra" in args:
                has_examples.append(
{
                    "file": str(router_file.relative_to(ROUTER_DIR.parent.parent)),
                    "method": method,
                    "path": path,
                }
            )
            else:
                missing_examples.append({
                    "file": str(router_file.relative_to(ROUTER_DIR.parent.parent)),
                    "method": method,
                    "path": path,
                })

    return has_examples, missing_examples


if __name__ == "__main__":
    has_examples, missing_examples = scan_endpoints()

    print(f"\n{'='*80}")
    print(f"OpenAPI Examples Coverage Audit")
    print(f"{'='*80}\n")

    print(f"✅ Endpoints WITH examples: {len(has_examples)}")
    print(f"❌ Endpoints WITHOUT examples: {len(missing_examples)}")
    print(f"📊 Coverage: {len(has_examples) / (len(has_examples) + len(missing_examples)) * 100:.1f}%")

    if missing_examples:
        print(f"\n{'='*80}")
        print("Missing Examples:")
        print(f"{'='*80}\n")

        # Group by file
        by_file: dict = {}
        for item in missing_examples:
            file = item["file"]
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(f"{item['method']:6} {item['path']}")

        for file, endpoints in sorted(by_file.items()):
            print(f"\n{file}:")
            for endpoint in sorted(endpoints):
                print(f"  - {endpoint}")

    print(f"\n{'='*80}\n")
