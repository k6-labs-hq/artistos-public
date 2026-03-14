from sqlalchemy.orm import Session

from XR7.anomaly.rules import royalties, touring, platforms
from XR7.earnings.engine import EarningsEngine
from XR7.graph.rights_graph import RightsGraph
from XR7.ml.anomaly_detector import MLAnomalyDetector
from XR7.models.model_registry import ModelRegistryEntry
from XR7.models.contract import Contract
from XR7.models.event import Event
from XR7.models.payment import Payment


class AnomalyEngine:
    def __init__(self, earnings_engine: EarningsEngine, rights_graph: RightsGraph):
        self.earnings_engine = earnings_engine
        self.rights_graph = rights_graph
        self._ml_detector = MLAnomalyDetector()

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
        result.extend(self.detect_ml_anomalies(artist_id, db_session))
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

    def detect_ml_anomalies(self, artist_id: str, db_session: Session) -> list[dict]:
        """Run ML-based anomaly detectors (IsolationForest, drift, missingness)."""
        events = self._events_to_dicts(db_session.query(Event).filter(Event.artist_id == artist_id).all())
        payments = self._payments_to_dicts(db_session.query(Payment).filter(Payment.artist_id == artist_id).all())

        peer_payments = self._payments_to_dicts(db_session.query(Payment).filter(Payment.artist_id != artist_id).limit(5000).all())
        peer_events = self._events_to_dicts(db_session.query(Event).filter(Event.artist_id != artist_id).limit(5000).all())

        peer_mean_amount = None
        if peer_payments:
            peer_mean_amount = sum(float(p.get("amount") or 0.0) for p in peer_payments) / max(len(peer_payments), 1)
        peer_unit_values = [float(e.get("unit_value") or 0.0) for e in peer_events if float(e.get("unit_value") or 0.0) > 0.0]
        peer_unit_value_baseline = (sum(peer_unit_values) / max(len(peer_unit_values), 1)) if peer_unit_values else None

        anomalies = self._ml_detector.detect(
            artist_id,
            events=events,
            payments=payments,
            peer_context={
                "peer_mean_amount": peer_mean_amount,
                "peer_unit_value_baseline": peer_unit_value_baseline,
            },
        )

        if anomalies:
            first_version = anomalies[0].get("model_version")
            if first_version:
                exists = (
                    db_session.query(ModelRegistryEntry)
                    .filter(
                        ModelRegistryEntry.model_family == "anomaly_detector",
                        ModelRegistryEntry.model_version == str(first_version),
                    )
                    .first()
                )
                if not exists:
                    db_session.add(
                        ModelRegistryEntry(
                            model_family="anomaly_detector",
                            model_version=str(first_version),
                            training_snapshot_ref="peer-context-live-window",
                            metrics={"detected_count": len(anomalies)},
                            metadata={"engine": "MLAnomalyDetector"},
                        )
                    )
                    db_session.commit()

        return anomalies
