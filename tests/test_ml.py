"""
Tests for the XR7.ml module:
- MLAnomalyDetector (IsolationForest, drift, missingness)
- EarningsForecaster (linear trend)
- CatalogScorer (health/risk scoring)
- ConfidenceUpdater (Bayesian confidence refinement)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from XR7.ml.anomaly_detector import (
    MLAnomalyDetector,
    detect_missing_periodic_payments,
    detect_payment_outliers,
    detect_rate_drift,
)
from XR7.ml.catalog_scorer import CatalogScorer, _grade
from XR7.ml.confidence import AnomalyOutcome, ConfidenceUpdater
from XR7.ml.forecaster import EarningsForecaster, forecast_earnings

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_payments(amounts: list[float]) -> list[dict]:
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return [
        {
            "amount": a,
            "currency": "USD",
            "payment_type": "ROYALTY",
            "received_at": (base + timedelta(days=30 * i)).isoformat(),
        }
        for i, a in enumerate(amounts)
    ]


def _make_events(unit_values: list[float], event_type: str = "STREAM") -> list[dict]:
    return [{"event_type": event_type, "unit_value": uv, "quantity": 1000} for uv in unit_values]


def _make_earnings_records(nets: list[float], event_type: str = "STREAM") -> list[dict]:
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return [
        {
            "event_type": event_type,
            "net": n,
            "timestamp": (base + timedelta(days=30 * i)).isoformat(),
        }
        for i, n in enumerate(nets)
    ]


# ===========================================================================
# MLAnomalyDetector — IsolationForest outlier detection
# ===========================================================================


class TestDetectPaymentOutliers:
    def test_returns_empty_when_too_few_samples(self):
        payments = _make_payments([100.0, 102.0, 98.0])
        result = detect_payment_outliers("artist-1", payments)
        assert result == []

    def test_detects_outlier_in_large_dataset(self):
        # 19 normal payments + 1 huge outlier
        amounts = [100.0] * 19 + [10_000.0]
        payments = _make_payments(amounts)
        result = detect_payment_outliers("artist-1", payments, contamination=0.1)
        # At least the large outlier should be flagged
        assert len(result) >= 1
        assert all(a["subtype"] == "PAYMENT_OUTLIER" for a in result)
        assert all("ml_model" in a for a in result)
        assert all(0.0 <= a["confidence_score"] <= 1.0 for a in result)

    def test_returns_correct_artist_id(self):
        amounts = [100.0] * 19 + [50_000.0]
        payments = _make_payments(amounts)
        result = detect_payment_outliers("artist-xyz", payments, contamination=0.1)
        assert all(a["artist_id"] == "artist-xyz" for a in result)

    def test_uniform_payments_flag_few_outliers(self):
        amounts = [100.0] * 20
        payments = _make_payments(amounts)
        # contamination = 0.05 → ≤ 1 outlier in perfectly uniform data
        result = detect_payment_outliers("artist-1", payments, contamination=0.05)
        assert len(result) <= 1


# ===========================================================================
# MLAnomalyDetector — rate drift detection
# ===========================================================================


class TestDetectRateDrift:
    def test_returns_empty_when_too_few_events(self):
        events = _make_events([0.004, 0.0041, 0.0039], "STREAM")
        result = detect_rate_drift("artist-1", events)
        assert result == []

    def test_detects_high_drift(self):
        # 9 events at 0.004, 1 event at 0.04 (10× higher)
        normal = [0.004] * 9
        outlier = [0.04]
        events = _make_events(normal + outlier, "STREAM")
        result = detect_rate_drift("artist-1", events, zscore_threshold=2.0)
        assert len(result) >= 1
        assert any("RATE_DRIFT" in a["subtype"] for a in result)

    def test_detects_low_drift(self):
        # 9 events at 0.004, 1 event at 0.0001 (much lower)
        normal = [0.004] * 9
        outlier = [0.0001]
        events = _make_events(normal + outlier, "STREAM")
        result = detect_rate_drift("artist-1", events, zscore_threshold=2.0)
        assert len(result) >= 1
        assert any("LOW" in a["subtype"] for a in result)

    def test_stable_rates_produce_no_anomalies(self):
        events = _make_events([0.004] * 10, "STREAM")
        result = detect_rate_drift("artist-1", events, zscore_threshold=2.5)
        assert result == []


# ===========================================================================
# MLAnomalyDetector — periodic missingness
# ===========================================================================


class TestDetectMissingPeriodicPayments:
    def test_returns_empty_for_single_payment(self):
        payments = _make_payments([100.0])
        result = detect_missing_periodic_payments("artist-1", payments)
        assert result == []

    def test_flags_large_gap(self):
        base = datetime(2024, 1, 1, tzinfo=timezone.utc)
        payments = [
            {"amount": 100.0, "received_at": base.isoformat()},
            # 150-day gap (5 months, expected 30 days)
            {"amount": 100.0, "received_at": (base + timedelta(days=150)).isoformat()},
        ]
        result = detect_missing_periodic_payments("artist-1", payments, expected_period_days=30)
        assert len(result) == 1
        assert result[0]["subtype"] == "MISSING_PERIODIC_PAYMENT"
        assert result[0]["gap_days"] == 150

    def test_no_flag_for_normal_gap(self):
        base = datetime(2024, 1, 1, tzinfo=timezone.utc)
        payments = [
            {"amount": 100.0, "received_at": base.isoformat()},
            {"amount": 100.0, "received_at": (base + timedelta(days=31)).isoformat()},
        ]
        result = detect_missing_periodic_payments("artist-1", payments, expected_period_days=30)
        assert result == []

    def test_severity_high_for_many_missed(self):
        base = datetime(2024, 1, 1, tzinfo=timezone.utc)
        payments = [
            {"amount": 100.0, "received_at": base.isoformat()},
            # 150 days → ~4 missed monthly periods (>= 3 → HIGH)
            {"amount": 100.0, "received_at": (base + timedelta(days=150)).isoformat()},
        ]
        result = detect_missing_periodic_payments("artist-1", payments, expected_period_days=30)
        assert result[0]["severity"] == "HIGH"


# ===========================================================================
# MLAnomalyDetector — combined wrapper
# ===========================================================================


class TestMLAnomalyDetector:
    def test_detect_returns_list(self):
        detector = MLAnomalyDetector()
        result = detector.detect("artist-1", events=[], payments=[])
        assert isinstance(result, list)

    def test_detect_aggregates_all_detectors(self):
        detector = MLAnomalyDetector()
        # Provide enough data to trigger outlier detection
        amounts = [100.0] * 19 + [50_000.0]
        payments = _make_payments(amounts)
        result = detector.detect("artist-1", events=[], payments=payments, contamination=0.1)
        subtypes = {a["subtype"] for a in result}
        assert "PAYMENT_OUTLIER" in subtypes


# ===========================================================================
# EarningsForecaster
# ===========================================================================


class TestEarningsForecaster:
    def test_returns_insufficient_data_for_empty_input(self):
        result = forecast_earnings([])
        assert result["trend"] == "INSUFFICIENT_DATA"
        assert result["data_points"] == 0
        assert result["forecast"] == []

    def test_growing_trend_detected(self):
        # Earnings double each month
        records = _make_earnings_records([10.0 * (i + 1) for i in range(12)])
        result = forecast_earnings(records, horizon_days=30)
        assert result["trend"] == "GROWING"
        assert result["slope_per_day"] > 0

    def test_declining_trend_detected(self):
        records = _make_earnings_records([100.0 - 5.0 * i for i in range(12)])
        result = forecast_earnings(records, horizon_days=30)
        assert result["trend"] == "DECLINING"
        assert result["slope_per_day"] < 0

    def test_forecast_has_correct_number_of_points(self):
        records = _make_earnings_records([50.0] * 12)
        result = forecast_earnings(records, horizon_days=60)
        assert len(result["forecast"]) == 60

    def test_forecast_bounds_are_ordered(self):
        records = _make_earnings_records([50.0 + i for i in range(12)])
        result = forecast_earnings(records, horizon_days=30)
        for pt in result["forecast"]:
            assert pt["lower"] <= pt["predicted"] <= pt["upper"]

    def test_r_squared_is_between_0_and_1(self):
        records = _make_earnings_records([10.0 * (i + 1) for i in range(12)])
        result = forecast_earnings(records, horizon_days=30)
        assert 0.0 <= result["r_squared"] <= 1.0

    def test_by_category_returns_dict_keyed_by_event_type(self):
        stream_records = _make_earnings_records([50.0] * 6, event_type="STREAM")
        show_records = _make_earnings_records([200.0] * 6, event_type="SHOW")
        all_records = stream_records + show_records
        forecaster = EarningsForecaster()
        result = forecaster.forecast_by_category(all_records, horizon_days=30)
        assert "STREAM" in result
        assert "SHOW" in result

    def test_predicted_values_are_non_negative(self):
        records = _make_earnings_records([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        result = forecast_earnings(records, horizon_days=90)
        for pt in result["forecast"]:
            assert pt["predicted"] >= 0.0
            assert pt["lower"] >= 0.0

    def test_forecast_contains_explainability_payload(self):
        records = _make_earnings_records([100.0, 110.0, 120.0, 132.0, 145.0, 160.0])
        result = forecast_earnings(records, horizon_days=30)
        assert result["model"] == "DeterministicGrowthV1"
        assert "explanation" in result
        explanation = result["explanation"]
        assert explanation["method"] == "6-month moving average growth"
        assert "monthly_growth_rate" in explanation
        assert "projected_total" in explanation
        assert isinstance(explanation["confidence_band"], list)
        assert "inputs" in explanation


# ===========================================================================
# CatalogScorer
# ===========================================================================


class TestCatalogScorer:
    def _scorer(self):
        return CatalogScorer()

    def test_perfect_catalog_scores_high(self):
        scorer = self._scorer()
        works = [{"isrc": f"US1234{i:06d}", "iswc": f"T-{i:09d}.0"} for i in range(10)]
        payments = [
            {"amount": 100.0, "currency": "USD", "received_at": "2024-01-01T00:00:00"}
            for _ in range(12)
        ]
        earnings_summary = {"total_expected": 1000.0, "total_received": 980.0}
        report = scorer.score(
            "artist-1", works=works, payments=payments, earnings_summary=earnings_summary
        )
        assert report.health_score >= 60
        assert report.grade in ("A", "B", "C")

    def test_empty_catalog_scores_low(self):
        scorer = self._scorer()
        earnings_summary = {"total_expected": 10000.0, "total_received": 0.0}
        report = scorer.score(
            "artist-1",
            works=[],
            payments=[],
            anomalies=[],
            claims=[],
            earnings_summary=earnings_summary,
        )
        assert report.health_score < 60

    def test_grade_function(self):
        assert _grade(95) == "A"
        assert _grade(80) == "B"
        assert _grade(65) == "C"
        assert _grade(50) == "D"
        assert _grade(30) == "F"

    def test_to_dict_contains_required_keys(self):
        scorer = self._scorer()
        report = scorer.score("artist-1")
        d = report.to_dict()
        assert "health_score" in d
        assert "grade" in d
        assert "signals" in d
        assert "risk_flags" in d
        assert "recommendations" in d
        assert d["artist_id"] == "artist-1"

    def test_missing_metadata_triggers_flag(self):
        scorer = self._scorer()
        works = [{"isrc": None, "iswc": None}] * 5
        report = scorer.score("artist-1", works=works)
        assert "LOW_METADATA_COMPLETENESS" in report.risk_flags
        assert len(report.recommendations) > 0

    def test_high_anomaly_density_triggers_flag(self):
        scorer = self._scorer()
        works = [{"isrc": "US123", "iswc": "T-001"}]
        anomalies = [{"status": "OPEN"}] * 5
        report = scorer.score("artist-1", works=works, anomalies=anomalies)
        assert "HIGH_ANOMALY_DENSITY" in report.risk_flags

    def test_health_score_in_valid_range(self):
        scorer = self._scorer()
        report = scorer.score("artist-1")
        assert 0 <= report.health_score <= 100

    def test_signals_all_between_0_and_1(self):
        scorer = self._scorer()
        payments = _make_payments([100.0, 200.0, 50.0, 300.0])
        report = scorer.score("artist-1", payments=payments)
        for k, v in report.signals.items():
            assert 0.0 <= v <= 1.0, f"Signal {k}={v} out of range"


# ===========================================================================
# ConfidenceUpdater
# ===========================================================================


class TestConfidenceUpdater:
    def test_initial_refined_confidence_close_to_raw(self):
        updater = ConfidenceUpdater()
        # With no outcomes recorded, posterior mean = alpha/(alpha+beta) = 2/3 ≈ 0.667
        # Blended = 0.5 * 0.667 + 0.5 * 0.85 ≈ 0.758
        score = updater.refined_confidence("ROYALTY", "MISSING_PAYMENT", raw_score=0.85)
        assert 0.5 <= score <= 1.0

    def test_true_positives_increase_confidence(self):
        updater = ConfidenceUpdater()
        raw = 0.5
        baseline = updater.refined_confidence("ROYALTY", "MISSING_PAYMENT", raw_score=raw)
        for _ in range(10):
            updater.record_outcome("ROYALTY", "MISSING_PAYMENT", AnomalyOutcome.TRUE_POSITIVE)
        after = updater.refined_confidence("ROYALTY", "MISSING_PAYMENT", raw_score=raw)
        assert after > baseline

    def test_false_positives_decrease_confidence(self):
        updater = ConfidenceUpdater()
        raw = 0.9
        baseline = updater.refined_confidence("ROYALTY", "MISSING_PAYMENT", raw_score=raw)
        for _ in range(10):
            updater.record_outcome("ROYALTY", "MISSING_PAYMENT", AnomalyOutcome.FALSE_POSITIVE)
        after = updater.refined_confidence("ROYALTY", "MISSING_PAYMENT", raw_score=raw)
        assert after < baseline

    def test_confidence_stays_in_bounds(self):
        updater = ConfidenceUpdater()
        for _ in range(50):
            updater.record_outcome("ROYALTY", "MISSING_PAYMENT", AnomalyOutcome.TRUE_POSITIVE)
        score = updater.refined_confidence("ROYALTY", "MISSING_PAYMENT", raw_score=0.99)
        assert 0.0 <= score <= 1.0

    def test_precision_stats_returns_expected_keys(self):
        updater = ConfidenceUpdater()
        updater.record_outcome("PLATFORM", "LOW_STREAM_RATE", AnomalyOutcome.TRUE_POSITIVE)
        stats = updater.precision_stats("PLATFORM", "LOW_STREAM_RATE")
        assert stats["category"] == "PLATFORM"
        assert stats["subtype"] == "LOW_STREAM_RATE"
        assert "posterior_mean" in stats
        assert "alpha" in stats
        assert "beta" in stats
        assert stats["sample_count"] == 1

    def test_all_stats_returns_list(self):
        updater = ConfidenceUpdater()
        updater.record_outcome("ROYALTY", "MISSING_PAYMENT", AnomalyOutcome.TRUE_POSITIVE)
        updater.record_outcome("TOURING", "MISSING_GUARANTEE", AnomalyOutcome.FALSE_POSITIVE)
        all_stats = updater.all_stats()
        assert len(all_stats) == 2
        keys = {(s["category"], s["subtype"]) for s in all_stats}
        assert ("ROYALTY", "MISSING_PAYMENT") in keys
        assert ("TOURING", "MISSING_GUARANTEE") in keys

    def test_bulk_record_from_claims(self):
        updater = ConfidenceUpdater()
        claims = [
            {
                "status": "PAID",
                "category": "ROYALTY",
                "subtype": "MISSING_PAYMENT",
                "recovered_amount": 500.0,
            },
            {
                "status": "CLOSED",
                "category": "ROYALTY",
                "subtype": "MISSING_PAYMENT",
                "recovered_amount": 0.0,
            },
            {
                "status": "IDENTIFIED",
                "category": "ROYALTY",
                "subtype": "MISSING_PAYMENT",
                "recovered_amount": 0.0,
            },
        ]
        updater.bulk_record_from_claims(claims)
        stats = updater.precision_stats("ROYALTY", "MISSING_PAYMENT")
        # 1 TP + 1 FP recorded, 1 IDENTIFIED skipped
        assert stats["sample_count"] == 2
