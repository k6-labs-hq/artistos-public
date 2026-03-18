from __future__ import annotations

from datetime import datetime, timezone

from tests.conftest import TestSession
from XR7.models.xr7_royalty import XR7RoyaltyStatement, XR7RoyaltyStatementLine, XR7UsageEvent, XR7Work, XR7SourceCategory, XR7MatchMethod
from XR7.services.xr7_crypto_vault import open_sealed, seal
from XR7.services.xr7_pipelines import build_royalty_gap_report, run_reconciliation_pipeline


def test_xr7_vault_round_trip():
    token = "secret-access-token-value"
    sealed = seal(token)
    opened = open_sealed(sealed)
    assert opened == token


def test_xr7_reconciliation_and_gap_detection():
    db = TestSession()
    try:
        tenant_id = "default"
        artist_id = "artist-xr7-test"

        work = XR7Work(
            tenant_id=tenant_id,
            artist_id=artist_id,
            title="Known Song",
            iswc="T-123.456.789-0",
        )
        db.add(work)
        db.flush()

        stmt = XR7RoyaltyStatement(
            tenant_id=tenant_id,
            artist_id=artist_id,
            source_system="mlc",
            gross_amount=10.0,
            net_amount=10.0,
            line_count=1,
            parse_status="processed",
        )
        db.add(stmt)
        db.flush()

        line = XR7RoyaltyStatementLine(
            statement_id=stmt.id,
            row_index=0,
            raw_work_title="Completely Different Title",
            amount=10.0,
            units=5.0,
            currency="USD",
        )
        db.add(line)

        usage = XR7UsageEvent(
            tenant_id=tenant_id,
            artist_id=artist_id,
            platform="spotify",
            event_type="stream",
            event_timestamp=datetime.now(timezone.utc),
            territory="US",
            channel="api",
            units=100.0,
            match_method=XR7MatchMethod.API,
            confidence_score=0.95,
            monetization_estimate=100.0,
            source_category=XR7SourceCategory.API,
        )
        db.add(usage)
        db.commit()

        out = run_reconciliation_pipeline(
            db,
            tenant_id=tenant_id,
            artist_id=artist_id,
            min_auto_match=0.95,
        )
        assert out.pipeline == "reconciliation"
        assert out.details["unmatched_created"] >= 1

        gap = build_royalty_gap_report(db, tenant_id=tenant_id, artist_id=artist_id)
        assert gap.total_gap > 0
        assert len(gap.rows) >= 1
    finally:
        db.close()
