"""Claim reference_number — human-readable XR7-YYYY-XXXXXX format."""

from __future__ import annotations

import re

from XR7.models.claim import _generate_claim_reference


def test_format_matches_xr7_year_hex():
    ref = _generate_claim_reference()
    assert re.match(r"^XR7-\d{4}-[0-9A-F]{6}$", ref), f"unexpected format: {ref}"


def test_two_calls_produce_different_references():
    refs = {_generate_claim_reference() for _ in range(20)}
    # 20 random draws from 16M-value space — collision is astronomically
    # unlikely. If this test ever fails, secrets.token_hex got broken.
    assert len(refs) == 20


def test_year_is_current():
    from datetime import datetime, timezone

    ref = _generate_claim_reference()
    year = ref.split("-")[1]
    assert year == str(datetime.now(timezone.utc).year)
