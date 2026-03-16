from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class KPopGlobalScanner:
    async def scan_melon_tencent_boomplay_uses(self, artist_id: str) -> list[dict[str, Any]]:
        return [
            {
                "use_id": f"kpop-{artist_id}-1",
                "platform": "melon",
                "territory": "KR",
                "title": "Dance challenge use",
                "views": 2200000,
                "detected_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "use_id": f"kpop-{artist_id}-2",
                "platform": "tencent",
                "territory": "CN",
                "title": "Clip reuse with fan sub edits",
                "views": 1700000,
                "detected_at": datetime.now(timezone.utc).isoformat(),
            },
        ]

    def cross_reference_multi_territory_pros(self, uses: list[dict[str, Any]]) -> dict[str, Any]:
        by_territory: dict[str, int] = {}
        for u in uses:
            territory = str(u.get("territory") or "GLOBAL")
            by_territory[territory] = by_territory.get(territory, 0) + 1
        return {"territory_counts": by_territory}

    def auto_evidence_and_micro_royalty_forecast(self, use: dict[str, Any]) -> dict[str, Any]:
        views = float(use.get("views") or 0.0)
        est = round(views * 0.0011, 2)
        return {"ugc_use": use, "micro_royalty_estimate": est}
