"""Plain-English finding labels in dispute emails."""

from __future__ import annotations

from XR7.recovery.dispute_delivery import _friendly_finding_label


def test_known_rule_id_maps_to_friendly_label():
    assert _friendly_finding_label("HIGH_RETROACTIVE_PAYMENT_RATIO") == "Retroactive Payment Pattern"
    assert _friendly_finding_label("HIGH_RETROACTIVE_RATIO") == "Retroactive Payment Pattern"
    assert (
        _friendly_finding_label("STREAM_MONTH_WITHOUT_PAYMENT")
        == "Stream Activity Without Corresponding Payment"
    )
    assert _friendly_finding_label("PAYMENT_GAP_OVER_60_DAYS") == "Extended Payment Gap"
    assert _friendly_finding_label("TRACK_RATE_OUTLIER") == "Per-Stream Rate Outlier"


def test_lowercase_rule_id_still_matches():
    assert _friendly_finding_label("high_retroactive_ratio") == "Retroactive Payment Pattern"


def test_unknown_rule_id_falls_back_to_titlecased_words():
    assert _friendly_finding_label("SOME_NEW_RULE_WE_HAVENT_ADDED") == "Some New Rule We Havent Added"


def test_none_returns_default():
    assert _friendly_finding_label(None) == "Royalty audit finding"
    assert _friendly_finding_label("") == "Royalty audit finding"
