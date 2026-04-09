from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime, timezone
from typing import Any


class PublicTransparencyAPI:
    def get_public_aggregates(self) -> dict[str, Any]:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_recovered": 128450000.0,
            "average_uplift_by_genre": {"country": 0.17, "hiphop": 0.19, "edm": 0.15},
            "common_anomaly_types": ["missing_mechanical", "split_conflict", "ugc_sync_gap"],
        }

    def generate_advocacy_kit(self, artist_id: str) -> bytes:
        buf = io.BytesIO()
        aggregates = self.get_public_aggregates()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                "your_story.md", f"# Advocacy Story for {artist_id}\n\nTemplate narrative here."
            )
            zf.writestr("public_aggregates.json", json.dumps(aggregates, indent=2))
            zf.writestr("pro_reform_letter_template.md", "# PRO Reform Letter\n\nDear ...")
        return buf.getvalue()
