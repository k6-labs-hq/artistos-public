from __future__ import annotations

import argparse
import json

from XR7.recovery.black_box_expiration import (
    export_black_box_model_snapshot,
    train_black_box_expiration_probability_model_from_csv,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train XR7 black-box expiration probability model from CSV.")
    parser.add_argument("--csv", required=True, help="Path to CSV with payer_or_society,royalty_type,event_date,redistributed_at")
    parser.add_argument("--out", default="", help="Optional output JSON path for model snapshot")
    args = parser.parse_args()

    result = train_black_box_expiration_probability_model_from_csv(args.csv)
    snapshot = export_black_box_model_snapshot()
    payload = {"training": result, "snapshot": snapshot}

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fp:
            json.dump(payload, fp, indent=2)
    else:
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
