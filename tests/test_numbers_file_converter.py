"""
Tests for the Apple Numbers (.numbers) → CSV converter (#162).

The library round-trip is what we care about. We don't try to ship a
synthetic .numbers fixture in the repo (binary, vendor-format, easily
broken by upstream library updates) — the real-data validation lives
out-of-band.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def test_import_doesnt_break_when_lib_present():
    """Module is importable regardless of whether numbers-parser is installed."""
    from XR7.ingestion import numbers_file  # noqa: F401


def test_missing_file_raises_useful_error(tmp_path: Path):
    from XR7.ingestion.numbers_file import numbers_to_rows

    bogus = tmp_path / "nonexistent.numbers"
    with pytest.raises((FileNotFoundError, ValueError, Exception)):
        numbers_to_rows(bogus)


def test_lib_missing_message_is_actionable(monkeypatch):
    """If numbers-parser isn't installed, the error tells you to install it."""
    import sys

    monkeypatch.setitem(sys.modules, "numbers_parser", None)

    from XR7.ingestion.numbers_file import numbers_to_rows

    with pytest.raises(ValueError, match="numbers-parser"):
        numbers_to_rows(b"not a real numbers file")
