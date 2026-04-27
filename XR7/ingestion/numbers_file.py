"""Apple Numbers (.numbers) → CSV bytes converter.

The MLC ships member statements as Apple iWork Numbers files by default.
Those are zip-wrapped binary protobuf, not directly parseable by csv. The
``numbers-parser`` library reads them; this module wraps it so the rest of
the ingestion pipeline (which is CSV-based) doesn't need to know about
iWork formats.

Usage:
    csv_bytes = numbers_to_csv_bytes(path_or_bytes)
    result = parse_csv(csv_bytes, artist_id="...")
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any


def numbers_to_csv_bytes(source: Path | bytes) -> bytes:
    """Convert an Apple Numbers file to CSV bytes.

    Reads the first table of the first sheet. If a workbook has multiple
    sheets/tables, callers can use ``numbers_to_rows`` directly with a
    sheet/table selector.

    Args:
        source: Either a Path to a ``.numbers`` file, or its raw bytes.

    Returns:
        UTF-8 encoded CSV bytes ready to feed into ``parse_csv``.

    Raises:
        ValueError: If the file isn't a valid Numbers document.
    """
    rows = numbers_to_rows(source)
    if not rows:
        return b""
    # Build CSV from the row dicts. Header order = first row's keys.
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def numbers_to_rows(source: Path | bytes) -> list[dict[str, Any]]:
    """Read a Numbers file and return rows as a list of dicts (header→value).

    The first row is always treated as the header; subsequent rows are
    coerced to strings so downstream parsers (which expect CSV-style
    string values) work uniformly.
    """
    try:
        from numbers_parser import Document
    except ImportError as exc:
        raise ValueError(
            "numbers-parser library not installed. Add 'numbers-parser' to "
            "requirements.txt to ingest .numbers files."
        ) from exc

    if isinstance(source, bytes):
        # numbers-parser only accepts paths; write to a temp file.
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".numbers", delete=False) as tmp:
            tmp.write(source)
            tmp_path = Path(tmp.name)
        try:
            doc = Document(str(tmp_path))
        finally:
            tmp_path.unlink(missing_ok=True)
    else:
        doc = Document(str(source))

    sheets = doc.sheets
    if not sheets:
        return []
    tables = sheets[0].tables
    if not tables:
        return []

    table = tables[0]
    all_rows = list(table.rows())
    if not all_rows:
        return []

    header = [str(c.value) if c.value is not None else "" for c in all_rows[0]]
    rows: list[dict[str, Any]] = []
    for row_cells in all_rows[1:]:
        # Skip totally empty rows.
        values = [c.value for c in row_cells]
        if all(v is None or v == "" for v in values):
            continue
        rows.append({header[i]: ("" if v is None else str(v)) for i, v in enumerate(values)})
    return rows
