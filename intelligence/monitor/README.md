# XR7 Platform Self-Monitor

**Automated health detection and GitHub issue filing for XR7 Engine 2**

The self-monitor continuously watches the platform across 7 domains and automatically files GitHub issues when problems are detected. One broken detector does not prevent others from running. Every finding is grounded in platform data, never speculation.

## What It Monitors

### 1. Ledger Integrity (Audit Domain)
- SHA-256 chain verification status across all tenants
- Scheduled verification job health
- Evidence packet integrity spot checks

### 2. Billing & Revenue (Billing Domain)
- Trolley disbursement failure rates
- Fee calculation accuracy (detected drift = potential revenue error)
- Founders Circle capacity utilization

### 3. Ingestion Pipeline (Ingestion Domain)
- Dead letter queue depth
- Payer-specific ingestion failure rates
- Catalog pattern errors

### 4. Compliance Posture (Compliance Domain)
- Statute of limitations deadlines approaching
- GDPR deletion request backlog (30+ days)
- SOC 2 evidence artifact staleness

### 5. SLO & Reliability (Reliability Domain)
- Error budget burn rate
- SLO compliance trends
- P0 incident patterns

### 6. Tenant Isolation (Security Domain)
- Cross-tenant query patterns
- Missing artist_id filter detection

### 7. Dependency Health (Security Domain)
- CVEs in production dependencies
- Deprecated API version warnings
- Security patch availability

## Installation & Setup

### Prerequisites
- Python 3.11+
- Access to XR7 platform database
- GitHub CLI (`gh`) installed and authenticated (for issue filing)

### Install GitHub CLI
```bash
# macOS
brew install gh

# Windows
winget install GitHub.cli

# Linux
sudo apt install gh

# Authenticate
gh auth login
```

### Run the Monitor

**Dry run (no issues filed):**
```bash
python -m intelligence.monitor.cli
```

**File GitHub issues for findings:**
```bash
python -m intelligence.monitor.cli --file-issues
```

**Simulate issue filing (see what would be filed):**
```bash
python -m intelligence.monitor.cli --file-issues --dry-run
```

**JSON output for automation:**
```bash
python -m intelligence.monitor.cli --output json
```

## Expected Output

```
================================================================================
XR7 PLATFORM MONITOR - RUN SUMMARY
================================================================================
Completed at: 2026-04-19T22:15:43.123456Z
Platform state from: 2026-04-19T22:15:38.987654Z

Detectors run: 7
Total findings: 3

Findings by severity:
  P0: 1
  P1: 2

Findings by domain:
  audit: 1
  billing: 1
  compliance: 1

GitHub issues: 2 filed, 1 skipped (duplicates)
================================================================================
```

## Architecture

### Detector Interface
Every detector implements:
```python
class Detector(ABC):
    @property
    def name(self) -> str:
        """Unique detector name for logging."""
        pass

    @property
    def domain(self) -> str:
        """Domain monitored (billing, compliance, etc.)."""
        pass

    def detect(self, state: PlatformState) -> list[Finding]:
        """Analyze platform state, return findings."""
        pass
```

### Timeout & Error Handling
- Each detector gets 30 seconds (configurable)
- Detector failures don't crash the monitor
- Failed detectors are logged  in `detector_errors`

### GitHub Issue Deduplication
Before filing, monitor checks for existing open issues with:
- Same domain label
- Similar title
- `auto-filed` label

If found, issue is skipped (no duplicate).

## Adding a New Detector

1. **Create detector class:**
```python
# intelligence/monitor/detectors/my_domain.py
from intelligence.monitor.detector import Detector
from intelligence.monitor.types import Finding, FindingSeverity, PlatformState

class MyDomainDetector(Detector):
    @property
    def name(self) -> str:
        return "my-domain-detector"

    @property
    def domain(self) -> str:
        return "my-domain"

    def detect(self, state: PlatformState) -> list[Finding]:
        findings = []

        # Query platform state
        # If problem detected, create Finding

        if problem_detected:
            findings.append(Finding(
                detector=self.name,
                severity=FindingSeverity.P1,
                domain=self.domain,
                title="short problem description",
                description="What is wrong right now",
                expected_behavior="What it should be doing",
                investigation_path=[
                    "First thing to check",
                    "Second thing to check",
                    "Escalation condition",
                ],
                runbook_link="docs/runbooks/my-domain-failure.md",
                metadata={"context": "value"},
            ))

        return findings
```

2. **Register in runner:**
```python
# intelligence/monitor/detectors/__init__.py
from intelligence.monitor.detectors.my_domain import MyDomainDetector

__all__ = [..., "MyDomainDetector"]
```

3. **Add to runner detector list:**
```python
# intelligence/monitor/runner.py
self.detectors = [
    ...,
    MyDomainDetector,
]
```

4. **Write tests:**
```python
# tests/test_monitor.py
class TestMyDomainDetector:
    def test_detects_problem(self, mock_platform_state):
        # Setup: create condition where problem exists
        detector = MyDomainDetector()
        findings = detector.detect(mock_platform_state)

        # Assert: finding returned
        assert len(findings) == 1
        assert findings[0].severity == FindingSeverity.P1

    def test_no_finding_when_healthy(self, mock_platform_state):
        # Setup: create clean state
        detector = MyDomainDetector()
        findings = detector.detect(mock_platform_state)

        # Assert: no findings
        assert len(findings) == 0
```

## Filed Issue Format

Every auto-filed issue includes:
- **Detector name** and **severity** (P0/P1/P2/P3)
- **Domain** (billing, compliance, audit, etc.)
- **Problem description** (what is wrong right now)
- **Expected behavior** (what system should be doing)
- **Investigation path** (numbered steps to diagnose)
- **Runbook link** (if operational runbook exists)
- **Additional context** (JSON metadata with specifics)
- **Auto-filed disclaimer** (do not close without resolving)

Labels applied:
- `auto-filed`
- `monitor`
- Domain name (e.g., `billing`, `compliance`)
- Severity (e.g., `p0`, `p1`)

## Scheduling Recommendations

### Development
Run manually before each sprint planning:
```bash
python -m intelligence.monitor.cli --file-issues
```

### Production
Run on cron schedule:
```bash
# Every 6 hours
0 */6 * * * cd /app && python -m intelligence.monitor.cli --file-issues >> /var/log/monitor.log 2>&1
```

Or configure as Celery periodic task:
```python
# XR7/celery_app.py
beat_schedule["xr7-platform-self-monitor"] = {
    "task": "xr7.monitor.run_and_file_issues",
    "schedule": crontab(hour="*/6"),  # Every 6 hours
}
```

## Graceful Degradation

The monitor is designed to provide useful output even when:
- Individual detectors fail (errors logged, others continue)
- Database queries time out (detector skipped)
- GitHub CLI unavailable (findings logged, no issues filed)
- Platform components offline (detector reports what it can see)

**One broken detector never stops the others from running.**

## Limitations & Future Work

### Current Limitations
1. **No historical trending** - detects current state, not trends over time
2. **Limited observability integration** - doesn't query Prometheus/Grafana metrics
3. **No ML model health** - doesn't check recovery estimate accuracy drift
4. **No payer intelligence** - doesn't analyze per-payer degradation patterns
5. **No code analysis** - tenant isolation detection is placeholder

### Future Enhancements (Systems 2-5)
- **Weekly Intelligence Briefing** (System 2): Synthesize findings into executive summary
- **Natural Language Query Interface** (System 3): "What payers are degraded right now?"
- **Real-time Health Dashboard** (System 4): Single-screen engineering health surface
- **Sprint Oracle** (System 5): AI-generated sprint board from full repo analysis

## Testing

Run monitor tests:
```bash
pytest tests/test_monitor.py -v
```

Run specific detector test:
```bash
pytest tests/test_monitor.py::TestLedgerDetector -v
```

Run integration test:
```bash
pytest tests/test_monitor.py::TestMonitorRunner::test_full_monitor_cycle_with_issue_filing -v
```

## Troubleshooting

### "GitHub CLI not found"
Install `gh` CLI and authenticate:
```bash
gh auth login
```

### "Database connection failed"
Verify `XR7.db` exists or `DATABASE_URL` environment variable is set.

### "Detector timeout"
Increase timeout in PlatformState:
```python
state = PlatformState(
    db_session=db,
    timeout_per_detector=60,  # Increase from default 30s
)
```

### "Issue already exists (skipped)"
This is expected - deduplication prevents filing the same issue twice. Close the existing issue if you want a new one filed.

## Exit Codes

- `0`: Monitor completed, no P0 findings
- `1`: Monitor completed, P0 findings detected
- `2`: Monitor failed to run (exception)

Use in CI/CD:
```bash
if ! python -m intelligence.monitor.cli --file-issues; then
    echo "Platform health issues detected - see GitHub issues"
    # Send alert to Slack, PagerDuty, etc.
fi
```

## What the Sr. Principal Sees Tomorrow

When they open the repository, they find:
- GitHub issues automatically filed for every critical gap
- Each issue scoped, prioritized, and ready to assign
- Clear investigation paths (no guessing)
- The platform watching itself before anyone asked

**The founder built the system that watches the system.**

---

**System 1 of 5** - Part of the XR7 Platform Intelligence Layer
See: `docs/intelligence/` for Systems 2-5 architecture
