from __future__ import annotations

from typing import Any


def build_catalog_graph(
    *,
    works: list[dict[str, Any]],
    registrations: list[dict[str, Any]],
    statements: list[dict[str, Any]],
) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    seen_isrc: dict[str, str] = {}
    duplicates: list[dict[str, str]] = []
    missing_metadata: list[dict[str, Any]] = []

    for work in works:
        work_id = str(work.get("work_id") or work.get("id") or f"work-{len(nodes)+1}")
        isrc = (work.get("isrc") or "").strip()
        title = work.get("work_title") or work.get("title")

        nodes.append({"id": work_id, "type": "work", "title": title, "isrc": isrc})

        if not isrc or not title:
            missing_metadata.append(
                {
                    "work_id": work_id,
                    "missing": [k for k, v in {"isrc": isrc, "title": title}.items() if not v],
                }
            )

        if isrc:
            if isrc in seen_isrc and seen_isrc[isrc] != work_id:
                duplicates.append({"isrc": isrc, "work_a": seen_isrc[isrc], "work_b": work_id})
            else:
                seen_isrc[isrc] = work_id

    for reg in registrations:
        reg_id = str(reg.get("registration_id") or f"reg-{len(nodes)+1}")
        nodes.append({"id": reg_id, "type": "registration", "source": reg.get("source")})
        if reg.get("work_id"):
            edges.append({"from": str(reg.get("work_id")), "to": reg_id, "type": "registered_in"})

    for st in statements:
        st_id = str(st.get("statement_id") or f"statement-{len(nodes)+1}")
        nodes.append({"id": st_id, "type": "statement", "source": st.get("source")})
        if st.get("work_id"):
            edges.append({"from": str(st.get("work_id")), "to": st_id, "type": "appears_in"})

    ownership_conflicts = [
        {
            "work_id": w.get("work_id") or w.get("id"),
            "owner_a": w.get("owner"),
            "owner_b": w.get("alt_owner"),
        }
        for w in works
        if w.get("owner") and w.get("alt_owner") and w.get("owner") != w.get("alt_owner")
    ]

    return {
        "nodes": nodes,
        "edges": edges,
        "duplicates": duplicates,
        "missing_metadata": missing_metadata,
        "ownership_conflicts": ownership_conflicts,
    }
