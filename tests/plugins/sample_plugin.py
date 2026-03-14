from __future__ import annotations


def parse(content: bytes, artist_id: str, filename: str) -> dict:
    text = content.decode("utf-8", errors="ignore")
    lines = [line for line in text.splitlines() if line.strip()]
    return {
        "parser_type": "custom_partner",
        "warnings": [],
        "events": [
            {
                "artist_id": artist_id,
                "source_type": "plugin",
                "source_name": "custom_partner",
                "record_type": "STATEMENT",
                "event_type": "ROYALTY_EVENT",
                "amount": float(len(lines)),
                "quantity": float(max(1, len(lines) - 1)),
                "unit_value": 1.0,
                "currency": "USD",
                "metadata": {"filename": filename},
            }
        ],
    }
