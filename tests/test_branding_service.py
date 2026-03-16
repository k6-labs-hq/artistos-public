from __future__ import annotations

import uuid
from types import SimpleNamespace

from XR7.services.branding import (
    branding_observability_snapshot,
    get_branding_profile,
    reset_branding_observability,
)


class _FakeQuery:
    def __init__(self, row):
        self._row = row

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._row


class _FakeSession:
    def __init__(self, row):
        self.info = {}
        self._row = row

    def query(self, *args, **kwargs):
        return _FakeQuery(self._row)


def _profile_row(org_id: str, white_label_enabled: bool) -> SimpleNamespace:
    return SimpleNamespace(
        org_id=org_id,
        display_name="Demo Org",
        logo_url=None,
        primary_color=None,
        secondary_color=None,
        accent_color=None,
        dashboard_header_text=None,
        dashboard_footer_text=None,
        support_email=None,
        support_phone=None,
        legal_disclaimer=None,
        custom_domain=None,
        white_label_enabled=white_label_enabled,
    )


def test_branding_observability_records_missing_profile_event():
    reset_branding_observability()

    missing_org = f"org-missing-{uuid.uuid4().hex[:8]}"
    profile = get_branding_profile(_FakeSession(row=None), missing_org)

    assert profile["org_id"] == missing_org
    counters = branding_observability_snapshot()
    assert counters.get("missing_branding_profile", 0) >= 1


def test_branding_observability_records_white_label_disabled_event():
    reset_branding_observability()

    org_id = f"org-disabled-{uuid.uuid4().hex[:8]}"
    profile = get_branding_profile(_FakeSession(row=_profile_row(org_id, white_label_enabled=False)), org_id)

    assert profile["org_id"] == org_id
    counters = branding_observability_snapshot()
    assert counters.get("white_label_disabled", 0) >= 1
