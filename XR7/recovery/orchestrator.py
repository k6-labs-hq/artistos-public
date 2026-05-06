import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from XR7.billing.engine import BillingEngine
from XR7.core.claims.state_machine import contract_type_for_category, next_status
from XR7.core.integrity.evidence_crypto import seal_packet
from XR7.core.integrity.evidence_crypto import verify_packet_integrity as _core_verify_integrity
from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.contract import Contract
from XR7.models.event import Event
from XR7.models.payment import Payment
from XR7.models.recovery_intelligence import RoyaltyLedgerEntry
from XR7.recovery.sol_calculator import calculate_sol
from XR7.services.metadata_repair_engine import MetadataRepairEngine


class ClaimsOrchestrator:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @staticmethod
    def _signing_mode() -> str:
        import os

        return os.environ.get("XR7_EVIDENCE_SIGNING_MODE", "hmac")

    @staticmethod
    def _money(value: float | None) -> float:
        return round(float(value or 0.0), 2)

    @staticmethod
    def _enum_value(value):
        return value.value if hasattr(value, "value") else value

    # _contract_type_for_category → XR7.core.claims.state_machine.contract_type_for_category
    # Cryptography helpers        → XR7.core.integrity.evidence_crypto

    def verify_packet_integrity(self, packet: dict) -> dict:
        """Delegates to the pure core implementation (no DB required)."""
        return _core_verify_integrity(packet)

    def _ledger_rows_for_anomaly(
        self, anomaly: Anomaly | None, artist_id: str
    ) -> list[RoyaltyLedgerEntry]:
        query = self.db_session.query(RoyaltyLedgerEntry).filter(
            RoyaltyLedgerEntry.artist_id == artist_id
        )
        if anomaly is None:
            return query.all()

        if anomaly.time_window_start is not None:
            query = query.filter(RoyaltyLedgerEntry.period_end >= anomaly.time_window_start.date())
        if anomaly.time_window_end is not None:
            query = query.filter(RoyaltyLedgerEntry.period_start <= anomaly.time_window_end.date())
        if anomaly.territory:
            query = query.filter(RoyaltyLedgerEntry.territory == anomaly.territory)
        return query.all()

    def _build_ledger_proof(self, rows: list[RoyaltyLedgerEntry]) -> tuple[list[dict], dict]:
        proof_lines: list[dict] = []
        total_expected = 0.0
        total_received = 0.0

        for row in rows:
            expected = float(row.expected_amount or 0.0)
            received = float(row.received_amount or 0.0)
            shortfall = max(expected - received, 0.0)
            total_expected += expected
            total_received += received

            proof_lines.append(
                {
                    "ledger_entry_id": row.id,
                    "source": row.source,
                    "source_file": row.source_file,
                    "source_row": row.source_row,
                    "record_type": self._enum_value(row.record_type),
                    "work_id": row.work_id,
                    "event_type": row.event_type,
                    "period_start": row.period_start.isoformat() if row.period_start else None,
                    "period_end": row.period_end.isoformat() if row.period_end else None,
                    "territory": row.territory,
                    "currency": row.currency,
                    "expected_amount": self._money(expected),
                    "received_amount": self._money(received),
                    "shortfall_amount": self._money(shortfall),
                    "calculation": f"{expected:.2f} - {received:.2f} = {shortfall:.2f}",
                    "ingested_at": row.ingested_at.isoformat() if row.ingested_at else None,
                }
            )

        totals = {
            "ledger_row_count": len(rows),
            "total_expected_amount": self._money(total_expected),
            "total_received_amount": self._money(total_received),
            "ledger_shortfall_amount": self._money(max(total_expected - total_received, 0.0)),
        }
        return proof_lines, totals

    def create_claim(
        self,
        anomaly_id: str,
        claim_type: str,
        evidence: dict | None = None,
        payer_name: str | None = None,
    ) -> Claim:
        anomaly = self.db_session.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not anomaly:
            raise ValueError(f"Anomaly {anomaly_id} not found")
        artist = self.db_session.query(Artist).filter(Artist.id == anomaly.artist_id).first()
        infringement_date = anomaly.time_window_end or anomaly.created_at
        sol = calculate_sol(
            governing_law_state=(artist.primary_jurisdiction if artist else "USA"),
            contract_type=(artist.preferred_contract_type if artist else "recording"),
            infringement_date=infringement_date,
            discovery_date=anomaly.created_at,
        )
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=anomaly.artist_id,
            anomaly_id=anomaly_id,
            claim_type=claim_type,
            status=ClaimStatus.IDENTIFIED,
            evidence=evidence or {},
            payer_name=payer_name,
            governing_law_state=sol.get("governing_law_state") or "USA",
            contract_type=sol.get("contract_type") or "recording",
            infringement_date=infringement_date,
            discovery_date=anomaly.created_at,
            sol_window_years=sol.get("sol_window_years"),
            sol_citation_source=sol.get("sol_citation_source"),
            sol_deadline=sol.get("sol_deadline"),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db_session.add(claim)
        self.db_session.commit()
        self.db_session.refresh(claim)
        return claim

    def advance_claim(self, claim_id: str) -> Claim:
        claim = self.db_session.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        claim.status = next_status(ClaimStatus(claim.status))
        claim.updated_at = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(claim)
        return claim

    def generate_evidence_packet(self, claim_id: str) -> dict:
        claim = self.db_session.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        anomaly = self.db_session.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
        artist_id = claim.artist_id
        events = self.db_session.query(Event).filter(Event.artist_id == artist_id).all()
        contracts = self.db_session.query(Contract).filter(Contract.artist_id == artist_id).all()
        payments = self.db_session.query(Payment).filter(Payment.artist_id == artist_id).all()

        ledger_rows = self._ledger_rows_for_anomaly(anomaly, artist_id)
        proof_lines, proof_totals = self._build_ledger_proof(ledger_rows)
        metadata_logs: list[dict] = MetadataRepairEngine(self.db_session).recent_repair_logs(
            artist_id
        )

        anomaly_expected = self._money(anomaly.expected_amount if anomaly else 0.0)
        anomaly_actual = self._money(anomaly.actual_amount if anomaly else 0.0)
        anomaly_shortfall = self._money(max(anomaly_expected - anomaly_actual, 0.0))
        estimated_recoverable = self._money(anomaly.estimated_recoverable if anomaly else 0.0)
        model_shortfall = anomaly_shortfall if anomaly_shortfall > 0 else estimated_recoverable
        proof_shortfall = (
            proof_totals["ledger_shortfall_amount"]
            if proof_totals["ledger_row_count"] > 0
            else model_shortfall
        )
        discrepancy_amount = self._money(abs(proof_shortfall - model_shortfall))

        anomaly_category = self._enum_value(anomaly.category) if anomaly else None
        target_contract_type = contract_type_for_category(
            str(anomaly_category) if anomaly else None
        )
        relevant_contracts = [
            c
            for c in contracts
            if target_contract_type is None
            or self._enum_value(c.contract_type) == target_contract_type
        ]

        prior_packet_hash = None
        revision = 1
        if isinstance(claim.evidence, dict):
            prior_packet_hash = claim.evidence.get("integrity", {}).get("packet_hash")
            prior_revision = claim.evidence.get("metadata", {}).get("revision")
            if isinstance(prior_revision, int):
                revision = prior_revision + 1

        packet = {
            "claim_id": claim_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "packet_version": "1.1",
                "revision": revision,
            },
            "anomaly": {
                "id": anomaly.id if anomaly else None,
                "category": anomaly_category,
                "subtype": anomaly.subtype if anomaly else None,
                "description": anomaly.description if anomaly else None,
                "expected_amount": anomaly_expected,
                "actual_amount": anomaly_actual,
                "estimated_recoverable": estimated_recoverable,
                "time_window_start": (
                    anomaly.time_window_start.isoformat()
                    if anomaly and anomaly.time_window_start
                    else None
                ),
                "time_window_end": (
                    anomaly.time_window_end.isoformat()
                    if anomaly and anomaly.time_window_end
                    else None
                ),
                "territory": anomaly.territory if anomaly else None,
            },
            "proof": {
                "ledger_evidence": proof_lines,
                "totals": proof_totals,
                "missing_money_amount": self._money(proof_shortfall),
                "method": "sum(max(expected_amount - received_amount, 0)) by ledger row",
                "data_scope": {
                    "artist_id": artist_id,
                    "territory": anomaly.territory if anomaly else None,
                    "time_window_start": (
                        anomaly.time_window_start.isoformat()
                        if anomaly and anomaly.time_window_start
                        else None
                    ),
                    "time_window_end": (
                        anomaly.time_window_end.isoformat()
                        if anomaly and anomaly.time_window_end
                        else None
                    ),
                },
            },
            "reconciliation": {
                "model_shortfall_amount": self._money(model_shortfall),
                "proof_shortfall_amount": self._money(proof_shortfall),
                "discrepancy_amount": discrepancy_amount,
                "discrepancy_flag": discrepancy_amount > 0.01,
            },
            "legal_support": {
                "contract_basis": [
                    {
                        "id": c.id,
                        "contract_type": self._enum_value(c.contract_type),
                        "counterparty": c.counterparty,
                        "effective_date": (
                            c.effective_date.isoformat() if c.effective_date else None
                        ),
                        "expiry_date": c.expiry_date.isoformat() if c.expiry_date else None,
                        "territory": c.territory,
                        "terms": c.terms,
                    }
                    for c in relevant_contracts
                ],
                "source_citations": [
                    {
                        "ledger_entry_id": p["ledger_entry_id"],
                        "source_file": p["source_file"],
                        "source_row": p["source_row"],
                        "source": p["source"],
                    }
                    for p in proof_lines
                ],
            },
            "existing_claim_evidence": claim.evidence or {},
            "metadata_repairs": {
                "logs": metadata_logs,
            },
            "events": [
                {
                    "id": e.id,
                    "event_type": self._enum_value(e.event_type),
                    "timestamp": str(e.timestamp),
                }
                for e in events
            ],
            "contracts": [
                {"id": c.id, "contract_type": self._enum_value(c.contract_type)} for c in contracts
            ],
            "payments": [
                {"id": p.id, "amount": p.amount, "currency": p.currency} for p in payments
            ],
            "summary": {
                "event_count": len(events),
                "contract_count": len(contracts),
                "payment_count": len(payments),
                "proof_row_count": proof_totals["ledger_row_count"],
                "metadata_repair_log_count": len(metadata_logs),
                "discrepancy_flag": discrepancy_amount > 0.01,
            },
        }

        packet["integrity"] = seal_packet(packet, prior_packet_hash)

        claim.evidence = packet
        claim.updated_at = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(claim)
        return packet

    def get_claim_status(self, claim_id: str) -> str:
        claim = self.db_session.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        return str(claim.status)

    def reconcile_recovered_amount(
        self, claim_id: str, recovered_amount: float, currency: str
    ) -> Claim:
        claim = self.db_session.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        artist = self.db_session.query(Artist).filter(Artist.id == claim.artist_id).first()
        billing_engine = BillingEngine(self.db_session)
        claim.recovered_amount = recovered_amount
        claim.currency = currency
        claim.contingency_fee = billing_engine.calculate_contingency_fee(
            recovered_amount, claim.artist_id
        )
        claim.platform_fee_percent = float(getattr(artist, "contingency_fee_percent", 0.0) or 0.0)
        claim.platform_fee_amount = claim.contingency_fee
        claim.artist_net_amount = float(recovered_amount or 0.0) - float(
            claim.contingency_fee or 0.0
        )
        claim.updated_at = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(claim)
        return claim
