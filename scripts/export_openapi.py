from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from XR7.api.app import app


def main() -> None:
    out = Path("openapi/openapi.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    spec = app.openapi()
    out.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print(f"Wrote OpenAPI spec to {out}")


if __name__ == "__main__":
    main()
