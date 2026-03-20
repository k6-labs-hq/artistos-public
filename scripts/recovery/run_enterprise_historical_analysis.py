#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from XR7.services.enterprise_historical_analysis import analyze_historical_portfolio


def _load_rows(path: Path) -> list[dict[str, str]]:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        return [dict(r) for r in reader]


def _to_markdown(summary: dict) -> str:
    lines = [
        f"# {summary['organization_name']} Historical Analysis",
        "",
        f"- Entity Type: {summary['entity_type']}",
        f"- Analysis Time: {summary['analysis_completed_at']}",
        f"- Roster Size: {summary['roster_size']}",
        f"- Total Estimated Recoverable: ${float(summary['total_estimated_recoverable']):,.2f}",
        "",
        "## Vertical Breakdown",
        "",
        "| Vertical | Clients | Estimated Recoverable |",
        "|---|---:|---:|",
    ]
    for vertical, payload in (summary.get("by_vertical") or {}).items():
        lines.append(
            f"| {vertical} | {int(payload.get('clients', 0))} | ${float(payload.get('estimated_recoverable', 0.0)):,.2f} |"
        )

    lines.extend(
        [
            "",
            "## SOL Risk",
            "",
            f"- High: {int((summary.get('sol_risk') or {}).get('high', 0))}",
            f"- Medium: {int((summary.get('sol_risk') or {}).get('medium', 0))}",
            f"- Low: {int((summary.get('sol_risk') or {}).get('low', 0))}",
            f"- Unknown: {int((summary.get('sol_risk') or {}).get('unknown', 0))}",
            "",
            "## Top Clients (Top 10)",
            "",
            "| Client | Vertical | Recoverable | SOL Risk |",
            "|---|---|---:|---|",
        ]
    )

    for row in (summary.get("top_25_clients") or [])[:10]:
        lines.append(
            f"| {row.get('client')} | {row.get('vertical')} | ${float(row.get('estimated_recoverable', 0.0)):,.2f} | {row.get('sol_risk')} |"
        )

    lines.extend(["", "## Next 24h", ""])
    for item in (summary.get("execution_plan") or {}).get("next_24h", []):
        lines.append(f"- {item}")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run enterprise mixed-vertical historical analysis from CSV/TSV")
    parser.add_argument("--input", required=True, help="Path to roster historical CSV/TSV")
    parser.add_argument("--organization", required=True, help="Organization name (for report metadata)")
    parser.add_argument("--entity-type", default="Talent Agency", help="Entity type label")
    parser.add_argument("--out-json", default="artifacts/enterprise_historical_analysis.json", help="JSON output path")
    parser.add_argument("--out-md", default="artifacts/enterprise_historical_analysis.md", help="Markdown output path")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    rows = _load_rows(in_path)
    if not rows:
        raise SystemExit("No rows found in input file")

    summary = analyze_historical_portfolio(
        organization_name=args.organization,
        entity_type=args.entity_type,
        records=rows,
    )

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    out_md.write_text(_to_markdown(summary), encoding="utf-8")

    print(f"[enterprise-analysis] roster={summary['roster_size']} total=${summary['total_estimated_recoverable']:,.2f}")
    print(f"[enterprise-analysis] json={out_json}")
    print(f"[enterprise-analysis] markdown={out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
