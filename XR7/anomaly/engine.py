from sqlalchemy.orm import Session

from XR7.anomaly.rules import platforms, royalties, touring
from XR7.anomaly.rules.metadata_rules import run_metadata_rules
from XR7.anomaly.rules.transparent_rules import run_transparent_rules
from XR7.anomaly.rules.work_level_rules import run_work_level_rules, work_level_rules_enabled
from XR7.earnings.engine import EarningsEngine
from XR7.graph.rights_graph import RightsGraph
from XR7.ingestion.metadata_sources.resolver import build_default_resolver
from XR7.models.contract import Contract
from XR7.models.event import Event
from XR7.models.payment import Payment
from XR7.models.work import Work
from XR7.services.isrc_resolution_cache import DbCachingResolver


class AnomalyEngine:
    def __init__(
        self,
        earnings_engine: EarningsEngine,
        rights_graph: RightsGraph,
        metadata_resolver=None,
    ):
        self.earnings_engine = earnings_engine
        self.rights_graph = rights_graph
        self.metadata_resolver = metadata_resolver

    @staticmethod
    def _enum_value(value):
        return getattr(value, "value", value)

    def _events_to_dicts(self, events) -> list[dict]:
        return [
            {
                "id": e.id,
                "event_type": self._enum_value(e.event_type),
                "work_id": e.work_id,
                "work_title": getattr(e, "work_title", None),
                "platform": getattr(e, "platform", None),
                "quantity": e.quantity,
                "unit_value": e.unit_value,
                "currency": e.currency,
                "territory": e.territory,
                "timestamp": e.timestamp,
                "share_pct": getattr(e, "share_pct", None),
            }
            for e in events
        ]

    def _payments_to_dicts(self, payments) -> list[dict]:
        return [
            {
                "id": p.id,
                "payment_type": self._enum_value(p.payment_type),
                "amount": p.amount,
                "currency": p.currency,
                "source": p.source,
                "received_at": p.received_at,
                # period_start/period_end describe the reporting period the
                # payment covers (e.g. 2026-02-01..2026-02-28 for a Feb
                # statement). received_at is the ingestion timestamp — using
                # it for monthly bucketing is wrong because uploads always
                # happen after the period closes. See #208.
                "period_start": getattr(p, "period_start", None),
                "period_end": getattr(p, "period_end", None),
            }
            for p in payments
        ]

    def _contracts_to_dicts(self, contracts) -> list[dict]:
        return [
            {
                "id": c.id,
                "contract_type": self._enum_value(c.contract_type),
                "terms": c.terms,
                "territory": c.territory,
            }
            for c in contracts
        ]

    def detect_all(self, artist_id: str, db_session: Session) -> list[dict]:
        return self.detect_rule_anomalies(artist_id, db_session)

    def detect_royalty_anomalies(self, artist_id: str, db_session: Session) -> list[dict]:
        events = self._events_to_dicts(
            db_session.query(Event).filter(Event.artist_id == artist_id).all()
        )
        payments = self._payments_to_dicts(
            db_session.query(Payment).filter(Payment.artist_id == artist_id).all()
        )
        contracts = self._contracts_to_dicts(
            db_session.query(Contract).filter(Contract.artist_id == artist_id).all()
        )
        result = []
        result.extend(royalties.check_missing_royalty_payments(artist_id, events, payments))
        result.extend(royalties.check_incorrect_rates(artist_id, payments, contracts))
        result.extend(royalties.check_foreign_royalties_not_remitted(artist_id, events, payments))
        return result

    def detect_touring_anomalies(self, artist_id: str, db_session: Session) -> list[dict]:
        events = self._events_to_dicts(
            db_session.query(Event).filter(Event.artist_id == artist_id).all()
        )
        payments = self._payments_to_dicts(
            db_session.query(Payment).filter(Payment.artist_id == artist_id).all()
        )
        contracts = self._contracts_to_dicts(
            db_session.query(Contract).filter(Contract.artist_id == artist_id).all()
        )
        result = []
        result.extend(touring.check_missing_guarantee(artist_id, events, payments))
        result.extend(touring.check_settlement_discrepancy(artist_id, events, payments, contracts))
        return result

    def detect_platform_anomalies(self, artist_id: str, db_session: Session) -> list[dict]:
        events = self._events_to_dicts(
            db_session.query(Event).filter(Event.artist_id == artist_id).all()
        )
        payments = self._payments_to_dicts(
            db_session.query(Payment).filter(Payment.artist_id == artist_id).all()
        )
        result = []
        result.extend(platforms.check_low_stream_rates(artist_id, events, payments))
        result.extend(platforms.check_missing_platform_payments(artist_id, events, payments))
        return result

    def detect_rule_anomalies(self, artist_id: str, db_session: Session) -> list[dict]:
        events = self._events_to_dicts(
            db_session.query(Event).filter(Event.artist_id == artist_id).all()
        )
        payments = self._payments_to_dicts(
            db_session.query(Payment).filter(Payment.artist_id == artist_id).all()
        )
        contracts = self._contracts_to_dicts(
            db_session.query(Contract).filter(Contract.artist_id == artist_id).all()
        )
        findings = run_transparent_rules(
            artist_id, events=events, payments=payments, contracts=contracts
        )
        findings.extend(self._detect_metadata_anomalies(artist_id, events, db_session))
        if work_level_rules_enabled():
            findings.extend(run_work_level_rules(artist_id, events))
        return findings

    def _detect_metadata_anomalies(
        self, artist_id: str, events: list[dict], db_session: Session
    ) -> list[dict]:
        """ISRC/ISWC cross-check against public metadata. No-op unless a resolver is
        injected or MUSICBRAINZ_USER_AGENT is set, so default behaviour (and tests)
        never touch the network."""
        resolver = self.metadata_resolver or build_default_resolver()
        if resolver is None:
            return []
        if self.metadata_resolver is None:
            # Env-configured live source: persist answers so re-runs and other
            # workers don't re-hit MusicBrainz. Injected resolvers are used as-is.
            resolver = DbCachingResolver(db_session, resolver)
        works = [
            {"id": w.id, "title": w.title, "isrc": w.isrc, "iswc": w.iswc}
            for w in db_session.query(Work)
            .filter(Work.artist_id == artist_id, Work.deleted_at.is_(None))
            .all()
        ]
        return run_metadata_rules(artist_id, works, events, resolver)
