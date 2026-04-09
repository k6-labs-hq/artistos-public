"""Characterization tests for shared.utils.dates.

Locks in the existing behaviour of ensure_utc() and period_key().
No module code is changed here.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from shared.utils.dates import ensure_utc, period_key

# ---------------------------------------------------------------------------
# ensure_utc
# ---------------------------------------------------------------------------


class TestEnsureUtcNoneHandling:
    def test_none_fallback_to_now_returns_datetime(self):
        result = ensure_utc(None)
        assert isinstance(result, datetime)

    def test_none_fallback_to_now_is_utc_aware(self):
        result = ensure_utc(None)
        assert result.tzinfo == timezone.utc

    def test_none_fallback_to_now_is_recent(self):
        before = datetime.now(timezone.utc)
        result = ensure_utc(None)
        after = datetime.now(timezone.utc)
        assert before <= result <= after

    def test_none_fallback_false_returns_none(self):
        assert ensure_utc(None, fallback_to_now=False) is None

    def test_none_default_arg_same_as_fallback_true(self):
        # ensuring the default keyword value is fallback_to_now=True
        result = ensure_utc(None)
        assert result is not None


class TestEnsureUtcNaiveDatetime:
    def test_naive_gets_utc_tzinfo(self):
        naive = datetime(2024, 6, 15, 12, 0, 0)
        result = ensure_utc(naive)
        assert result.tzinfo == timezone.utc

    def test_naive_time_values_are_preserved(self):
        naive = datetime(2024, 6, 15, 12, 30, 45)
        result = ensure_utc(naive)
        # replace, not convert — values stay identical
        assert result.year == 2024
        assert result.month == 6
        assert result.day == 15
        assert result.hour == 12
        assert result.minute == 30
        assert result.second == 45

    def test_naive_midnight(self):
        naive = datetime(2000, 1, 1, 0, 0, 0)
        result = ensure_utc(naive)
        assert result == datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    def test_naive_end_of_year(self):
        naive = datetime(2025, 12, 31, 23, 59, 59)
        result = ensure_utc(naive)
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 31


class TestEnsureUtcAwareDatetime:
    def test_already_utc_passthrough(self):
        aware_utc = datetime(2024, 3, 10, 8, 0, 0, tzinfo=timezone.utc)
        result = ensure_utc(aware_utc)
        assert result == aware_utc
        assert result.tzinfo == timezone.utc

    def test_non_utc_converted_to_utc(self):
        est = timezone(timedelta(hours=-5))
        aware_est = datetime(2024, 3, 10, 8, 0, 0, tzinfo=est)
        result = ensure_utc(aware_est)
        assert result.tzinfo == timezone.utc
        # 8:00 EST → 13:00 UTC
        assert result.hour == 13

    def test_positive_offset_converted(self):
        jst = timezone(timedelta(hours=9))
        aware_jst = datetime(2024, 3, 10, 9, 0, 0, tzinfo=jst)
        result = ensure_utc(aware_jst)
        assert result.tzinfo == timezone.utc
        # 9:00 JST → 0:00 UTC
        assert result.hour == 0

    def test_returns_datetime_not_none(self):
        aware = datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert ensure_utc(aware) is not None


# ---------------------------------------------------------------------------
# period_key
# ---------------------------------------------------------------------------


class TestPeriodKeyMonth:
    def test_january(self):
        dt = datetime(2025, 1, 15, tzinfo=timezone.utc)
        assert period_key(dt, "month") == "2025-01"

    def test_december(self):
        dt = datetime(2025, 12, 31, tzinfo=timezone.utc)
        assert period_key(dt, "month") == "2025-12"

    def test_zero_padded(self):
        dt = datetime(2025, 3, 1, tzinfo=timezone.utc)
        assert period_key(dt, "month") == "2025-03"

    def test_default_granularity_is_month(self):
        dt = datetime(2025, 7, 4, tzinfo=timezone.utc)
        assert period_key(dt) == "2025-07"


class TestPeriodKeyQuarter:
    @pytest.mark.parametrize(
        "month,expected_q",
        [
            (1, "Q1"),
            (2, "Q1"),
            (3, "Q1"),
            (4, "Q2"),
            (5, "Q2"),
            (6, "Q2"),
            (7, "Q3"),
            (8, "Q3"),
            (9, "Q3"),
            (10, "Q4"),
            (11, "Q4"),
            (12, "Q4"),
        ],
    )
    def test_month_maps_to_quarter(self, month, expected_q):
        dt = datetime(2025, month, 1, tzinfo=timezone.utc)
        assert period_key(dt, "quarter") == f"2025-{expected_q}"

    def test_format_includes_year(self):
        dt = datetime(2022, 4, 1, tzinfo=timezone.utc)
        assert period_key(dt, "quarter").startswith("2022-")

    def test_q4_december(self):
        dt = datetime(2025, 12, 31, tzinfo=timezone.utc)
        assert period_key(dt, "quarter") == "2025-Q4"


class TestPeriodKeyYear:
    def test_returns_year_string(self):
        dt = datetime(2024, 6, 15, tzinfo=timezone.utc)
        assert period_key(dt, "year") == "2024"

    def test_year_only_no_hyphen(self):
        dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
        result = period_key(dt, "year")
        assert "-" not in result

    def test_year_is_four_digits(self):
        dt = datetime(2025, 8, 20, tzinfo=timezone.utc)
        assert len(period_key(dt, "year")) == 4


class TestPeriodKeySortability:
    def test_month_keys_sort_chronologically(self):
        dates = [
            datetime(2024, 12, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            datetime(2024, 6, 1, tzinfo=timezone.utc),
        ]
        keys = [period_key(d, "month") for d in dates]
        assert sorted(keys) == ["2024-06", "2024-12", "2025-01"]

    def test_quarter_keys_sort_chronologically(self):
        dates = [
            datetime(2025, 10, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 4, 1, tzinfo=timezone.utc),
        ]
        keys = [period_key(d, "quarter") for d in dates]
        assert sorted(keys) == ["2025-Q1", "2025-Q2", "2025-Q4"]


# ---------------------------------------------------------------------------
# Additional branches and edge cases
# ---------------------------------------------------------------------------


class TestEnsureUtcAdditional:
    def test_fallback_to_now_false_ignored_for_non_none_dt(self):
        # fallback_to_now only affects the dt-is-None branch; a real datetime
        # must be returned regardless of the flag value.
        naive = datetime(2024, 6, 1, 10, 0, 0)
        result = ensure_utc(naive, fallback_to_now=False)
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc

    def test_naive_microseconds_preserved(self):
        # The function uses .replace(tzinfo=...) not conversion, so microseconds
        # must be carried over unchanged.
        naive = datetime(2024, 6, 1, 12, 30, 45, 123456)
        result = ensure_utc(naive)
        assert result.microsecond == 123456

    def test_aware_with_utc_zero_offset_normalised(self):
        # timezone(timedelta(0)) is semantically UTC but is not the singleton
        # timezone.utc; astimezone() should still yield timezone.utc.
        utc_zero = timezone(timedelta(0))
        aware = datetime(2024, 3, 15, 8, 0, 0, tzinfo=utc_zero)
        result = ensure_utc(aware)
        assert result.tzinfo == timezone.utc
        assert result.hour == 8  # no shift

    def test_aware_half_hour_offset_crosses_midnight(self):
        # IST (+05:30): 23:00 on 10 Mar → 17:30 on 10 Mar UTC
        # Verify the date does NOT roll over (offset is positive, moving backwards).
        ist = timezone(timedelta(hours=5, minutes=30))
        aware = datetime(2024, 3, 10, 23, 0, 0, tzinfo=ist)
        result = ensure_utc(aware)
        assert result.tzinfo == timezone.utc
        assert result.day == 10
        assert result.hour == 17
        assert result.minute == 30

    def test_aware_negative_offset_crosses_midnight_forward(self):
        # UTC-3: 2024-03-10 22:00 → 2024-03-11 01:00 UTC (date rolls forward).
        m3 = timezone(timedelta(hours=-3))
        aware = datetime(2024, 3, 10, 22, 0, 0, tzinfo=m3)
        result = ensure_utc(aware)
        assert result.day == 11
        assert result.hour == 1


class TestPeriodKeyAdditional:
    def test_naive_datetime_works(self):
        # The function only accesses .year/.month/.strftime; tzinfo is irrelevant.
        naive = datetime(2025, 6, 15)
        assert period_key(naive) == "2025-06"

    def test_unknown_granularity_falls_through_to_year(self):
        # The function has two explicit if-branches then a bare return str(dt.year).
        # Any unrecognised granularity silently returns the year string.
        dt = datetime(2025, 6, 15, tzinfo=timezone.utc)
        assert period_key(dt, "week") == "2025"  # type: ignore[arg-type]

    def test_quarter_keys_sort_across_year_boundary(self):
        # "2024-Q4" must sort before "2025-Q1" lexicographically.
        q4_2024 = period_key(datetime(2024, 12, 1, tzinfo=timezone.utc), "quarter")
        q1_2025 = period_key(datetime(2025, 1, 1, tzinfo=timezone.utc), "quarter")
        assert sorted([q1_2025, q4_2024]) == [q4_2024, q1_2025]

    def test_year_keys_sort_across_decade(self):
        years = [2023, 2025, 2021, 2024]
        keys = [period_key(datetime(y, 6, 1, tzinfo=timezone.utc), "year") for y in years]
        assert sorted(keys) == ["2021", "2023", "2024", "2025"]

    def test_month_day_does_not_affect_key(self):
        # Two datetimes in the same month but different days → same key.
        d1 = datetime(2025, 8, 1, tzinfo=timezone.utc)
        d2 = datetime(2025, 8, 31, tzinfo=timezone.utc)
        assert period_key(d1) == period_key(d2)
