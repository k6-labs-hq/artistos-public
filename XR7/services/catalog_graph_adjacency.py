from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.catalog_graph_adj import CatalogGraphEdge, CatalogGraphNode

XR7_CATALOG_NODE_TYPES: tuple[str, ...] = (
    "Work",
    "Recording",
    "Writer",
    "Publisher",
    "Distributor",
    "PRO",
    "MLC",
    "UGCPlatform",
    "Statement",
    "UsageEvent",
    "VarianceEvent",
)


@dataclass
class CatalogGraphPayload:
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]


class CatalogGraphAdjacencyService:
    """Builds and persists graph payloads using normalized adjacency tables."""

    def __init__(self, db: Session):
        self.db = db

    def persist(self, artist_id: str, payload: CatalogGraphPayload) -> dict[str, int]:
        ext_to_pk: dict[str, str] = {}
        created_nodes = 0
        created_edges = 0

        for node in payload.nodes:
            node_type = str(node.get("node_type") or "").strip()
            if node_type not in XR7_CATALOG_NODE_TYPES:
                continue
            external_id = str(node.get("id") or "").strip()
            if not external_id:
                continue

            existing = (
                self.db.query(CatalogGraphNode)
                .filter(
                    CatalogGraphNode.artist_id == artist_id,
                    CatalogGraphNode.node_type == node_type,
                    CatalogGraphNode.external_id == external_id,
                )
                .first()
            )

            if existing:
                existing.label = node.get("label") or existing.label
                existing.attributes_json = json.dumps(node.get("attributes") or {}, sort_keys=True)
                ext_to_pk[external_id] = existing.id
                continue

            row = CatalogGraphNode(
                artist_id=artist_id,
                node_type=node_type,
                external_id=external_id,
                label=node.get("label"),
                attributes_json=json.dumps(node.get("attributes") or {}, sort_keys=True),
            )
            self.db.add(row)
            self.db.flush()
            ext_to_pk[external_id] = row.id
            created_nodes += 1

        for edge in payload.edges:
            src_external = str(edge.get("source_id") or "").strip()
            dst_external = str(edge.get("target_id") or "").strip()
            edge_type = str(edge.get("edge_type") or "").strip()
            if not src_external or not dst_external or not edge_type:
                continue
            src_pk = ext_to_pk.get(src_external)
            dst_pk = ext_to_pk.get(dst_external)
            if not src_pk or not dst_pk:
                continue

            exists = (
                self.db.query(CatalogGraphEdge)
                .filter(
                    CatalogGraphEdge.artist_id == artist_id,
                    CatalogGraphEdge.source_node_id == src_pk,
                    CatalogGraphEdge.target_node_id == dst_pk,
                    CatalogGraphEdge.edge_type == edge_type,
                )
                .first()
            )
            if exists:
                exists.attributes_json = json.dumps(edge.get("attributes") or {}, sort_keys=True)
                continue

            self.db.add(
                CatalogGraphEdge(
                    artist_id=artist_id,
                    source_node_id=src_pk,
                    target_node_id=dst_pk,
                    edge_type=edge_type,
                    attributes_json=json.dumps(edge.get("attributes") or {}, sort_keys=True),
                )
            )
            created_edges += 1

        self.db.commit()
        return {"created_nodes": created_nodes, "created_edges": created_edges}

    def fetch(self, artist_id: str) -> CatalogGraphPayload:
        nodes = self.db.query(CatalogGraphNode).filter(CatalogGraphNode.artist_id == artist_id).all()
        edges = self.db.query(CatalogGraphEdge).filter(CatalogGraphEdge.artist_id == artist_id).all()

        node_map = {n.id: n.external_id for n in nodes}
        payload_nodes = [
            {
                "id": n.external_id,
                "node_type": n.node_type,
                "label": n.label,
                "attributes": json.loads(n.attributes_json or "{}"),
            }
            for n in nodes
        ]
        payload_edges = [
            {
                "source_id": node_map.get(e.source_node_id, e.source_node_id),
                "target_id": node_map.get(e.target_node_id, e.target_node_id),
                "edge_type": e.edge_type,
                "attributes": json.loads(e.attributes_json or "{}"),
            }
            for e in edges
        ]
        return CatalogGraphPayload(nodes=payload_nodes, edges=payload_edges)


def build_minimal_catalog_graph(works: Iterable[dict[str, Any]]) -> CatalogGraphPayload:
    """Create minimal Work/Writer/Publisher node graph from normalized work rows."""
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for w in works:
        work_id = str(w.get("work_id") or "")
        if not work_id:
            continue
        writer = str(w.get("writer_name") or "").strip()
        publisher = str(w.get("publisher_name") or "").strip()

        nodes.append({"id": work_id, "node_type": "Work", "label": w.get("title"), "attributes": w})
        if writer:
            writer_id = f"writer:{writer.lower()}"
            nodes.append({"id": writer_id, "node_type": "Writer", "label": writer, "attributes": {}})
            edges.append({"source_id": work_id, "target_id": writer_id, "edge_type": "written_by", "attributes": {}})
        if publisher:
            publisher_id = f"publisher:{publisher.lower()}"
            nodes.append({"id": publisher_id, "node_type": "Publisher", "label": publisher, "attributes": {}})
            edges.append(
                {"source_id": work_id, "target_id": publisher_id, "edge_type": "published_by", "attributes": {}}
            )

    # Deduplicate nodes by (id, node_type)
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for n in nodes:
        key = (str(n.get("id")), str(n.get("node_type")))
        unique[key] = n

    return CatalogGraphPayload(nodes=list(unique.values()), edges=edges)
