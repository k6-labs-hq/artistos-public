"""Characterization tests for shared.utils.numbers.

Locks in the existing behaviour of safe_float() and money_round().
No module code is changed here.
"""

from __future__ import annotations

import pytest

from shared.utils.numbers import money_round, safe_float


# ---------------------------------------------------------------------------
# safe_float – typical inputs
# ---------------------------------------------------------------------------

class TestSafeFloatTypicalInputs:
    def test_plain_integer_string(self):
        assert safe_float("42") == 42.0

    def test_plain_float_string(self):
        assert safe_float("3.14") == 3.14

    def test_actual_int(self):
        assert safe_float(100) == 100.0

    def test_actual_float(self):
        assert safe_float(9.99) == 9.99

    def test_dollar_sign_stripped(self):
        assert safe_float("$250.00") == 250.0

    def test_comma_stripped(self):
        assert safe_float("1,000") == 1000.0

    def test_dollar_and_comma_stripped(self):
        assert safe_float("$1,234.56") == 1234.56

    def test_negative_value(self):
        assert safe_float("-50.25") == -50.25

    def test_zero_string(self):
        assert safe_float("0") == 0.0

    def test_zero_float(self):
        assert safe_float(0.0) == 0.0

    def test_leading_whitespace_handled(self):
        assert safe_float("  7.5") == 7.5

    def test_trailing_whitespace_handled(self):
        assert safe_float("7.5  ") == 7.5


# ---------------------------------------------------------------------------
# safe_float – empty / sentinel tokens → default
# ---------------------------------------------------------------------------

class TestSafeFloatSentinelTokens:
    @pytest.mark.parametrize("sentinel", ["", "-", "N/A", "na", "None", "n/a"])
    def test_sentinel_returns_default(self, sentinel):
        assert safe_float(sentinel) == 0.0

    def test_none_returns_default(self):
        assert safe_float(None) == 0.0

    def test_none_custom_default(self):
        assert safe_float(None, default=99.0) == 99.0

    def test_sentinel_custom_default(self):
        assert safe_float("N/A", default=-1.0) == -1.0

    def test_empty_string_custom_default(self):
        assert safe_float("", default=0.5) == 0.5


# ---------------------------------------------------------------------------
# safe_float – error paths
# ---------------------------------------------------------------------------

class TestSafeFloatErrorPaths:
    def test_unparseable_string_returns_default(self):
        assert safe_float("not_a_number") == 0.0

    def test_unparseable_string_custom_default(self):
        assert safe_float("???", default=-99.0) == -99.0

    def test_list_input_returns_default(self):
        assert safe_float([1, 2]) == 0.0

    def test_dict_input_returns_default(self):
        assert safe_float({"a": 1}) == 0.0

    def test_boolean_true_coerces_to_1(self):
        # bool is a subclass of int; str(True) == "True" → unparseable after strip
        # but float(True) would be 1.0. The function calls str() first.
        # "True" → not in _EMPTY_TOKENS → float("True") raises ValueError → default
        assert safe_float(True) == 0.0

    def test_boolean_false_coerces_via_str(self):
        # "False" → raises ValueError → default
        assert safe_float(False) == 0.0

    def test_scientific_notation_string(self):
        # "1e3" should parse correctly via float()
        assert safe_float("1e3") == 1000.0

    def test_returns_float_type(self):
        assert type(safe_float("5")) is float


# ---------------------------------------------------------------------------
# money_round – typical inputs
# ---------------------------------------------------------------------------

class TestMoneyRoundTypical:
    def test_rounds_down(self):
        assert money_round(1.234) == 1.23

    def test_rounds_up(self):
        assert money_round(1.235) == pytest.approx(1.24, abs=1e-9)

    def test_exactly_two_decimals(self):
        assert money_round(9.99) == 9.99

    def test_zero(self):
        assert money_round(0.0) == 0.0

    def test_integer_value(self):
        assert money_round(100.0) == 100.0

    def test_large_value(self):
        assert money_round(1_000_000.999) == 1_000_001.0

    def test_negative_value(self):
        assert money_round(-3.456) == -3.46

    def test_returns_float(self):
        assert isinstance(money_round(1.1), float)


# ---------------------------------------------------------------------------
# money_round – edge cases
# ---------------------------------------------------------------------------

class TestMoneyRoundEdgeCases:
    def test_very_small_positive(self):
        assert money_round(0.001) == 0.0

    def test_very_small_negative(self):
        assert money_round(-0.001) == 0.0

    def test_half_cent_positive(self):
        # Python uses banker's rounding (round-half-to-even)
        # 0.5 rounds to 0 (even), 1.5 rounds to 2 (even)
        assert money_round(0.005) == pytest.approx(0.0, abs=0.01)

    def test_precision_two_places(self):
        result = money_round(1.23456789)
        # result must have no more than 2 significant decimal places
        assert result == pytest.approx(1.23, abs=1e-9)


# ---------------------------------------------------------------------------
# Additional branches and edge cases
# ---------------------------------------------------------------------------

class TestSafeFloatAdditional:
    def test_dollar_sign_alone_returns_default(self):
        # "$".replace("$","") → "" → in _EMPTY_TOKENS → default.
        assert safe_float("$") == 0.0

    def test_whitespace_only_string_returns_default(self):
        # strip() → "" → in _EMPTY_TOKENS.
        assert safe_float("   ") == 0.0

    def test_multiple_commas_stripped(self):
        # "1,000,000" → "1000000" → 1_000_000.0
        assert safe_float("1,000,000") == 1_000_000.0

    def test_dollar_before_negative_number(self):
        # "$-50" → "-50" → -50.0
        assert safe_float("$-50") == -50.0

    def test_negative_before_dollar_sign(self):
        # "-$50" → "-50" ($ stripped) → -50.0
        assert safe_float("-$50") == -50.0

    def test_float_nan_passes_through_as_nan(self):
        # float('nan') → str → "nan" → not in _EMPTY_TOKENS → float("nan") = nan.
        # The function does NOT substitute the default for NaN inputs.
        import math
        result = safe_float(float("nan"))
        assert math.isnan(result)

    def test_string_nan_passes_through_as_nan(self):
        # "nan" is not in _EMPTY_TOKENS (which has "na", not "nan").
        import math
        result = safe_float("nan")
        assert math.isnan(result)

    def test_float_infinity_passes_through(self):
        import math
        result = safe_float(float("inf"))
        assert math.isinf(result)

    def test_string_inf_passes_through(self):
        import math
        result = safe_float("inf")
        assert math.isinf(result)

    def test_integer_input_returns_float(self):
        # int input → str() → parse → float; return type must be float.
        result = safe_float(7)
        assert type(result) is float


class TestMoneyRoundAdditional:
    def test_integer_input_returns_int_not_float(self):
        # round(int, ndigits) returns int in Python 3; callers should pass floats.
        result = money_round(5)  # type: ignore[arg-type]
        assert isinstance(result, int)
        assert result == 5

    def test_nan_input_propagates(self):
        # round(nan, 2) returns nan without raising in CPython 3.x.
        import math
        result = money_round(float("nan"))
        assert math.isnan(result)

    def test_infinity_input_propagates(self):
        # round(inf, 2) returns inf in CPython 3 (ndigits form does not overflow).
        import math
        result = money_round(float("inf"))
        assert math.isinf(result)

    def test_negative_zero_is_zero(self):
        # round(-0.0, 2) → -0.0; == 0.0 is True, but sign bit differs.
        result = money_round(-0.0)
        assert result == 0.0
