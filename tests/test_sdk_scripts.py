from __future__ import annotations

from pathlib import Path


def test_sdk_scripts_exist_and_executable():
    root = Path(__file__).resolve().parents[1]
    paths = [
        root / "scripts" / "generate_sdks.sh",
        root / "scripts" / "generate_sdk_python.sh",
        root / "scripts" / "generate_sdk_typescript.sh",
    ]
    for p in paths:
        assert p.exists(), f"Missing script: {p}"
