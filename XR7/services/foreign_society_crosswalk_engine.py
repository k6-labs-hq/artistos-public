from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.event import Event
from XR7.models.work import Work

_FOREIGN_SOCIETIES = ["PRS", "GEMA", "SACEM", "SOCAN", "APRA", "JASRAC"]


@dataclass
class ForeignCrosswalkReport:
    artist_id: str
    findings: list[dict[str, Any]]
    registration_packets: list[dict[str, Any]]


class ForeignSocietyCrosswalkEngine:
    def __init__(self, db: Session):
        self.db = db

    def analyze(self, artist_id: str) -> ForeignCrosswalkReport:
        works = self.db.query(Work).filter(Work.artist_id == artist_id).all()
        events = self.db.query(Event).filter(Event.artist_id == artist_id).all()
        foreign_events = [e for e in events if (e.territory or "US").upper() not in {"US", "USA"}]

        findings: list[dict[str, Any]] = []
        packets: list[dict[str, Any]] = []

        if foreign_events and not works:
            findings.append(
                {
                    "issue": "MISSING_FOREIGN_REGISTRATIONS",
                    "details": "Foreign usage detected with no catalog works available for registration crosswalk.",
                }
            )

        for w in works:
            if not w.isrc or not w.iswc:
                findings.append(
                    {
                        "work_id": w.id,
                        "issue": "MISMATCHED_ISRC_ISWC_ACROSS_SOCIETIES",
                        "details": "Work is missing ISRC or ISWC required for foreign society crosswalk.",
                    }
                )
            packets.append(
                {
                    "work_id": w.id,
                    "title": w.title,
                    "isrc": w.isrc,
                    "iswc": w.iswc,
                    "packet_type": "FOREIGN_REGISTRATION",
                    "target_societies": list(_FOREIGN_SOCIETIES),
                }
            )

        if foreign_events and len(foreign_events) > len(works):
            findings.append(
                {
                    "issue": "BLACK_BOX_ALLOCATION_RISK",
                    "details": "Foreign event volume exceeds registered work coverage, risk of black-box allocations.",
                    "event_count": len(foreign_events),
                    "registered_works": len(works),
                }
            )

        if foreign_events:
            findings.append(
                {
                    "issue": "MISSING_SUB_PUBLISHER_COLLECTIONS",
                    "details": "Foreign activity present; ensure sub-publisher collection mandates are on file.",
                    "territories": sorted(
                        {str(e.territory or "").upper() for e in foreign_events if e.territory}
                    ),
                }
            )

        return ForeignCrosswalkReport(
            artist_id=artist_id, findings=findings, registration_packets=packets
        )
