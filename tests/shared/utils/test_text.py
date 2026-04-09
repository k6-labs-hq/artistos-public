"""Characterization tests for shared.utils.text.

Locks in the existing behaviour of decode_bytes().
No module code is changed here.
"""

from __future__ import annotations

import pytest

from shared.utils.text import decode_bytes

# ---------------------------------------------------------------------------
# decode_bytes – UTF-8
# ---------------------------------------------------------------------------


class TestDecodeBytesUtf8:
    def test_plain_ascii(self):
        assert decode_bytes(b"hello world") == "hello world"

    def test_utf8_multibyte(self):
        original = "café résumé"
        assert decode_bytes(original.encode("utf-8")) == original

    def test_utf8_emoji(self):
        original = "music \U0001f3b5"
        assert decode_bytes(original.encode("utf-8")) == original

    def test_empty_bytes(self):
        assert decode_bytes(b"") == ""

    def test_newlines_preserved(self):
        assert decode_bytes(b"line1\nline2\r\nline3") == "line1\nline2\r\nline3"


# ---------------------------------------------------------------------------
# decode_bytes – UTF-8 with BOM (utf-8-sig)
# ---------------------------------------------------------------------------


class TestDecodeBytesUtf8Bom:
    def test_bom_is_stripped(self):
        bom_bytes = b"\xef\xbb\xbfhello"
        result = decode_bytes(bom_bytes)
        assert result == "hello"
        assert not result.startswith("\ufeff")

    def test_utf8_sig_content_preserved(self):
        content = "أهلاً"
        bom_bytes = b"\xef\xbb\xbf" + content.encode("utf-8")
        assert decode_bytes(bom_bytes) == content


# ---------------------------------------------------------------------------
# decode_bytes – latin-1 fallback
# ---------------------------------------------------------------------------


class TestDecodeBytesLatin1:
    def test_latin1_only_bytes_decoded(self):
        # 0x80–0xFF range is valid latin-1 but invalid UTF-8
        latin1_bytes = bytes([0xE9, 0xE0, 0xFC])  # é à ü in latin-1
        result = decode_bytes(latin1_bytes)
        assert isinstance(result, str)
        assert len(result) == 3

    def test_latin1_specific_chars(self):
        # "é" in latin-1 is 0xE9
        result = decode_bytes(b"\xe9")
        assert result == "é"

    def test_invalid_utf8_falls_back_gracefully(self):
        # 0xFF is not valid in UTF-8
        bad_utf8 = b"\xff\xfe"
        result = decode_bytes(bad_utf8)
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# decode_bytes – errors parameter
# ---------------------------------------------------------------------------


class TestDecodeBytesErrorsParam:
    def test_default_errors_replace_used_as_fallback(self):
        # Bytes that are valid latin-1 will decode without invoking errors= at all;
        # the parameter applies to the final fallback attempt on truly bad sequences.
        result = decode_bytes(b"\xe9", errors="replace")
        assert isinstance(result, str)

    def test_errors_ignore_drops_bad_chars(self):
        # Build truly undecodable bytes for utf-8 and utf-8-sig,
        # then verify errors='ignore' produces a string (possibly empty for bad bytes)
        result = decode_bytes(b"\x80\x81", errors="ignore")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# decode_bytes – return type guarantee
# ---------------------------------------------------------------------------


class TestDecodeBytesReturnType:
    @pytest.mark.parametrize(
        "raw",
        [
            b"ascii",
            b"\xef\xbb\xbfbom",
            b"\xe9",
            b"",
        ],
    )
    def test_always_returns_str(self, raw):
        assert isinstance(decode_bytes(raw), str)


# ---------------------------------------------------------------------------
# Additional branches and edge cases
# ---------------------------------------------------------------------------


class TestDecodeBytesEncodingPriority:
    def test_bom_only_bytes_return_empty_string(self):
        # BOM with no payload → utf-8-sig strips BOM → empty string.
        assert decode_bytes(b"\xef\xbb\xbf") == ""

    def test_utf8_preferred_over_latin1_for_multibyte(self):
        # b"\xc3\xa9" is the UTF-8 encoding of é (U+00E9).
        # utf-8-sig / utf-8 should succeed giving 1 character, not 2 latin-1 chars.
        result = decode_bytes(b"\xc3\xa9")
        assert result == "é"
        assert len(result) == 1  # one Unicode code point, not two bytes

    def test_bom_with_invalid_utf8_falls_back_to_latin1(self):
        # BOM followed by 0xFF: utf-8-sig fails (0xFF is invalid in UTF-8/UTF-8-sig),
        # utf-8 also fails, so latin-1 handles the whole byte sequence.
        raw = b"\xef\xbb\xbf\xff"
        result = decode_bytes(raw)
        assert isinstance(result, str)
        # latin-1 encodes all 256 byte values; should not raise
        assert len(result) == 4  # BOM bytes (3) + \xff (1) all mapped 1-to-1

    def test_null_byte_decoded_as_null_character(self):
        # Null bytes are valid UTF-8; the function must not swallow them.
        result = decode_bytes(b"\x00")
        assert result == "\x00"
        assert len(result) == 1

    def test_mixed_ascii_and_latin1(self):
        # ASCII portion + high-byte; UTF-8 fails on the high byte, latin-1 used.
        raw = b"Price: \xa3100"  # \xa3 = £ in latin-1, invalid lone byte in UTF-8
        result = decode_bytes(raw)
        assert "Price:" in result
        assert "£" in result  # latin-1 0xa3 = £


class TestDecodeBytesErrorsArgScope:
    def test_errors_strict_on_valid_utf8_succeeds(self):
        # errors= is only forwarded to the final latin-1 call, but valid UTF-8
        # never reaches that call anyway.
        result = decode_bytes("hello".encode("utf-8"), errors="strict")
        assert result == "hello"

    def test_errors_strict_on_latin1_only_bytes_succeeds(self):
        # latin-1 accepts all 256 byte values, so strict will never raise here.
        raw = bytes(range(0x80, 0x100))  # entire high-byte range
        result = decode_bytes(raw, errors="strict")
        assert isinstance(result, str)
        assert len(result) == 128

    def test_errors_param_not_applied_to_utf8_attempt(self):
        # bytes that fail utf-8 but succeed in latin-1 must not propagate the
        # errors= flag during the failed utf-8 attempt (UnicodeDecodeError is
        # caught internally and the loop continues).
        raw = b"\x80\x81"  # invalid utf-8, valid latin-1
        result = decode_bytes(raw, errors="strict")
        assert isinstance(result, str)


class TestDecodeBytesRoundTrip:
    @pytest.mark.parametrize(
        "original",
        [
            "hello world",
            "café résumé",
            "日本語",
            "music \U0001f3b5",
            "\n\r\t",
        ],
    )
    def test_utf8_encode_then_decode_bytes_roundtrip(self, original):
        assert decode_bytes(original.encode("utf-8")) == original
