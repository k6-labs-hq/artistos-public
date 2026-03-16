from __future__ import annotations

from typing import Any

from XR7.ugc.global_scanner import GlobalUGCScanner


class UGCRepairEngine:
    def __init__(self):
        self.scanner = GlobalUGCScanner()

    async def analyze(self, artist_id: str) -> dict[str, Any]:
        uses = await self.scanner.scan_global_uses(artist_id, days_back=365)
        findings: list[dict[str, Any]] = []
        actions: list[dict[str, Any]] = []

        for use in uses:
            views = float(use.get("views") or 0.0)
            platform = str(use.get("platform") or "").lower()
            use_id = str(use.get("use_id") or "")
            est = float(self.scanner.calculate_hidden_value(use) or 0.0)

            findings.append({
                "use_id": use_id,
                "platform": platform,
                "issue": "UNCLAIMED_VIDEO",
                "estimated_recoverable": round(est, 2),
            })
            if views > 100000:
                findings.append({
                    "use_id": use_id,
                    "platform": platform,
                    "issue": "MISSING_MONETIZATION_FLAG",
                    "details": "High-view UGC use should be monetized.",
                })
            if platform in {"youtube", "tiktok"} and views > 0:
                findings.append({
                    "use_id": use_id,
                    "platform": platform,
                    "issue": "MISSING_FINGERPRINT_MATCH",
                    "details": "Register or refresh audio fingerprint for this use cluster.",
                })

            actions.append(
                {
                    "use_id": use_id,
                    "platform": platform,
                    "auto_file_monetization_claim": True,
                    "auto_register_fingerprint": platform in {"youtube", "tiktok"},
                    "evidence_packet": self.scanner.auto_generate_evidence_packet(use),
                }
            )

        return {
            "artist_id": artist_id,
            "findings": findings,
            "auto_actions": actions,
            "auto_claim_count": len(actions),
        }
