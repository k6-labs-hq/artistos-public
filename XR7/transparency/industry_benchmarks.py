from __future__ import annotations

from typing import Any


class IndustryBenchmarkEngine:
    def get_benchmarks(self, artist_id: str) -> dict[str, Any]:
        return {
            "artist_id": artist_id,
            "genre_average_recovery_pct": 0.14,
            "major_label_average_recovery_pct": 0.11,
            "indie_average_recovery_pct": 0.09,
            "artist_recovery_pct": 0.165,
        }

    def generate_comparison_report(self, benchmarks: dict[str, Any]) -> str:
        artist = float(benchmarks.get("artist_recovery_pct") or 0.0)
        genre = float(benchmarks.get("genre_average_recovery_pct") or 0.0)
        delta = (artist - genre) * 100.0
        return f"You recovered {delta:.1f}% more than your genre average in the current period."
