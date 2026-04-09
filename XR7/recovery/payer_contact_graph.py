from __future__ import annotations


def payer_contacts(payer_id: str) -> dict:
    """Return payer contacts/escalation paths and dispute portal metadata."""
    key = str(payer_id or "generic").strip().lower()
    defaults = {
        "support_email": f"disputes@{key}.com" if key != "generic" else "disputes@example.com",
        "escalation_email": (
            f"escalations@{key}.com" if key != "generic" else "escalations@example.com"
        ),
        "legal_email": f"legal@{key}.com" if key != "generic" else "legal@example.com",
        "dispute_portal": (
            f"https://portal.{key}.com/disputes"
            if key != "generic"
            else "https://portal.example.com/disputes"
        ),
        "sla_expectations_days": 30,
        "historical_responsiveness": "medium",
    }
    if key in {"spotify", "distrokid", "tunecore", "ascap", "bmi", "sesac"}:
        defaults["sla_expectations_days"] = (
            21 if key in {"spotify", "distrokid", "tunecore"} else 45
        )
        defaults["historical_responsiveness"] = (
            "high" if key in {"spotify", "tunecore"} else "medium"
        )
    return {"payer_id": payer_id, **defaults}
