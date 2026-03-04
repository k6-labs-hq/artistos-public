"""
ML-based anomaly detector for ARCOS7 Engine 2.

Uses:
- Isolation Forest (scikit-learn) for unsupervised outlier detection across
  payment amount sequences.
- Z-score / rolling-window drift detection to flag when a metric (e.g. per-
  stream rate or payout size) shifts significantly from its historical baseline.
- Missingness detector to surface gaps in expected periodic payments.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Fraction of samples considered outliers by IsolationForest.
# Set conservatively so we surface genuine anomalies without flooding the queue.
_IF_CONTAMINATION = 0.05

# Z-score threshold above which a data point is considered a drift anomaly.
_ZSCORE_THRESHOLD = 2.5

# Minimum number of data points required before running statistical checks.
_MIN_SAMPLES = 5

# Maximum number of consecutive missing periodic payments before flagging.
_MAX_CONSECUTIVE_MISSING = 2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_feature_matrix(records: list[dict], feature_keys: list[str]) -> np.ndarray:
    """Extract numeric features from a list of dicts into an ndarray."""
    rows = []
    for r in records:
        row = [float(r.get(k, 0.0) or 0.0) for k in feature_keys]
        rows.append(row)
    return np.array(rows, dtype=float)


def _zscore(values: np.ndarray) -> np.ndarray:
    """Return Z-scores for a 1-D array, guarding against zero std."""
    std = values.std()
    if std == 0.0:
        return np.zeros_like(values)
    return (values - values.mean()) / std


def _normalize_if_scores(scores: np.ndarray) -> np.ndarray:
    """
    Map IsolationForest ``score_samples`` output to [0, 1].

    ``score_samples`` returns negative values; lower (more negative) means
    more anomalous.  We invert and normalise so that the most anomalous point
    maps to 1.0 and the least anomalous maps to 0.0.
    """
    inverted = -scores  # now: higher = more anomalous
    min_v, max_v = inverted.min(), inverted.max()
    if max_v == min_v:
        return np.zeros_like(inverted)
    return (inverted - min_v) / (max_v - min_v)


# ---------------------------------------------------------------------------
# IsolationForest outlier detector
# ---------------------------------------------------------------------------

def detect_payment_outliers(
    artist_id: str,
    payments: list[dict],
    contamination: float = _IF_CONTAMINATION,
) -> list[dict]:
    """
    Use an IsolationForest to find payments whose amount is anomalously high or
    low compared to the artist's own payment history.

    Parameters
    ----------
    artist_id:
        The artist being analysed (used to populate returned anomaly dicts).
    payments:
        List of payment dicts, each containing at least ``amount``.
    contamination:
        Expected proportion of outliers in the dataset.  Forwarded to
        ``IsolationForest``.

    Returns
    -------
    List of anomaly dicts (empty when there are not enough samples).
    """
    if len(payments) < _MIN_SAMPLES:
        return []

    features = _to_feature_matrix(payments, ["amount"])
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    clf = IsolationForest(contamination=contamination, random_state=42)
    labels = clf.fit_predict(X)  # -1 = outlier, 1 = inlier
    scores = clf.score_samples(X)  # lower = more anomalous
    normalized = _normalize_if_scores(scores)

    anomalies: list[dict] = []
    for idx, (label, norm_score) in enumerate(zip(labels, normalized)):
        if label == -1:
            p = payments[idx]
            anomalies.append(
                {
                    "artist_id": artist_id,
                    "category": "PLATFORM",
                    "subtype": "PAYMENT_OUTLIER",
                    "severity": "MEDIUM",
                    "actual_amount": p.get("amount"),
                    "confidence_score": round(float(norm_score), 4),
                    "description": (
                        f"Payment of {p.get('amount')} {p.get('currency', 'USD')} "
                        f"is statistically anomalous (normalised anomaly score {norm_score:.3f})."
                    ),
                    "ml_model": "IsolationForest",
                    "payment_index": idx,
                }
            )
    return anomalies


# ---------------------------------------------------------------------------
# Drift detector
# ---------------------------------------------------------------------------

def detect_rate_drift(
    artist_id: str,
    events: list[dict],
    zscore_threshold: float = _ZSCORE_THRESHOLD,
) -> list[dict]:
    """
    Detect drift in per-unit rates (e.g. per-stream royalty rate) using a
    Z-score approach over a rolling window.

    An event's ``unit_value`` is compared against the distribution of all prior
    unit values for the same event type.  A Z-score beyond *zscore_threshold*
    indicates that the rate has shifted in a statistically significant way.

    Parameters
    ----------
    artist_id:
        The artist being analysed.
    events:
        List of event dicts, each containing ``event_type`` and ``unit_value``.
    zscore_threshold:
        Absolute Z-score value that triggers a drift anomaly.

    Returns
    -------
    List of anomaly dicts.
    """
    by_type: dict[str, list[float]] = {}
    for e in events:
        et = e.get("event_type", "UNKNOWN")
        uv = float(e.get("unit_value", 0.0) or 0.0)
        if uv > 0.0:
            by_type.setdefault(et, []).append(uv)

    anomalies: list[dict] = []
    for event_type, values in by_type.items():
        if len(values) < _MIN_SAMPLES:
            continue
        arr = np.array(values)
        zscores = _zscore(arr)
        for idx, z in enumerate(zscores):
            if abs(z) > zscore_threshold:
                direction = "HIGH" if z > 0 else "LOW"
                severity = "HIGH" if abs(z) > zscore_threshold * 1.5 else "MEDIUM"
                anomalies.append(
                    {
                        "artist_id": artist_id,
                        "category": "PLATFORM",
                        "subtype": f"RATE_DRIFT_{direction}",
                        "severity": severity,
                        "actual_amount": values[idx],
                        "confidence_score": round(
                            float(np.clip((abs(z) - zscore_threshold) / zscore_threshold, 0.0, 1.0)), 4
                        ),
                        "description": (
                            f"{event_type} unit_value {values[idx]:.6f} has Z-score "
                            f"{z:.2f}, indicating a {direction.lower()} drift from "
                            f"the historical mean of {arr.mean():.6f}."
                        ),
                        "ml_model": "ZScoreDrift",
                        "event_type": event_type,
                    }
                )
    return anomalies


# ---------------------------------------------------------------------------
# Missingness detector
# ---------------------------------------------------------------------------

def detect_missing_periodic_payments(
    artist_id: str,
    payments: list[dict],
    expected_period_days: int = 30,
    max_consecutive_missing: int = _MAX_CONSECUTIVE_MISSING,
) -> list[dict]:
    """
    Detect gaps in what should be a regular periodic payment schedule.

    Payments are sorted by ``received_at`` (or ``period_start``).  If the gap
    between two consecutive payments exceeds ``expected_period_days *
    (max_consecutive_missing + 1)`` we flag a missingness anomaly.

    Parameters
    ----------
    artist_id:
        The artist being analysed.
    payments:
        List of payment dicts.  Each dict should contain ``received_at`` or
        ``period_start`` (ISO 8601 string or datetime).
    expected_period_days:
        Expected number of days between regular payments (default 30 = monthly).
    max_consecutive_missing:
        Number of allowed missed periods before raising an anomaly.

    Returns
    -------
    List of anomaly dicts.
    """
    if len(payments) < 2:
        return []

    def _parse_date(p: dict) -> datetime | None:
        for key in ("received_at", "period_start"):
            val = p.get(key)
            if val is None:
                continue
            if isinstance(val, datetime):
                return val
            try:
                return datetime.fromisoformat(str(val))
            except ValueError:
                continue
        return None

    dated = sorted(
        [(p, _parse_date(p)) for p in payments if _parse_date(p) is not None],
        key=lambda x: x[1],
    )
    if len(dated) < 2:
        return []

    threshold = timedelta(days=expected_period_days * (max_consecutive_missing + 1))
    anomalies: list[dict] = []
    for i in range(1, len(dated)):
        prev_p, prev_dt = dated[i - 1]
        curr_p, curr_dt = dated[i]
        gap = curr_dt - prev_dt
        if gap > threshold:
            missed_periods = int(gap.days / expected_period_days) - 1
            anomalies.append(
                {
                    "artist_id": artist_id,
                    "category": "ROYALTY",
                    "subtype": "MISSING_PERIODIC_PAYMENT",
                    "severity": "HIGH" if missed_periods >= 3 else "MEDIUM",
                    "confidence_score": 0.9,
                    "description": (
                        f"Gap of {gap.days} days between payments "
                        f"({prev_dt.date()} → {curr_dt.date()}) suggests "
                        f"~{missed_periods} missed payment period(s)."
                    ),
                    "ml_model": "PeriodicMissingnessDetector",
                    "gap_days": gap.days,
                    "estimated_missed_periods": missed_periods,
                }
            )
    return anomalies


# ---------------------------------------------------------------------------
# Convenience wrapper
# ---------------------------------------------------------------------------

class MLAnomalyDetector:
    """
    Aggregates all ML-based anomaly detection methods into a single callable.

    Usage::

        detector = MLAnomalyDetector()
        anomalies = detector.detect(artist_id, events=events, payments=payments)
    """

    def detect(
        self,
        artist_id: str,
        events: list[dict] | None = None,
        payments: list[dict] | None = None,
        contamination: float = _IF_CONTAMINATION,
        zscore_threshold: float = _ZSCORE_THRESHOLD,
        expected_period_days: int = 30,
    ) -> list[dict]:
        """
        Run all ML detectors and return a merged list of anomaly dicts.

        Parameters
        ----------
        artist_id:
            The artist being analysed.
        events:
            List of event dicts (used for drift detection).
        payments:
            List of payment dicts (used for outlier and missingness detection).
        contamination:
            IsolationForest contamination fraction.
        zscore_threshold:
            Z-score threshold for drift detection.
        expected_period_days:
            Expected days between periodic payments.

        Returns
        -------
        Merged list of anomaly dicts from all detectors.
        """
        events = events or []
        payments = payments or []

        results: list[dict] = []
        results.extend(detect_payment_outliers(artist_id, payments, contamination))
        results.extend(detect_rate_drift(artist_id, events, zscore_threshold))
        results.extend(detect_missing_periodic_payments(artist_id, payments, expected_period_days))
        return results
