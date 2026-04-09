from datetime import datetime

from sqlalchemy.orm import Session

from XR7.graph.rights_graph import RightsGraph
from XR7.models.contract import Contract
from XR7.models.event import Event
from XR7.models.payment import Payment


class EarningsEngine:
    def __init__(self, rights_graph: RightsGraph):
        self.rights_graph = rights_graph

    def calculate_expected_earnings(self, event: dict, contracts: list) -> dict:
        quantity = event.get("quantity", 1)
        unit_value = event.get("unit_value", 0.0)
        currency = event.get("currency", "USD")
        gross = quantity * unit_value

        breakdown = []
        net = gross
        for contract in contracts:
            terms = getattr(contract, "terms", {}) or {}
            artist_split = terms.get("artist_split", 1.0)
            recoupment = terms.get("recoupment_balance", 0.0)
            contract_net = gross * artist_split
            if recoupment > 0:
                contract_net = max(0.0, contract_net - recoupment)
            breakdown.append(
                {
                    "contract_id": str(contract.id),
                    "contract_type": contract.contract_type,
                    "artist_split": artist_split,
                    "gross_share": gross * artist_split,
                    "net_after_recoupment": contract_net,
                }
            )
            net = contract_net

        if not contracts:
            net = gross

        return {"gross": gross, "net": net, "currency": currency, "breakdown": breakdown}

    def reconstruct_historical(
        self, artist_id: str, start_date: datetime, end_date: datetime, db_session: Session
    ) -> list[dict]:
        events = (
            db_session.query(Event)
            .filter(
                Event.artist_id == artist_id,
                Event.timestamp >= start_date,
                Event.timestamp <= end_date,
            )
            .all()
        )
        contracts = db_session.query(Contract).filter(Contract.artist_id == artist_id).all()
        results = []
        for event in events:
            event_dict = {
                "id": event.id,
                "event_type": event.event_type,
                "quantity": event.quantity,
                "unit_value": event.unit_value,
                "currency": event.currency,
                "timestamp": event.timestamp,
            }
            earnings = self.calculate_expected_earnings(event_dict, contracts)
            results.append({"event_id": event.id, "timestamp": event.timestamp, **earnings})
        return results

    def compute_realtime(self, event_dict: dict, db_session: Session) -> dict:
        artist_id = event_dict.get("artist_id")
        contracts = db_session.query(Contract).filter(Contract.artist_id == artist_id).all()
        return self.calculate_expected_earnings(event_dict, contracts)

    def get_earnings_summary(self, artist_id: str, db_session: Session) -> dict:
        events = db_session.query(Event).filter(Event.artist_id == artist_id).all()
        contracts = db_session.query(Contract).filter(Contract.artist_id == artist_id).all()
        payments = db_session.query(Payment).filter(Payment.artist_id == artist_id).all()

        total_expected = 0.0
        by_type: dict[str, float] = {}
        for event in events:
            event_dict = {
                "quantity": event.quantity,
                "unit_value": event.unit_value,
                "currency": event.currency,
            }
            earnings = self.calculate_expected_earnings(event_dict, contracts)
            total_expected += earnings["net"]
            et = str(event.event_type)
            by_type[et] = by_type.get(et, 0.0) + earnings["net"]

        total_received = sum(p.amount for p in payments)
        variance = total_expected - total_received

        return {
            "artist_id": artist_id,
            "total_expected": total_expected,
            "total_received": total_received,
            "variance": variance,
            "by_type": by_type,
        }
