import pytest
from arcos7.anomaly.rules.royalties import check_missing_royalty_payments, check_incorrect_rates
from arcos7.anomaly.rules.platforms import check_low_stream_rates


def test_check_missing_royalty_payments_detects_missing():
    events = [{"event_type": "STREAM", "quantity": 1000, "unit_value": 0.004}]
    payments = []
    anomalies = check_missing_royalty_payments("artist-1", events, payments)
    assert len(anomalies) == 1
    assert anomalies[0]["category"] == "ROYALTY"
    assert anomalies[0]["subtype"] == "MISSING_PAYMENT"
    assert anomalies[0]["severity"] == "HIGH"


def test_check_missing_royalty_payments_no_anomaly_when_paid():
    events = [{"event_type": "STREAM", "quantity": 1000}]
    payments = [{"payment_type": "ROYALTY", "amount": 4.0}]
    anomalies = check_missing_royalty_payments("artist-1", events, payments)
    assert len(anomalies) == 0


def test_check_low_stream_rates_detects_below_threshold():
    events = [{"event_type": "STREAM", "quantity": 1000, "unit_value": 0.001}]
    payments = []
    anomalies = check_low_stream_rates("artist-1", events, payments)
    assert len(anomalies) == 1
    assert anomalies[0]["category"] == "PLATFORM"
    assert anomalies[0]["subtype"] == "LOW_STREAM_RATE"
    assert anomalies[0]["actual_amount"] == 0.001


def test_check_low_stream_rates_no_anomaly_above_threshold():
    events = [{"event_type": "STREAM", "quantity": 1000, "unit_value": 0.004}]
    payments = []
    anomalies = check_low_stream_rates("artist-1", events, payments)
    assert len(anomalies) == 0


def test_check_incorrect_rates_with_discrepancy():
    payments = [{"amount": 50.0, "quantity": 1000}]
    contracts = [{"contract_type": "LABEL", "terms": {"rate": 0.1}}]
    anomalies = check_incorrect_rates("artist-1", payments, contracts)
    assert len(anomalies) == 1
    assert anomalies[0]["subtype"] == "INCORRECT_RATE"
    assert anomalies[0]["category"] == "ROYALTY"


def test_check_incorrect_rates_no_anomaly_within_tolerance():
    payments = [{"amount": 100.0, "quantity": 1000}]
    contracts = [{"contract_type": "LABEL", "terms": {"rate": 0.1}}]
    anomalies = check_incorrect_rates("artist-1", payments, contracts)
    assert len(anomalies) == 0
