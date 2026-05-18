from __future__ import annotations

import csv
import io
import json
from typing import Any

from openpyxl import load_workbook


def _norm(v: str) -> str:
    return str(v or "").strip().lower().replace("_", " ")


def _parse_tabular(content: bytes, filename: str) -> list[dict[str, str]]:
    lower = (filename or "").strip().lower()
    if lower.endswith(".xlsx"):
        wb = load_workbook(filename=io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []
        headers = [_norm(str(h or "")) for h in rows[0]]
        out: list[dict[str, str]] = []
        for row in rows[1:301]:
            item: dict[str, str] = {}
            for i, h in enumerate(headers):
                if not h:
                    continue
                item[h] = str(row[i] or "").strip() if i < len(row) else ""
            if any(item.values()):
                out.append(item)
        return out

    raw = content.decode("utf-8", errors="ignore")
    # newline="" so the csv module handles line endings — a CR-only file
    # (classic-Mac TSV exports) otherwise raises csv.Error. See the same
    # fix in statement_parser.parse_csv / parse_delimited.
    if "\t" in raw and lower.endswith(".tsv"):
        reader = csv.DictReader(io.StringIO(raw, newline=""), delimiter="\t")
    else:
        reader = csv.DictReader(io.StringIO(raw, newline=""))
    out = []
    try:
        for i, row in enumerate(reader):
            if i >= 300:
                break
            normed = {_norm(k): str(v or "").strip() for k, v in row.items() if k is not None}
            if any(normed.values()):
                out.append(normed)
    except csv.Error:
        # Signal extraction is best-effort analytics — never block ingestion
        # on a malformed file. The parser proper reports parse errors.
        return out
    return out


def _first_non_empty(rows: list[dict[str, str]], keys: list[str]) -> str | None:
    keyset = {_norm(k) for k in keys}
    for row in rows:
        for k, v in row.items():
            if _norm(k) in keyset and v:
                return v.strip()
    return None


def _collect_values(rows: list[dict[str, str]], keys: list[str], *, limit: int = 20) -> list[str]:
    keyset = {_norm(k) for k in keys}
    seen: list[str] = []
    for row in rows:
        for k, v in row.items():
            if _norm(k) in keyset and v:
                vv = v.strip()
                if vv and vv not in seen:
                    seen.append(vv)
                if len(seen) >= limit:
                    return seen
    return seen


def _infer_artist_name(rows: list[dict[str, str]]) -> str | None:
    direct = _first_non_empty(
        rows,
        [
            "artist",
            "artist name",
            "primary artist",
            "performer",
            "band",
            "account name",
            "account holder",
        ],
    )
    if direct:
        return direct

    # Fallback from frequent title ownership-like columns.
    candidates = _collect_values(rows, ["label", "publisher", "account", "profile name"], limit=8)
    if candidates:
        return candidates[0]
    return None


def extract_statement_signals(
    content: bytes, filename: str, *, format_detected: str | None = None
) -> dict[str, Any]:
    rows = _parse_tabular(content, filename)
    if not rows:
        return {
            "artist_name": None,
            "email": None,
            "distributor_account_id": None,
            "pro_writer_id": None,
            "distributor_list": [],
            "pro_affiliations": [],
            "label_publishers": [],
            "catalog_titles": [],
            "isrcs": [],
            "iswcs": [],
            "upcs": [],
            "source_format": format_detected or "unknown",
        }

    artist_name = _infer_artist_name(rows)
    email = _first_non_empty(rows, ["email", "contact email", "account email", "user email"])
    distributor_account_id = _first_non_empty(
        rows,
        ["distributor account id", "account id", "partner account id", "profile id", "artist id"],
    )
    pro_writer_id = _first_non_empty(
        rows, ["pro writer id", "writer id", "ipi", "cae", "ipi number"]
    )

    distributor_list = _collect_values(
        rows,
        ["distributor", "store", "platform", "retailer", "source", "payer", "service"],
    )
    pro_affiliations = _collect_values(
        rows, ["pro", "society", "collecting society", "payer"], limit=10
    )
    labels = _collect_values(rows, ["label", "publisher", "publishing", "rights holder"], limit=20)
    titles = _collect_values(
        rows, ["title", "track title", "track name", "song", "work title"], limit=25
    )
    isrcs = _collect_values(rows, ["isrc"], limit=50)
    iswcs = _collect_values(rows, ["iswc"], limit=50)
    upcs = _collect_values(rows, ["upc", "ean"], limit=50)

    # If explicit format indicates PRO and pro affiliation list is sparse, infer from format.
    fmt = (format_detected or "").strip().lower()
    if fmt in {"ascap", "bmi"} and fmt.upper() not in {p.upper() for p in pro_affiliations}:
        pro_affiliations.append(fmt.upper())

    # If distributor list is empty, infer from source format.
    if not distributor_list and fmt and fmt not in {"ascap", "bmi", "generic"}:
        distributor_list = [fmt]

    return {
        "artist_name": artist_name,
        "email": email,
        "distributor_account_id": distributor_account_id,
        "pro_writer_id": pro_writer_id,
        "distributor_list": distributor_list,
        "pro_affiliations": pro_affiliations,
        "label_publishers": labels,
        "catalog_titles": titles,
        "isrcs": isrcs,
        "iswcs": iswcs,
        "upcs": upcs,
        "source_format": fmt or "unknown",
        "row_sample_count": len(rows),
    }


def merge_statement_signals(items: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, Any] = {
        "artist_name": None,
        "email": None,
        "distributor_account_id": None,
        "pro_writer_id": None,
        "distributor_list": [],
        "pro_affiliations": [],
        "label_publishers": [],
        "catalog_titles": [],
        "isrcs": [],
        "iswcs": [],
        "upcs": [],
        "source_formats": [],
    }
    if not items:
        return merged

    def _uniq_extend(key: str, vals: list[str]) -> None:
        cur = list(merged.get(key) or [])
        for v in vals:
            if v and v not in cur:
                cur.append(v)
        merged[key] = cur

    for item in items:
        if not merged["artist_name"] and item.get("artist_name"):
            merged["artist_name"] = item.get("artist_name")
        if not merged["email"] and item.get("email"):
            merged["email"] = item.get("email")
        if not merged["distributor_account_id"] and item.get("distributor_account_id"):
            merged["distributor_account_id"] = item.get("distributor_account_id")
        if not merged["pro_writer_id"] and item.get("pro_writer_id"):
            merged["pro_writer_id"] = item.get("pro_writer_id")

        _uniq_extend("distributor_list", list(item.get("distributor_list") or []))
        _uniq_extend("pro_affiliations", list(item.get("pro_affiliations") or []))
        _uniq_extend("label_publishers", list(item.get("label_publishers") or []))
        _uniq_extend("catalog_titles", list(item.get("catalog_titles") or []))
        _uniq_extend("isrcs", list(item.get("isrcs") or []))
        _uniq_extend("iswcs", list(item.get("iswcs") or []))
        _uniq_extend("upcs", list(item.get("upcs") or []))

        fmt = item.get("source_format")
        if fmt and fmt not in merged["source_formats"]:
            merged["source_formats"].append(fmt)

    return merged


def to_json(signals: dict[str, Any]) -> str:
    return json.dumps(signals, sort_keys=True)
