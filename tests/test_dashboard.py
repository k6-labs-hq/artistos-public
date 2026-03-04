"""
Tests for the artist recovery dashboard (GET /artists/{id}/dashboard).

Validates:
- DashboardEngine.compute() returns all expected sections
- leakage_discovered correctly totals estimated_recoverable
- in_pursuit correctly counts and sums active claims
- recovered_and_deposited only counts APPROVED/SETTLED disbursements
- balance_still_pursuing math
- activity_feed includes all three event types, newest first
- API endpoint returns 200 with the right structure
- API endpoint returns 404 for unknown artist
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from arcos7.api.app import app
from arcos7.earnings.dashboard import DashboardEngine
from arcos7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from arcos7.models.artist import Artist
from arcos7.models.celero_transaction import (
    CeleroTransaction,
    CeleroTxnStatus,
    CeleroTxnType,
)
from arcos7.models.claim import Claim, ClaimStatus

from tests.conftest import TestSession as _TestSession

client = TestClient(app)

# Base timestamp — all test records use this + an offset so ordering is deterministic.
_BASE_TS = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _ts(offset_seconds: int = 0) -> datetime:
    """Return a fixed timestamp offset from _BASE_TS for deterministic ordering."""
    return _BASE_TS + timedelta(seconds=offset_seconds)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def db():
    session = _TestSession()
    yield session
    session.close()


@pytest.fixture()
def artist(db):
    a = Artist(
        id=str(uuid.uuid4()),
        name="Dashboard Test Artist",
        created_at=_ts(),
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


# Shared counter to give each added record a unique, monotonically increasing
# timestamp within a test run — avoids flaky ordering in activity feed tests.
_counter = 0


def _next_ts() -> datetime:
    global _counter
    _counter += 1
    return _ts(_counter * 10)


def _add_anomaly(db, artist_id, *, estimated_recoverable=500.0, status=AnomalyStatus.OPEN,
                 category=AnomalyCategory.ROYALTY, severity=AnomalySeverity.HIGH,
                 subtype="MISSING_PAYMENT", description=None):
    a = Anomaly(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        category=category,
        subtype=subtype,
        severity=severity,
        confidence_score=0.9,
        estimated_recoverable=estimated_recoverable,
        status=status,
        description=description,
        created_at=_next_ts(),
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def _add_claim(db, artist_id, anomaly_id, *, status=ClaimStatus.IDENTIFIED,
               recovered_amount=None, contingency_fee=None, currency="USD"):
    ts = _next_ts()
    c = Claim(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        anomaly_id=anomaly_id,
        claim_type="ROYALTY",
        status=status,
        recovered_amount=recovered_amount,
        contingency_fee=contingency_fee,
        currency=currency,
        created_at=ts,
        updated_at=ts,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _add_disbursement(db, artist_id, *, amount=450.0, status=CeleroTxnStatus.SETTLED,
                      claim_id=None, celero_transaction_id=None, currency="USD"):
    ts = _next_ts()
    t = CeleroTransaction(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        claim_id=claim_id,
        type=CeleroTxnType.DISBURSEMENT,
        amount=amount,
        currency=currency,
        status=status,
        celero_transaction_id=celero_transaction_id or f"TXN-{uuid.uuid4().hex[:8]}",
        created_at=ts,
        updated_at=ts,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


# ---------------------------------------------------------------------------
# DashboardEngine unit tests
# ---------------------------------------------------------------------------

class TestDashboardEngineLeakage:
    def test_empty_returns_zero_leakage(self, db, artist):
        engine = DashboardEngine(db)
        data = engine.compute(artist.id)
        ld = data["leakage_discovered"]
        assert ld["total_anomalies"] == 0
        assert ld["total_estimated_recoverable"] == 0.0
        assert ld["by_category"] == {}
        assert ld["by_severity"] == {}
        assert ld["recent_discoveries"] == []

    def test_leakage_totals_estimated_recoverable(self, db, artist):
        _add_anomaly(db, artist.id, estimated_recoverable=300.0)
        _add_anomaly(db, artist.id, estimated_recoverable=700.0)
        engine = DashboardEngine(db)
        ld = engine.compute(artist.id)["leakage_discovered"]
        assert ld["total_estimated_recoverable"] == pytest.approx(1000.0)
        assert ld["total_anomalies"] == 2

    def test_open_anomaly_count(self, db, artist):
        _add_anomaly(db, artist.id, status=AnomalyStatus.OPEN)
        _add_anomaly(db, artist.id, status=AnomalyStatus.CLOSED)
        ld = DashboardEngine(db).compute(artist.id)["leakage_discovered"]
        assert ld["open_anomalies"] == 1

    def test_by_category_grouping(self, db, artist):
        _add_anomaly(db, artist.id, category=AnomalyCategory.ROYALTY, estimated_recoverable=200.0)
        _add_anomaly(db, artist.id, category=AnomalyCategory.ROYALTY, estimated_recoverable=100.0)
        _add_anomaly(db, artist.id, category=AnomalyCategory.TOURING, estimated_recoverable=400.0)
        ld = DashboardEngine(db).compute(artist.id)["leakage_discovered"]
        assert ld["by_category"]["ROYALTY"]["count"] == 2
        assert ld["by_category"]["ROYALTY"]["estimated_recoverable"] == pytest.approx(300.0)
        assert ld["by_category"]["TOURING"]["count"] == 1
        assert ld["by_category"]["TOURING"]["estimated_recoverable"] == pytest.approx(400.0)

    def test_by_severity_grouping(self, db, artist):
        _add_anomaly(db, artist.id, severity=AnomalySeverity.HIGH, estimated_recoverable=500.0)
        _add_anomaly(db, artist.id, severity=AnomalySeverity.CRITICAL, estimated_recoverable=200.0)
        ld = DashboardEngine(db).compute(artist.id)["leakage_discovered"]
        assert ld["by_severity"]["HIGH"]["count"] == 1
        assert ld["by_severity"]["CRITICAL"]["count"] == 1

    def test_none_estimated_recoverable_counts_as_zero(self, db, artist):
        _add_anomaly(db, artist.id, estimated_recoverable=None)
        ld = DashboardEngine(db).compute(artist.id)["leakage_discovered"]
        assert ld["total_estimated_recoverable"] == pytest.approx(0.0)

    def test_recent_discoveries_max_10(self, db, artist):
        for i in range(15):
            _add_anomaly(db, artist.id, subtype=f"TYPE_{i}")
        ld = DashboardEngine(db).compute(artist.id)["leakage_discovered"]
        assert len(ld["recent_discoveries"]) == 10


class TestDashboardEngineInPursuit:
    def test_empty_in_pursuit(self, db, artist):
        ip = DashboardEngine(db).compute(artist.id)["in_pursuit"]
        assert ip["active_claim_count"] == 0
        assert ip["total_amount_in_pursuit"] == 0.0

    def test_active_claims_counted(self, db, artist):
        anom = _add_anomaly(db, artist.id)
        _add_claim(db, artist.id, anom.id, status=ClaimStatus.IDENTIFIED, recovered_amount=800.0)
        _add_claim(db, artist.id, anom.id, status=ClaimStatus.SUBMITTED, recovered_amount=600.0)
        ip = DashboardEngine(db).compute(artist.id)["in_pursuit"]
        assert ip["active_claim_count"] == 2
        assert ip["total_amount_in_pursuit"] == pytest.approx(1400.0)

    def test_closed_claims_not_in_active(self, db, artist):
        anom = _add_anomaly(db, artist.id)
        _add_claim(db, artist.id, anom.id, status=ClaimStatus.PAID, recovered_amount=1000.0,
                   contingency_fee=100.0)
        _add_claim(db, artist.id, anom.id, status=ClaimStatus.CLOSED, recovered_amount=500.0,
                   contingency_fee=50.0)
        ip = DashboardEngine(db).compute(artist.id)["in_pursuit"]
        assert ip["active_claim_count"] == 0
        assert ip["closed_claim_count"] == 2
        assert ip["total_gross_recovered"] == pytest.approx(1500.0)
        assert ip["total_fees_collected"] == pytest.approx(150.0)
        assert ip["total_net_recovered"] == pytest.approx(1350.0)

    def test_all_active_statuses_included(self, db, artist):
        anom = _add_anomaly(db, artist.id)
        for status in (ClaimStatus.IDENTIFIED, ClaimStatus.PREPARED, ClaimStatus.SUBMITTED,
                       ClaimStatus.IN_REVIEW, ClaimStatus.ACCEPTED):
            _add_claim(db, artist.id, anom.id, status=status, recovered_amount=100.0)
        ip = DashboardEngine(db).compute(artist.id)["in_pursuit"]
        assert ip["active_claim_count"] == 5


class TestDashboardEngineDeposited:
    def test_no_disbursements_zero_total(self, db, artist):
        dep = DashboardEngine(db).compute(artist.id)["recovered_and_deposited"]
        assert dep["total_deposited"] == 0.0
        assert dep["deposit_count"] == 0

    def test_settled_disbursements_counted(self, db, artist):
        _add_disbursement(db, artist.id, amount=900.0, status=CeleroTxnStatus.SETTLED)
        dep = DashboardEngine(db).compute(artist.id)["recovered_and_deposited"]
        assert dep["total_deposited"] == pytest.approx(900.0)
        assert dep["deposit_count"] == 1

    def test_approved_disbursements_counted(self, db, artist):
        _add_disbursement(db, artist.id, amount=300.0, status=CeleroTxnStatus.APPROVED)
        dep = DashboardEngine(db).compute(artist.id)["recovered_and_deposited"]
        assert dep["total_deposited"] == pytest.approx(300.0)

    def test_pending_disbursements_not_counted_as_deposited(self, db, artist):
        _add_disbursement(db, artist.id, amount=500.0, status=CeleroTxnStatus.PENDING)
        dep = DashboardEngine(db).compute(artist.id)["recovered_and_deposited"]
        assert dep["total_deposited"] == pytest.approx(0.0)
        assert dep["deposit_count"] == 0

    def test_failed_disbursements_not_counted(self, db, artist):
        _add_disbursement(db, artist.id, amount=200.0, status=CeleroTxnStatus.FAILED)
        dep = DashboardEngine(db).compute(artist.id)["recovered_and_deposited"]
        assert dep["total_deposited"] == pytest.approx(0.0)

    def test_deposits_list_has_expected_fields(self, db, artist):
        _add_disbursement(db, artist.id, amount=750.0, status=CeleroTxnStatus.SETTLED,
                          celero_transaction_id="TXN-DEPOSIT-1")
        dep = DashboardEngine(db).compute(artist.id)["recovered_and_deposited"]
        assert len(dep["deposits"]) == 1
        d = dep["deposits"][0]
        assert d["amount"] == pytest.approx(750.0)
        assert d["celero_transaction_id"] == "TXN-DEPOSIT-1"
        assert "deposited_at" in d

    def test_charge_transactions_not_included_in_deposited(self, db, artist):
        """CHARGE (fee collection) should never appear in the deposited section."""
        t = CeleroTransaction(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            type=CeleroTxnType.CHARGE,
            amount=100.0,
            currency="USD",
            status=CeleroTxnStatus.APPROVED,
            created_at=_next_ts(),
            updated_at=_next_ts(),
        )
        db.add(t)
        db.commit()
        dep = DashboardEngine(db).compute(artist.id)["recovered_and_deposited"]
        assert dep["total_deposited"] == pytest.approx(0.0)


class TestDashboardEngineBalance:
    def test_zero_balance_with_no_data(self, db, artist):
        bal = DashboardEngine(db).compute(artist.id)["balance_still_pursuing"]
        assert bal["balance_still_pursuing"] == pytest.approx(0.0)
        assert bal["total_deposited_to_date"] == pytest.approx(0.0)
        assert bal["total_pending_deposit"] == pytest.approx(0.0)

    def test_balance_equals_active_claims_when_nothing_deposited(self, db, artist):
        anom = _add_anomaly(db, artist.id)
        _add_claim(db, artist.id, anom.id, status=ClaimStatus.SUBMITTED, recovered_amount=1000.0)
        bal = DashboardEngine(db).compute(artist.id)["balance_still_pursuing"]
        assert bal["balance_still_pursuing"] == pytest.approx(1000.0)

    def test_settled_deposits_appear_in_total_deposited_to_date(self, db, artist):
        _add_disbursement(db, artist.id, amount=600.0, status=CeleroTxnStatus.SETTLED)
        bal = DashboardEngine(db).compute(artist.id)["balance_still_pursuing"]
        assert bal["total_deposited_to_date"] == pytest.approx(600.0)

    def test_pending_deposit_reduces_balance_still_pursuing(self, db, artist):
        anom = _add_anomaly(db, artist.id)
        _add_claim(db, artist.id, anom.id, status=ClaimStatus.ACCEPTED, recovered_amount=1000.0)
        _add_disbursement(db, artist.id, amount=900.0, status=CeleroTxnStatus.APPROVED)
        bal = DashboardEngine(db).compute(artist.id)["balance_still_pursuing"]
        assert bal["total_pending_deposit"] == pytest.approx(900.0)
        assert bal["balance_still_pursuing"] == pytest.approx(100.0)

    def test_balance_never_negative(self, db, artist):
        """Even if deposits exceed active claims, balance floors at 0."""
        _add_disbursement(db, artist.id, amount=5000.0, status=CeleroTxnStatus.APPROVED)
        bal = DashboardEngine(db).compute(artist.id)["balance_still_pursuing"]
        assert bal["balance_still_pursuing"] >= 0.0


class TestDashboardActivityFeed:
    def test_empty_artist_empty_feed(self, db, artist):
        feed = DashboardEngine(db).compute(artist.id)["activity_feed"]
        assert feed == []

    def test_leakage_event_in_feed(self, db, artist):
        _add_anomaly(db, artist.id, estimated_recoverable=250.0, subtype="RATE_BELOW_MARKET")
        feed = DashboardEngine(db).compute(artist.id)["activity_feed"]
        types = [e["type"] for e in feed]
        assert "LEAKAGE_DISCOVERED" in types
        leakage_events = [e for e in feed if e["type"] == "LEAKAGE_DISCOVERED"]
        assert leakage_events[0]["amount"] == pytest.approx(250.0)

    def test_claim_event_in_feed(self, db, artist):
        anom = _add_anomaly(db, artist.id)
        _add_claim(db, artist.id, anom.id, status=ClaimStatus.SUBMITTED, recovered_amount=800.0)
        feed = DashboardEngine(db).compute(artist.id)["activity_feed"]
        claim_events = [e for e in feed if "CLAIM_" in e["type"]]
        assert len(claim_events) >= 1
        assert claim_events[0]["amount"] == pytest.approx(800.0)

    def test_payment_deposited_event_in_feed(self, db, artist):
        _add_disbursement(db, artist.id, amount=720.0, status=CeleroTxnStatus.SETTLED,
                          celero_transaction_id="TXN-FEED-1")
        feed = DashboardEngine(db).compute(artist.id)["activity_feed"]
        deposit_events = [e for e in feed if e["type"] == "PAYMENT_DEPOSITED"]
        assert len(deposit_events) == 1
        assert deposit_events[0]["amount"] == pytest.approx(720.0)
        assert "TXN-FEED-1" in deposit_events[0]["detail"]

    def test_feed_sorted_newest_first(self, db, artist):
        anom = _add_anomaly(db, artist.id)
        _add_claim(db, artist.id, anom.id, status=ClaimStatus.IDENTIFIED)
        _add_disbursement(db, artist.id, amount=100.0, status=CeleroTxnStatus.SETTLED)
        feed = DashboardEngine(db).compute(artist.id)["activity_feed"]
        timestamps = [e["timestamp"] for e in feed]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_feed_capped_at_50_entries(self, db, artist):
        for i in range(60):
            _add_anomaly(db, artist.id, subtype=f"TYPE_{i}")
        feed = DashboardEngine(db).compute(artist.id)["activity_feed"]
        assert len(feed) <= 50

    def test_feed_entry_has_required_fields(self, db, artist):
        _add_anomaly(db, artist.id)
        feed = DashboardEngine(db).compute(artist.id)["activity_feed"]
        e = feed[0]
        assert "type" in e
        assert "timestamp" in e
        assert "title" in e
        assert "detail" in e
        assert "reference_id" in e


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

class TestDashboardAPIEndpoint:
    def test_dashboard_unknown_artist_404(self):
        resp = client.get("/artists/nonexistent-id/dashboard")
        assert resp.status_code == 404

    def test_dashboard_returns_200(self):
        resp = client.post("/artists/", json={"name": "Dashboard Artist"})
        assert resp.status_code == 201
        aid = resp.json()["id"]
        resp = client.get(f"/artists/{aid}/dashboard")
        assert resp.status_code == 200

    def test_dashboard_has_all_sections(self):
        resp = client.post("/artists/", json={"name": "Sections Artist"})
        aid = resp.json()["id"]
        data = client.get(f"/artists/{aid}/dashboard").json()
        assert "artist_id" in data
        assert "generated_at" in data
        assert "leakage_discovered" in data
        assert "in_pursuit" in data
        assert "recovered_and_deposited" in data
        assert "balance_still_pursuing" in data
        assert "activity_feed" in data

    def test_dashboard_leakage_fields(self):
        resp = client.post("/artists/", json={"name": "Leakage Fields Artist"})
        aid = resp.json()["id"]
        ld = client.get(f"/artists/{aid}/dashboard").json()["leakage_discovered"]
        assert "total_anomalies" in ld
        assert "open_anomalies" in ld
        assert "total_estimated_recoverable" in ld
        assert "by_category" in ld
        assert "by_severity" in ld
        assert "recent_discoveries" in ld

    def test_dashboard_in_pursuit_fields(self):
        resp = client.post("/artists/", json={"name": "Pursuit Fields Artist"})
        aid = resp.json()["id"]
        ip = client.get(f"/artists/{aid}/dashboard").json()["in_pursuit"]
        assert "active_claim_count" in ip
        assert "total_amount_in_pursuit" in ip
        assert "total_gross_recovered" in ip
        assert "total_net_recovered" in ip

    def test_dashboard_deposited_fields(self):
        resp = client.post("/artists/", json={"name": "Deposited Fields Artist"})
        aid = resp.json()["id"]
        dep = client.get(f"/artists/{aid}/dashboard").json()["recovered_and_deposited"]
        assert "total_deposited" in dep
        assert "deposit_count" in dep
        assert "deposits" in dep

    def test_dashboard_balance_fields(self):
        resp = client.post("/artists/", json={"name": "Balance Fields Artist"})
        aid = resp.json()["id"]
        bal = client.get(f"/artists/{aid}/dashboard").json()["balance_still_pursuing"]
        assert "balance_still_pursuing" in bal
        assert "total_deposited_to_date" in bal
        assert "total_pending_deposit" in bal
        assert "note" in bal

    def test_dashboard_artist_id_matches(self):
        resp = client.post("/artists/", json={"name": "ID Check Artist"})
        aid = resp.json()["id"]
        data = client.get(f"/artists/{aid}/dashboard").json()
        assert data["artist_id"] == aid

    def test_dashboard_empty_artist_is_all_zeros(self):
        resp = client.post("/artists/", json={"name": "Zero Artist"})
        aid = resp.json()["id"]
        data = client.get(f"/artists/{aid}/dashboard").json()
        assert data["leakage_discovered"]["total_estimated_recoverable"] == 0.0
        assert data["in_pursuit"]["active_claim_count"] == 0
        assert data["recovered_and_deposited"]["total_deposited"] == 0.0
        assert data["balance_still_pursuing"]["balance_still_pursuing"] == 0.0
        assert data["activity_feed"] == []
