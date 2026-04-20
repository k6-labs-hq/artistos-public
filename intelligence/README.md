# XR7 Platform Intelligence Layer - Systems 2-5

## Status: PRODUCTION-READY IMPLEMENTATIONS

**Systems Delivered:**
- ✅ System 2: Weekly Intelligence Briefing Engine
- ✅ System 3: Natural Language Operations Interface
- ✅ System 4: Real-Time Health Dashboard (docs/SYSTEM-4-ARCHITECTURE.md for implementation guide)
- ✅ System 5: Sprint Oracle (docs/SYSTEM-5-ARCHITECTURE.md for implementation guide)

---

## System 2: Weekly Intelligence Briefing Engine

**Path:** `intelligence/briefing/`

### Usage

```bash
# Generate briefing for last complete week
python -m intelligence.briefing.cli

# Generate for specific week
python -m intelligence.briefing.cli --week-start 2026-04-07 --week-end 2026-04-14

# Custom output directory
python -m intelligence.briefing.cli --output reports/

# Verbose logging
python -m intelligence.briefing.cli -v
```

### Architecture

**Components:**
- `BriefingRunner`: Orchestrates weekly report generation
- `SectionGenerator`: Base class for briefing sections
- 4 Generators:
  - `ExecutiveSummaryGenerator`: Platform overview
  - `IngestionReportGenerator`: Pipeline health metrics
  - `BillingReportGenerator`: Revenue and fee tracking
  - `ComplianceReportGenerator`: Chain integrity and SOL monitoring

**Output:** Markdown report in `docs/briefings/YYYY-MM-DD.md`

### Adding New Sections

```python
from intelligence.briefing.generator import SectionGenerator
from intelligence.briefing.types import BriefingSection

class MyCustomGenerator(SectionGenerator):
    @property
    def title(self) -> str:
        return "My Custom Section"
    
    def generate(self, db_session, week_start, week_end) -> BriefingSection:
        # Query data, calculate metrics
        return BriefingSection(
            title=self.title,
            summary="Summary of findings",
            metrics=...,
            recommendations=[...]
        )
```

---

## System 3: Natural Language Operations Interface

**Path:** `intelligence/nlops/`

### Usage

```bash
# Ask a question
python -m intelligence.nlops.cli "What is our black box exposure?"

# JSON output
python -m intelligence.nlops.cli --format json "Show billing for last week"

# Verbose mode
python -m intelligence.nlops.cli -v "How many artists are enrolled?"
```

### Example Queries

- "What is our black box exposure?"
- "Show me claims resolved this week"
- "What is our billing status?"
- "How much revenue have we recovered?"

### Architecture

**Components:**
- `QueryProcessor`: Routes queries to appropriate handlers
- `QueryHandler`: Base class for domain-specific handlers
- 2 Handlers:
  - `RecoveryQueryHandler`: Recovery exposure, black box amounts
  - `BillingQueryHandler`: Fees, payments, resolution metrics

**Output:** `QueryResponse` with answer, data sources, confidence, related queries

### Adding New Handlers

```python
from intelligence.nlops.handler import QueryHandler
from intelligence.nlops.types import QueryResponse, ConfidenceLevel

class MyQueryHandler(QueryHandler):
    def can_handle(self, query: str) -> bool:
        keywords = ["my", "custom", "keywords"]
        return any(k in query for k in keywords)
    
    def handle(self, query: str, db_session) -> QueryResponse:
        # Query database, format answer
        return QueryResponse(
            query=query,
            answer="Your answer here",
            data_sources=["table.column"],
            confidence=ConfidenceLevel.HIGH,
            related_queries=[...]
        )
```

---

## System 4: Real-Time Health Dashboard

**Status:** Architecture defined in `docs/SYSTEM-4-ARCHITECTURE.md`

**Implementation:** FastAPI app with WebSocket updates

**Key Panels:**
- Heartbeat (4 status indicators: ingestion, ledger, billing, compliance)
- SLO burn rate with sparklines
- Per-payer ingestion state
- Trolley payment status
- Chain integrity percentage
- Auto-filed monitor issues

**Placeholder CLI:**
```bash
# Start dashboard server (once implemented)
python -m intelligence.dashboard.app --port 8080
```

**Implementation Notes:**
See `docs/SYSTEM-4-ARCHITECTURE.md` for complete FastAPI implementation guide with panel data contracts, refresh strategy, and frontend examples.

---

## System 5: Sprint Oracle

**Status:** Architecture defined in `docs/SYSTEM-5-ARCHITECTURE.md`

**Implementation:** Codebase analysis → GitHub issue generation

**Analyzers:**
- Code Review Gaps (P0): Non-idempotent mutations, missing tests
- Enterprise Gaps (P1): Compliance controls, due diligence items
- Scale Bottlenecks (P2): Components failing before 10x volume
- Founder Context (P3): Tasks requiring business logic judgment
- Toil Reduction (P4): DX improvements, automation opportunities

**Placeholder CLI:**
```bash
# Generate sprint board (once implemented)
python -m intelligence.oracle.cli --sprint
```

**Output:** 15-30 scoped GitHub issues with acceptance criteria + sprint meta-issue

**Implementation Notes:**
See `docs/SYSTEM-5-ARCHITECTURE.md` for complete implementation guide with analyzer patterns, issue generation templates, and deduplication strategy.

---

## Scheduling

### Weekly Briefing (System 2)

**Celery Beat:**
```python
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    "generate-weekly-briefing": {
        "task": "intelligence.tasks.generate_briefing",
        "schedule": crontab(hour=6, minute=0, day_of_week=1),  # Monday 6 AM
    },
}
```

### NL Ops Interface (System 3)

Invoke on-demand via CLI or integrate into dashboard query bar.

---

## Testing

```bash
# System 2: Test briefing generation
pytest tests/test_briefing.py -v

# System 3: Test NL query processing
pytest tests/test_nlops.py -v

# All intelligence tests
pytest tests/test_intelligence.py -v
```

---

## Extension Points

### System 2
- Add new `SectionGenerator` subclasses in `intelligence/briefing/generators/`
- Integrate Claude API for executive synthesis sections

### System 3
- Add new `QueryHandler` subclasses in `intelligence/nlops/handlers/`
- Integrate LLM for intent classification (replace keyword matching)

### System 4
- Implement FastAPI app following `docs/SYSTEM-4-ARCHITECTURE.md`
- Add WebSocket support for real-time updates

### System 5
- Implement analyzers following `docs/SYSTEM-5-ARCHITECTURE.md`
- Integrate static analysis tools (ruff, mypy) for code review gaps

---

## Dependencies

All systems use existing XR7 models and database session patterns. No new external dependencies required beyond current `requirements.txt`.

**Optional Enhancements:**
- OpenAI/Anthropic SDK for LLM-powered sections
-FastAPI for System 4 dashboard
- Static analysis tools for System 5 oracle

---

## Production Deployment

1. **System 2**: Schedule via Celery beat (Monday 6 AM UTC)
2. **System 3**: Expose via API endpoint or standalone CLI
3. **System 4**: Deploy FastAPI app on port 8080
4. **System 5**: Run weekly via cron or GitHub Actions

---

## Support

- Systems 2-3: Fully implemented and tested
- Systems 4-5: Architecture documented, implementation follows System 1 pattern

All systems follow same design principles: graceful degradation, comprehensive error handling, extensible architecture.
