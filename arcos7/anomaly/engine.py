from sqlalchemy.orm import Session

from arcos7.anomaly.rules import royalties, touring, platforms
from arcos7.earnings.engine import EarningsEngine
from arcos7.graph.rights_graph import RightsGraph
from arcos7.models.contract import Contract
from arcos7.models.event import Event
from arcos7.models.payment import Payment


class AnomalyEngine:
    def __init__(self, earnings_engine: EarningsEngine, rights_graph: RightsGraph):
        self.earnings_engine = earnings_engine
        self.rights_graph = rights_graph

    def _events_to_dicts(self, events) -> list[dict]:
        return [
            {
                "id": e.id,
                "event_type": str(e.event_type),
                "work_id": e.work_id,
                "quantity": e.quantity,
                "unit_value": e.unit_value,
                "currency": e.currency,
                "territory": e.territory,
                "timestamp": e.timestamp,
            }
            for e in events
        ]

    def _payments_to_dicts(self, payments) -> list[dict]:
        return [
            {
                "id": p.id,
                "payment_type": str(p.payment_type),
                "amount": p.amount,
                "currency": p.currency,
                "source": p.source,
            }
            for p in payments
        ]

    def _contracts_to_dicts(self, contracts) -> list[dict]:
        return [
            {
                "id": c.id,
                "contract_type": str(c.contract_type),
                "terms": c.terms,
                "territory": c.territory,
            }
            for c in contracts
        ]

    def detect_all(self, artist_id: str, db_session: Session) -> list[dict]:
        result = []
        result.extend(self.detect_royalty_anomalies(artist_id, db_session))
        result.extend(self.detect_touring_anomalies(artist_id, db_session))
        result.extend(self.detect_platform_anomalies(artist_id, db_session))
        return result

    def detect_royalty_anomalies(self, artist_id: str, db_session: Session) -> list[dict]:
        events = self._events_to_dicts(db_session.query(Event).filter(Event.artist_id == artist_id).all())
        payments = self._payments_to_dicts(db_session.query(Payment).filter(Payment.artist_id == artist_id).all())
        contracts = self._contracts_to_dicts(db_session.query(Contract).filter(Contract.artist_id == artist_id).all())
        result = []
        result.extend(royalties.check_missing_royalty_payments(artist_id, events, payments))
        result.extend(royalties.check_incorrect_rates(artist_id, payments, contracts))
        result.extend(royalties.check_foreign_royalties_not_remitted(artist_id, events, payments))
        return result

    def detect_touring_anomalies(self, artist_id: str, db_session: Session) -> list[dict]:
        events = self._events_to_dicts(db_session.query(Event).filter(Event.artist_id == artist_id).all())
        payments = self._payments_to_dicts(db_session.query(Payment).filter(Payment.artist_id == artist_id).all())
        contracts = self._contracts_to_dicts(db_session.query(Contract).filter(Contract.artist_id == artist_id).all())
        result = []
        result.extend(touring.check_missing_guarantee(artist_id, events, payments))
        result.extend(touring.check_settlement_discrepancy(artist_id, events, payments, contracts))
        return result

    def detect_platform_anomalies(self, artist_id: str, db_session: Session) -> list[dict]:
        events = self._events_to_dicts(db_session.query(Event).filter(Event.artist_id == artist_id).all())
        payments = self._payments_to_dicts(db_session.query(Payment).filter(Payment.artist_id == artist_id).all())
        result = []
        result.extend(platforms.check_low_stream_rates(artist_id, events, payments))
        result.extend(platforms.check_missing_platform_payments(artist_id, events, payments))
        return result
