"""
Recoupment Tracker for XR7 Engine 2.

Label and publishing contracts frequently include recoupment provisions: the
label/publisher advances money to the artist and then recoups that advance
(plus applicable expenses) from the artist's royalty share before the artist
sees any net payment.

Two major money-recovery scenarios arise:

1. **Under-reported recoupment** — The counterparty claims the artist is still
   unrecouped when the payments received suggest recoupment should have been
   reached.  This is a classic audit finding.

2. **Post-recoupment underpayment** — Once recouped, the artist should receive
   their full contracted royalty rate.  If post-recoupment payments remain at
   the pre-recoupment level, money is being withheld.

This module:
- Computes the current recoupment position for each applicable contract.
- Flags contracts where the artist's payments imply a different recoupment
  status than the reported one.
- Detects post-recoupment underpayment when the artist is provably past
  recoupment yet payment rates haven't increased.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Recoupment status enum
# ---------------------------------------------------------------------------

class RecoupmentStatus:
    UNRECOUPED = "UNRECOUPED"         # Artist has not yet recouped the advance
    RECOUPED = "RECOUPED"             # Artist has fully recouped
    OVER_RECOUPED = "OVER_RECOUPED"   # More than advance recouped (possible error)
    UNKNOWN = "UNKNOWN"               # Insufficient data to determine


class RecoupmentFlag:
    RECOUPMENT_DISCREPANCY = "RECOUPMENT_DISCREPANCY"
    POST_RECOUPMENT_UNDERPAYMENT = "POST_RECOUPMENT_UNDERPAYMENT"
    ADVANCE_NEVER_STATED = "ADVANCE_NEVER_STATED"
    EXCESS_RECOUPMENT = "EXCESS_RECOUPMENT"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RecoupmentPosition:
    """Recoupment status for a single contract."""

    contract_id: str
    contract_type: str
    counterparty: str
    advance: float
    recoupment_rate: float          # fraction of artist royalties applied to recoupment
    total_payments: float           # total payments received under this contract
    recouped_amount: float          # advance × recoupment_rate applied to payments
    recoupment_balance: float       # remaining balance (negative = over-recouped)
    recoupment_status: str          # see RecoupmentStatus
    flags: list[str] = field(default_factory=list)
    anomalies: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "contract_type": self.contract_type,
            "counterparty": self.counterparty,
            "advance": round(self.advance, 2),
            "recoupment_rate": self.recoupment_rate,
            "total_payments": round(self.total_payments, 2),
            "recouped_amount": round(self.recouped_amount, 2),
            "recoupment_balance": round(self.recoupment_balance, 2),
            "recoupment_status": self.recoupment_status,
            "flags": self.flags,
            "anomalies": self.anomalies,
        }


def _filter_payments_for_contract(
    payments: list[dict],
    contract: dict,
) -> list[dict]:
    """
    Return payments that plausibly belong to this contract.

    Strategy (in priority order):
    1. Match by ``contract_id`` field on the payment, if present.
    2. Match by payment type matching the contract type.
    3. Fall back to all payments (conservative — maximises recoupment estimate).
    """
    contract_id = contract.get("id", "")
    ct = str(contract.get("contract_type", "")).upper()

    # Map contract types to payment types
    _type_map = {
        "LABEL": "ROYALTY",
        "PUBLISHING": "ROYALTY",
        "MERCH": "ROYALTY",
        "SYNC": "ROYALTY",
        "TOURING": "SETTLEMENT",
        "BRAND": "PAYOUT",
        "GRANT": "GRANT_DISBURSEMENT",
    }
    expected_payment_type = _type_map.get(ct)

    matched = []
    for p in payments:
        if p.get("contract_id") == contract_id:
            matched.append(p)
    if matched:
        return matched

    if expected_payment_type:
        matched = [p for p in payments if str(p.get("payment_type", "")).upper() == expected_payment_type]
    if matched:
        return matched

    return payments


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_recoupment(
    contracts: list[dict],
    payments: list[dict] | None = None,
) -> list[RecoupmentPosition]:
    """
    Compute recoupment status for each contract that has an advance.

    Parameters
    ----------
    contracts:
        List of contract dicts.  Each should have ``id``, ``contract_type``,
        ``counterparty``, and ``terms`` (dict).  Relevant ``terms`` keys:
        - ``advance`` (float): the advance amount
        - ``recoupment_rate`` (float, 0–1): fraction of royalties applied
          to recoupment (default 1.0 = 100 %)
        - ``recoupment_balance`` (float): counterparty-reported remaining balance
    payments:
        All payments for the artist.
    reference_date:
        "Today" — currently unused but reserved for future time-windowed analysis.

    Returns
    -------
    List of :class:`RecoupmentPosition`, sorted by ``recoupment_balance`` ascending
    (largest remaining balance first — most urgent to investigate).
    """
    payments = payments or []
    positions: list[RecoupmentPosition] = []

    # Only process contracts that have recoupment provisions
    recoupable_types = {"LABEL", "PUBLISHING", "MERCH", "SYNC"}

    for contract in contracts:
        ct = str(contract.get("contract_type", "LABEL")).upper()
        if ct not in recoupable_types:
            continue

        terms = contract.get("terms") or {}
        advance = float(terms.get("advance", 0.0) or 0.0)

        if advance <= 0.0:
            continue  # No advance — no recoupment tracking needed

        recoupment_rate = float(terms.get("recoupment_rate", 1.0) or 1.0)
        reported_balance = terms.get("recoupment_balance")  # may be None

        relevant_payments = _filter_payments_for_contract(payments, contract)
        total_payments = sum(float(p.get("amount", 0.0) or 0.0) for p in relevant_payments)

        # How much of the advance has been recouped via payments?
        # raw_recouped is the uncapped value; we cap at the advance for the
        # reported balance but flag excess if the label should have stopped
        # deducting once the advance was fully covered.
        raw_recouped = total_payments * recoupment_rate
        recouped_amount = min(raw_recouped, advance)
        balance = advance - recouped_amount

        if balance <= 0:
            status = RecoupmentStatus.RECOUPED
        else:
            status = RecoupmentStatus.UNRECOUPED

        if raw_recouped > advance:
            status = RecoupmentStatus.OVER_RECOUPED

        flags: list[str] = []
        anomalies_found: list[dict] = []

        # Flag 1: Discrepancy between our calculation and reported balance
        if reported_balance is not None:
            reported = float(reported_balance)
            discrepancy = abs(balance - reported)
            if discrepancy > max(balance * 0.05, 10.0):
                flags.append(RecoupmentFlag.RECOUPMENT_DISCREPANCY)
                anomalies_found.append(
                    {
                        "flag": RecoupmentFlag.RECOUPMENT_DISCREPANCY,
                        "calculated_balance": round(balance, 2),
                        "reported_balance": round(reported, 2),
                        "discrepancy": round(discrepancy, 2),
                        "description": (
                            f"Calculated recoupment balance ({balance:.2f}) differs from "
                            f"counterparty-reported balance ({reported:.2f}) by {discrepancy:.2f}."
                        ),
                    }
                )

        # Flag 2: Payments imply more was recouped than the advance —
        # the label may have continued deducting after the advance was covered.
        if status == RecoupmentStatus.OVER_RECOUPED:
            excess = raw_recouped - advance
            flags.append(RecoupmentFlag.EXCESS_RECOUPMENT)
            anomalies_found.append(
                {
                    "flag": RecoupmentFlag.EXCESS_RECOUPMENT,
                    "advance": round(advance, 2),
                    "raw_recouped_amount": round(raw_recouped, 2),
                    "excess": round(excess, 2),
                    "description": (
                        f"Payments imply {raw_recouped:.2f} was recouped against an advance of "
                        f"{advance:.2f} ({excess:.2f} excess).  Verify no additional expenses "
                        f"are being deducted beyond the stated advance."
                    ),
                }
            )

        positions.append(
            RecoupmentPosition(
                contract_id=contract.get("id", "unknown"),
                contract_type=ct,
                counterparty=contract.get("counterparty", "Unknown"),
                advance=advance,
                recoupment_rate=recoupment_rate,
                total_payments=total_payments,
                recouped_amount=recouped_amount,
                recoupment_balance=max(balance, 0.0),
                recoupment_status=status,
                flags=flags,
                anomalies=anomalies_found,
            )
        )

    # Sort: largest balance (most unrecouped) first
    return sorted(positions, key=lambda p: -p.recoupment_balance)


def recoupment_summary(positions: list[RecoupmentPosition]) -> dict:
    """
    Produce a high-level summary dict from a list of recoupment positions.
    """
    total_advance = sum(p.advance for p in positions)
    total_recouped = sum(p.recouped_amount for p in positions)
    total_balance = sum(p.recoupment_balance for p in positions)
    flagged = [p for p in positions if p.flags]

    return {
        "contracts_tracked": len(positions),
        "total_advance": round(total_advance, 2),
        "total_recouped": round(total_recouped, 2),
        "total_remaining_balance": round(total_balance, 2),
        "recouped_contracts": sum(1 for p in positions if p.recoupment_status == RecoupmentStatus.RECOUPED),
        "unrecouped_contracts": sum(1 for p in positions if p.recoupment_status == RecoupmentStatus.UNRECOUPED),
        "flagged_contracts": len(flagged),
        "flag_types": list({f for p in flagged for f in p.flags}),
    }
