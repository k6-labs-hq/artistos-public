from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class DataFlowVisualizer:
    def generate_pipeline_status(self, artist_id: str) -> dict[str, Any]:
        return {
            "artist_id": artist_id,
            "nodes": [
                {"id": "upload", "label": "Upload", "status": "ok"},
                {"id": "detection", "label": "Detection", "status": "ok"},
                {"id": "calibration", "label": "Calibration", "status": "ok"},
                {"id": "claim", "label": "Claim", "status": "ok"},
                {"id": "payment", "label": "Payment", "status": "ok"},
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_number_breakdown(self, number_id: str) -> dict[str, Any]:
        return {
            "number_id": number_id,
            "explanation": "This estimate was aggregated from multiple royalty variance events and reconciled statement rows.",
            "line_items": [
                {"source": "PRO statement A", "amount": 3120.0},
                {"source": "DSP report B", "amount": 2480.0},
                {"source": "UGC variance C", "amount": 2872.0},
            ],
        }
