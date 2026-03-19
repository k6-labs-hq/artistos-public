from __future__ import annotations

import argparse
import csv
import json

from XR7.recovery.black_box_expiration import BlackBoxExpirationProbabilityModel, SocietyBehaviorCalibrationJob


def main() -> None:
    parser = argparse.ArgumentParser(description="Quarterly society behavior calibration job.")
    parser.add_argument("--csv", required=True, help="Confirmed redistribution events CSV")
    args = parser.parse_args()

    rows = []
    with open(args.csv, encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            rows.append(dict(row))

    model = BlackBoxExpirationProbabilityModel()
    job = SocietyBehaviorCalibrationJob(model)
    result = job.recalibrate(rows)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
