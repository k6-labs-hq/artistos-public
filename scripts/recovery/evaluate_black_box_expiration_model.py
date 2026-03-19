from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone

from XR7.recovery.black_box_expiration import evaluate_black_box_expiration_for_anomaly


def _to_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate XR7 black-box expiration probability model metrics.")
    parser.add_argument("--csv", required=True, help="Validation CSV with columns: payer_or_society,royalty_type,event_date,redistributed_at")
    args = parser.parse_args()

    rows = []
    with open(args.csv, encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            rows.append(dict(row))

    if not rows:
        print(json.dumps({"count": 0, "brier_score": None, "mae_days": None}, indent=2))
        return

    brier = 0.0
    mae_days = 0.0
    now = datetime.now(timezone.utc)
    for row in rows:
        anomaly = {
            "payer": row.get("payer_or_society"),
            "royalty_type": row.get("royalty_type"),
            "event_date": row.get("event_date"),
        }
        pred = evaluate_black_box_expiration_for_anomaly(anomaly, as_of=now)
        p = float(pred.get("P_already_redistributed") or 0.0)
        y = 1.0 if _to_dt(str(row.get("redistributed_at"))) <= now else 0.0
        brier += (p - y) ** 2

        p50 = pred.get("p50_expiration_date")
        if p50:
            mae_days += abs((_to_dt(str(p50)) - _to_dt(str(row.get("redistributed_at")))).days)

    result = {
        "count": len(rows),
        "brier_score": round(brier / len(rows), 6),
        "mae_days": round(mae_days / len(rows), 4),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
