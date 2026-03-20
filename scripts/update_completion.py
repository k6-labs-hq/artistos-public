#!/usr/bin/env python3
"""
scripts/update_completion.py

Calculates project completion % and updates the README.md badge section.
Automatically invoked via .githooks/pre-commit on every commit.

Signals (weighted):
    45%  Market Readiness  — ✅ Ready items in the README table
    25%  Test Coverage     — test functions collected in tests/
    20%  Documentation     — docs/ files without placeholder content
    10%  Infrastructure    — key project files present
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"

MARKER_START = "<!-- COMPLETION_START -->"
MARKER_END = "<!-- COMPLETION_END -->"

WEIGHT_MARKET_READINESS = 0.45
WEIGHT_TEST_COVERAGE = 0.25
WEIGHT_DOC_COMPLETENESS = 0.20
WEIGHT_INFRASTRUCTURE = 0.10
TEST_FUNCTION_TARGET = 300

# ── signals ────────────────────────────────────────────────────────────────

def _market_readiness():
    """Parse the '## Market Readiness' table for ✅ / 🔑 / ⚠️ rows."""
    text = README_PATH.read_text(encoding="utf-8")
    # Scope to the Market Readiness section only
    m = re.search(r"## Market Readiness(.*?)(?=\n## |\n---|\Z)", text, re.DOTALL)
    section = m.group(1) if m else text
    ready      = len(re.findall(r"✅ Ready",    section))
    key_needed = len(re.findall(r"🔑 Key needed", section))
    pending    = len(re.findall(r"⚠️ Pending",  section))
    total      = ready + key_needed + pending
    score      = (ready + key_needed * 0.5) / total if total else 1.0
    return score, ready, key_needed, pending, total


def _test_coverage():
    """Count test functions across tests/*.py. Target = 300 for 100%."""
    tests_dir = ROOT / "tests"
    count = sum(
        len(re.findall(r"^def test_", f.read_text(encoding="utf-8"), re.MULTILINE))
        for f in tests_dir.glob("test_*.py")
    )
    target = TEST_FUNCTION_TARGET
    return min(count / target, 1.0), count, target


def _doc_completeness():
    """Fraction of docs/*.md files that have no placeholder content."""
    docs_dir = ROOT / "docs"
    all_docs = [f for f in docs_dir.glob("*.md") if f.name != "README.md"]
    total = len(all_docs)
    if not total:
        return 1.0, 0, 0
    placeholder_re = re.compile(r"^Placeholder documentation\.$", re.MULTILINE)
    placeholders = sum(
        1 for f in all_docs
        if placeholder_re.search(f.read_text(encoding="utf-8"))
    )
    completed = total - placeholders
    return completed / total, completed, total


def _infrastructure():
    """Presence of key project files and platform infrastructure."""
    k8s_overlays = (ROOT / "infrastructure/kubernetes/overlays")
    checks = {
        # app baseline
        "Dockerfile":                 (ROOT / "Dockerfile").exists(),
        "docker-compose.yml":         (ROOT / "docker-compose.yml").exists(),
        "pyproject.toml":             (ROOT / "pyproject.toml").exists(),
        "CI workflows":               any((ROOT / ".github/workflows").glob("*.yml")),
        "OpenAPI spec":               (ROOT / "openapi/openapi.json").exists(),
        "TS SDK lockfile":            (ROOT / "sdk/typescript/package-lock.json").exists(),
        "Alembic migrations":         any((ROOT / "alembic/versions").glob("[0-9]*.py")),
        "requirements.txt":           (ROOT / "requirements.txt").exists(),
        # kubernetes platform
        "K8s base manifests":         (ROOT / "infrastructure/kubernetes/base/kustomization.yaml").exists(),
        "K8s env overlays":           all((k8s_overlays / e / "kustomization.yaml").exists() for e in ["dev", "staging", "prod"]),
        "K8s autoscaling":            (ROOT / "infrastructure/kubernetes/base/autoscaling.yaml").exists(),
        "K8s backup cron":            (ROOT / "infrastructure/kubernetes/base/backup-cronjob.yaml").exists(),
        "K8s security policies":      (ROOT / "infrastructure/kubernetes/base/security.yaml").exists(),
        # terraform
        "Terraform aws_foundation":   (ROOT / "infrastructure/terraform/modules/aws_foundation/main.tf").exists(),
        "Terraform platform module":  (ROOT / "infrastructure/terraform/modules/platform/main.tf").exists(),
        "Terraform dev env":          (ROOT / "infrastructure/terraform/environments/dev/main.tf").exists(),
        "Terraform staging env":      (ROOT / "infrastructure/terraform/environments/staging/main.tf").exists(),
        "Terraform prod env":         (ROOT / "infrastructure/terraform/environments/prod/main.tf").exists(),
        # operations
        "Deploy script":              (ROOT / "scripts/ops/deploy_env.sh").exists(),
        "Bootstrap script":           (ROOT / "scripts/ops/bootstrap_env.sh").exists(),
        "SLO gate script":            (ROOT / "scripts/ops/slo_gate.sh").exists(),
        "DR restore drill":           (ROOT / "scripts/ops/restore_drill.sh").exists(),
        # observability
        "OTel collector config":      (ROOT / "infrastructure/observability/otel/collector-config.yaml").exists(),
        "Prometheus SLO rules":       (ROOT / "infrastructure/observability/prometheus/slo-rules.yaml").exists(),
        "Grafana dashboard":          (ROOT / "infrastructure/observability/grafana/xr7-overview-dashboard.json").exists(),
        # incident runbooks
        "Incident runbook":           (ROOT / "infrastructure/runbooks/incident_response.md").exists(),
        "DR runbook":                 (ROOT / "infrastructure/runbooks/disaster_recovery.md").exists(),
    }
    present = sum(checks.values())
    total   = len(checks)
    return present / total, present, total, checks


# ── rendering ──────────────────────────────────────────────────────────────

def _bar(pct: float, width: int = 20) -> str:
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


def _build_section(pct, mr, tests, docs, infra) -> str:
    mr_score, ready, key_needed, pending, mr_total = mr
    _,         test_count, _                        = tests
    doc_score, doc_done,   doc_total                = docs
    _,         infra_ok,   infra_total, _           = infra

    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    return "\n".join([
        MARKER_START,
        "",
        f"## Project Completion: {pct:.0f}%",
        "",
        f"`{_bar(pct)}` **{pct:.0f}%** — {today}",
        "",
        "| Signal | Detail | Weight |",
        "|--------|--------|--------|",
        f"| 🚀 Market Readiness | {ready} ✅&nbsp; {key_needed} 🔑&nbsp; {pending} ⚠️&nbsp; ({mr_score*100:.0f}% of {mr_total} components) | {WEIGHT_MARKET_READINESS*100:.0f}% |",
        f"| 🧪 Test Coverage | {test_count}/{TEST_FUNCTION_TARGET} test functions ({tests[0]*100:.0f}%) | {WEIGHT_TEST_COVERAGE*100:.0f}% |",
        f"| 📚 Documentation | {doc_done}/{doc_total} docs complete ({doc_score*100:.0f}%) | {WEIGHT_DOC_COMPLETENESS*100:.0f}% |",
        f"| ⚙️  Infrastructure | {infra_ok}/{infra_total} checks passing | {WEIGHT_INFRASTRUCTURE*100:.0f}% |",
        "",
        MARKER_END,
    ])


# ── main ───────────────────────────────────────────────────────────────────

def main() -> int:
    readme = README_PATH.read_text(encoding="utf-8")

    mr    = _market_readiness()
    tests = _test_coverage()
    docs  = _doc_completeness()
    infra = _infrastructure()

    pct = (
        mr[0] * WEIGHT_MARKET_READINESS
        + tests[0] * WEIGHT_TEST_COVERAGE
        + docs[0] * WEIGHT_DOC_COMPLETENESS
        + infra[0] * WEIGHT_INFRASTRUCTURE
    ) * 100
    section = _build_section(pct, mr, tests, docs, infra)

    if MARKER_START in readme and MARKER_END in readme:
        readme = re.sub(
            re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
            section,
            readme,
            flags=re.DOTALL,
        )
    else:
        # First run: inject after the opening heading line
        readme = re.sub(
            r"(# [^\n]+\n)",
            r"\1\n" + section + "\n",
            readme,
            count=1,
        )

    README_PATH.write_text(readme, encoding="utf-8")
    print(f"[completion] {pct:.0f}%  — README.md updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
