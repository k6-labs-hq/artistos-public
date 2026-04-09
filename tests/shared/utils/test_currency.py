"""Characterization tests for shared.utils.currency.

Locks in the existing behaviour of coerce_currency().
No module code is changed here.
"""

from __future__ import annotations

from shared.utils.currency import coerce_currency

# ---------------------------------------------------------------------------
# coerce_currency – typical inputs
# ---------------------------------------------------------------------------


class TestCoerceCurrencyTypical:
    def test_lowercase_usd_uppercased(self):
        assert coerce_currency("usd") == "USD"

    def test_mixed_case_uppercased(self):
        assert coerce_currency("Eur") == "EUR"

    def test_already_uppercase(self):
        assert coerce_currency("GBP") == "GBP"

    def test_known_codes_returned_as_is(self):
        known = [
            "USD",
            "EUR",
            "GBP",
            "CAD",
            "AUD",
            "JPY",
            "CHF",
            "SEK",
            "NOK",
            "DKK",
            "NZD",
            "HKD",
            "SGD",
            "MXN",
            "BRL",
            "ZAR",
            "INR",
            "KRW",
            "CNY",
        ]
        for code in known:
            assert coerce_currency(code) == code

    def test_unknown_code_uppercased_and_returned(self):
        # Lenient: unknown codes are still uppercased and passed through
        assert coerce_currency("xyz") == "XYZ"

    def test_unknown_code_preserved(self):
        assert coerce_currency("FOO") == "FOO"


# ---------------------------------------------------------------------------
# coerce_currency – None / empty → fallback
# ---------------------------------------------------------------------------


class TestCoerceCurrencyFallback:
    def test_none_returns_usd(self):
        assert coerce_currency(None) == "USD"

    def test_empty_string_returns_usd(self):
        assert coerce_currency("") == "USD"

    def test_zero_int_returns_fallback(self):
        # 0 is falsy → treated as empty
        assert coerce_currency(0) == "USD"

    def test_false_returns_fallback(self):
        assert coerce_currency(False) == "USD"

    def test_whitespace_only_returns_fallback(self):
        # "   ".strip() == "" → empty → fallback
        assert coerce_currency("   ") == "USD"

    def test_custom_fallback_used_for_none(self):
        assert coerce_currency(None, fallback="EUR") == "EUR"

    def test_custom_fallback_used_for_empty(self):
        assert coerce_currency("", fallback="GBP") == "GBP"


# ---------------------------------------------------------------------------
# coerce_currency – whitespace stripping
# ---------------------------------------------------------------------------


class TestCoerceCurrencyStripping:
    def test_leading_whitespace_stripped(self):
        assert coerce_currency("  usd") == "USD"

    def test_trailing_whitespace_stripped(self):
        assert coerce_currency("eur  ") == "EUR"

    def test_surrounding_whitespace_stripped(self):
        assert coerce_currency("  gbp  ") == "GBP"


# ---------------------------------------------------------------------------
# coerce_currency – return type
# ---------------------------------------------------------------------------


class TestCoerceCurrencyReturnType:
    def test_always_returns_str(self):
        assert isinstance(coerce_currency("usd"), str)
        assert isinstance(coerce_currency(None), str)
        assert isinstance(coerce_currency(""), str)


# ---------------------------------------------------------------------------
# Additional branches and edge cases
# ---------------------------------------------------------------------------


class TestCoerceCurrencySecondFallbackBranch:
    def test_tab_whitespace_hits_second_fallback(self):
        # "\t" is truthy so `if not value` is False; strip() → "" → second fallback.
        assert coerce_currency("\t") == "USD"

    def test_newline_whitespace_hits_second_fallback(self):
        assert coerce_currency("\n") == "USD"

    def test_tab_with_custom_fallback(self):
        assert coerce_currency("\t", fallback="EUR") == "EUR"


class TestCoerceCurrencyNonStringTruthyInputs:
    def test_truthy_integer_returns_string_representation(self):
        # Non-zero int is truthy → str(42).strip().upper() → "42".
        # The function is lenient; callers are responsible for passing valid codes.
        assert coerce_currency(42) == "42"

    def test_boolean_true_returns_true_string(self):
        # True is truthy → str(True).upper() → "TRUE".
        assert coerce_currency(True) == "TRUE"

    def test_non_zero_float_returns_string(self):
        assert coerce_currency(1.0) == "1.0"


class TestCoerceCurrencyEmbeddedWhitespace:
    def test_code_with_internal_space_not_stripped(self):
        # strip() only removes leading/trailing whitespace; internal spaces remain.
        result = coerce_currency("U S D")
        assert result == "U S D"  # lenient passthrough

    def test_code_with_embedded_newline_not_stripped(self):
        result = coerce_currency("US\nD")
        assert result == "US\nD"


class TestCoerceCurrencyCustomFallbackTypes:
    def test_custom_fallback_returned_verbatim_for_none(self):
        # fallback value is returned as-is, no normalisation applied.
        assert coerce_currency(None, fallback="eur") == "eur"

    def test_custom_fallback_is_not_uppercased(self):
        # The fallback path bypasses the upper() call.
        result = coerce_currency("", fallback="eur")
        assert result == "eur"  # lowercase preserved
