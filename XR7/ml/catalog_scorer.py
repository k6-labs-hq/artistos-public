"""
Catalog health / risk scorer for XR7 Engine 2.

Produces a 0–100 health score for an artist's catalog by combining multiple
feature signals:

- Metadata completeness (ISRC/ISWC coverage on works)
- Payment regularity (coefficient of variation of payment amounts)
- Anomaly density (open anomalies per work)
- Recovery rate (fraction of claims that reached PAID/CLOSED)
- Earnings variance (expected vs. actual mismatch ratio)

Each signal is normalised to [0, 1] and a weighted average is computed.
The final score is expressed as an integer in [0, 100] where 100 = perfectly
healthy catalog.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

# ---------------------------------------------------------------------------
# Signal weights (must sum to 1.0)
# ---------------------------------------------------------------------------

_WEIGHTS: dict[str, float] = {
    "metadata_completeness": 0.20,
    "metadata_consistency": 0.10,
    "payment_regularity": 0.20,
    "anomaly_density": 0.20,
    "recovery_rate": 0.15,
    "earnings_accuracy": 0.15,
}

if abs(sum(_WEIGHTS.values()) - 1.0) >= 1e-9:
    raise ValueError(f"Signal weights must sum to 1.0, got {sum(_WEIGHTS.values())}")


# ---------------------------------------------------------------------------
# Individual signal scorers (return value in [0, 1], higher = healthier)
# ---------------------------------------------------------------------------

def _score_metadata_completeness(works: list[dict]) -> float:
    """Fraction of works that have both ISRC and ISWC."""
    if not works:
        return 0.0
    with_both = sum(
        1 for w in works if w.get("isrc") and w.get("iswc")
    )
    return with_both / len(works)


def _score_payment_regularity(payments: list[dict]) -> float:
    """
    Use the inverse of the coefficient of variation (CV) of payment amounts as
    a regularity proxy.  Low CV → regular payments → high score.
    """
    amounts = [float(p.get("amount", 0.0) or 0.0) for p in payments if p.get("amount")]
    if len(amounts) < 2:
        return 0.5  # neutral when we have no history

    arr = np.array(amounts)
    mean = arr.mean()
    if mean == 0.0:
        return 0.0
    cv = arr.std() / mean
    # Map CV: 0 → 1.0, 1 → 0.5, 2+ → 0.0 (clamped)
    return float(np.clip(1.0 - cv / 2.0, 0.0, 1.0))


def _score_anomaly_density(anomalies: list[dict], works: list[dict]) -> float:
    """
    Penalise catalogs with many open anomalies per work.
    0 anomalies / work → 1.0, ≥ 2 anomalies / work → 0.0.
    """
    n_works = max(len(works), 1)
    open_anomalies = [a for a in anomalies if a.get("status", "OPEN") == "OPEN"]
    density = len(open_anomalies) / n_works
    # Map: 0 → 1.0, 2 → 0.0 (linear, clamped)
    return float(np.clip(1.0 - density / 2.0, 0.0, 1.0))


def _score_recovery_rate(claims: list[dict]) -> float:
    """
    Fraction of claims that ended in PAID or CLOSED (i.e. successfully
    recovered).  Returns 0.5 when there are no claims (neutral).
    """
    if not claims:
        return 0.5
    resolved = sum(1 for c in claims if c.get("status") in ("PAID", "CLOSED"))
    return resolved / len(claims)


def _score_earnings_accuracy(earnings_summary: dict) -> float:
    """
    Measure how closely actual payments track expected earnings.
    Perfect match → 1.0; large shortfall → approaches 0.
    """
    expected = float(earnings_summary.get("total_expected", 0.0) or 0.0)
    received = float(earnings_summary.get("total_received", 0.0) or 0.0)
    if expected <= 0.0:
        return 0.5  # no expectation yet — neutral
    ratio = received / expected
    # Clamp ratio to [0, 1.5] then normalise to [0, 1]
    return float(np.clip(ratio / 1.5, 0.0, 1.0))


def _score_metadata_consistency(metadata_health: dict | None) -> float:
    if not metadata_health:
        return 0.5
    return float(np.clip(float(metadata_health.get("consistency_score") or 0.5), 0.0, 1.0))


# ---------------------------------------------------------------------------
# Public data structures
# ---------------------------------------------------------------------------

@dataclass
class CatalogHealthReport:
    """Structured output of ``CatalogScorer.score()``."""

    artist_id: str
    health_score: int                     # 0–100
    grade: str                            # A/B/C/D/F
    signals: dict[str, float] = field(default_factory=dict)    # raw [0,1] values
    risk_flags: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "artist_id": self.artist_id,
            "health_score": self.health_score,
            "grade": self.grade,
            "signals": self.signals,
            "risk_flags": self.risk_flags,
            "recommendations": self.recommendations,
        }


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 45:
        return "D"
    return "F"


# ---------------------------------------------------------------------------
# Main scorer class
# ---------------------------------------------------------------------------

class CatalogScorer:
    """
    Compute a composite catalog health score from raw data dicts.

    Usage::

        scorer = CatalogScorer()
        report = scorer.score(
            artist_id="...",
            works=[...],
            payments=[...],
            anomalies=[...],
            claims=[...],
            earnings_summary={...},
        )
        print(report.health_score, report.grade)
    """

    def score(
        self,
        artist_id: str,
        works: list[dict] | None = None,
        payments: list[dict] | None = None,
        anomalies: list[dict] | None = None,
        claims: list[dict] | None = None,
        earnings_summary: dict | None = None,
        metadata_health: dict | None = None,
    ) -> CatalogHealthReport:
        """
        Compute the catalog health score and return a full report.

        Parameters
        ----------
        artist_id:
            Artist identifier included verbatim in the report.
        works:
            List of work dicts (fields: ``isrc``, ``iswc``, etc.).
        payments:
            List of payment dicts (field: ``amount``).
        anomalies:
            List of anomaly dicts (field: ``status``).
        claims:
            List of claim dicts (field: ``status``).
        earnings_summary:
            Dict from ``EarningsEngine.get_earnings_summary()``.

        Returns
        -------
        :class:`CatalogHealthReport`
        """
        works = works or []
        payments = payments or []
        anomalies = anomalies or []
        claims = claims or []
        earnings_summary = earnings_summary or {}

        signals = {
            "metadata_completeness": _score_metadata_completeness(works),
            "metadata_consistency": _score_metadata_consistency(metadata_health),
            "payment_regularity": _score_payment_regularity(payments),
            "anomaly_density": _score_anomaly_density(anomalies, works),
            "recovery_rate": _score_recovery_rate(claims),
            "earnings_accuracy": _score_earnings_accuracy(earnings_summary),
        }

        weighted = sum(_WEIGHTS[k] * v for k, v in signals.items())
        health_score = int(round(weighted * 100))
        health_score = max(0, min(100, health_score))

        risk_flags: list[str] = []
        recommendations: list[str] = []

        if signals["metadata_completeness"] < 0.5:
            risk_flags.append("LOW_METADATA_COMPLETENESS")
            recommendations.append(
                "Register missing ISRC/ISWC identifiers to improve rights tracking."
            )
        if signals["metadata_consistency"] < 0.6:
            risk_flags.append("METADATA_CONSISTENCY_DRIFT")
            recommendations.append(
                "Metadata repairs are pending review; finalize identifier reconciliation to prevent future leakage."
            )
        if signals["payment_regularity"] < 0.4:
            risk_flags.append("IRREGULAR_PAYMENTS")
            recommendations.append(
                "Payment amounts vary significantly — audit distributor and PRO statements."
            )
        if signals["anomaly_density"] < 0.5:
            risk_flags.append("HIGH_ANOMALY_DENSITY")
            recommendations.append(
                "Multiple open anomalies detected. Prioritise claim review queue."
            )
        if signals["recovery_rate"] < 0.4:
            risk_flags.append("LOW_RECOVERY_RATE")
            recommendations.append(
                "Many claims are unresolved. Escalate stalled claims to dispute resolution."
            )
        if signals["earnings_accuracy"] < 0.5:
            risk_flags.append("EARNINGS_SHORTFALL")
            recommendations.append(
                "Actual payments are significantly below expected earnings. "
                "Run a full historical anomaly scan."
            )

        return CatalogHealthReport(
            artist_id=artist_id,
            health_score=health_score,
            grade=_grade(health_score),
            signals={k: round(v, 4) for k, v in signals.items()},
            risk_flags=risk_flags,
            recommendations=recommendations,
        )
