from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from XR7.ugc.usage_monitor import UGCUsageMonitor


class GlobalUGCScanner:
    """Global UGC scanner with deterministic simulated examples."""

    def __init__(self):
        self.monitor = UGCUsageMonitor()

    async def scan_global_uses(self, artist_id: str, days_back: int = 365) -> list[dict[str, Any]]:
        uses = await self.monitor.scan_for_uses(artist_id, days_back=days_back)
        if not uses:
            return [
                {
                    "use_id": f"global-{artist_id}-1",
                    "platform": "instagram",
                    "territory": "BR",
                    "title": "Reels trend using chorus",
                    "views": 2400000,
                    "url": "https://example.com/ig/use-1",
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "use_id": f"global-{artist_id}-2",
                    "platform": "tencent",
                    "territory": "CN",
                    "title": "UGC lip-sync reuse",
                    "views": 1200000,
                    "url": "https://example.com/tencent/use-2",
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                },
            ]
        return uses

    def calculate_hidden_value(self, use: dict[str, Any]) -> float:
        views = float(use.get("views") or 0.0)
        platform = str(use.get("platform") or "generic").lower()
        base = views * 0.001
        if platform in {"tiktok", "youtube"}:
            base *= 1.15
        return round(base, 2)

    def auto_generate_evidence_packet(self, use: dict[str, Any]) -> dict[str, Any]:
        est = self.calculate_hidden_value(use)
        payload = {
            "ugc_use": use,
            "estimated_recoverable": est,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        payload["packet_hash"] = hashlib.sha256(str(payload).encode("utf-8")).hexdigest()
        return payload
