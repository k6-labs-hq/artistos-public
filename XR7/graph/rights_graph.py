import networkx as nx


class RightsGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_artist(self, artist) -> None:
        self.graph.add_node(str(artist.id), type="artist", name=artist.name, data=artist)

    def add_work(self, work) -> None:
        self.graph.add_node(str(work.id), type="work", title=work.title, data=work)
        self.graph.add_edge(str(work.artist_id), str(work.id), relationship="owns")

    def add_contract(self, contract) -> None:
        self.graph.add_node(
            str(contract.id), type="contract", contract_type=contract.contract_type, data=contract
        )
        self.graph.add_edge(str(contract.artist_id), str(contract.id), relationship="party_to")

    def add_relationship(
        self, node_a_id: str, node_b_id: str, relationship_type: str, **attrs
    ) -> None:
        self.graph.add_edge(str(node_a_id), str(node_b_id), relationship=relationship_type, **attrs)

    def get_rights_for_work(self, work_id: str) -> list[dict]:
        if work_id not in self.graph:
            return []
        self.graph.nodes[work_id]
        artist_id = None
        for pred in self.graph.predecessors(work_id):
            if self.graph.nodes[pred].get("type") == "artist":
                artist_id = pred
                break
        if not artist_id:
            return []
        contracts = []
        for succ in self.graph.successors(artist_id):
            node = self.graph.nodes[succ]
            if node.get("type") == "contract":
                contracts.append(
                    {
                        "contract_id": succ,
                        "contract_type": node.get("contract_type"),
                        "data": node.get("data"),
                    }
                )
        return contracts

    def resolve_expected_payment(
        self, work_id: str, event_type: str, territory: str | None = None
    ) -> dict:
        contracts = self.get_rights_for_work(work_id)
        result = {
            "work_id": work_id,
            "event_type": event_type,
            "territory": territory,
            "applicable_contracts": [],
        }
        for c in contracts:
            data = c.get("data")
            terms = getattr(data, "terms", {}) or {}
            rate = terms.get("rate", 0.0)
            split = terms.get("artist_split", 1.0)
            result["applicable_contracts"].append(
                {
                    "contract_id": c["contract_id"],
                    "contract_type": c["contract_type"],
                    "rate": rate,
                    "artist_split": split,
                }
            )
        return result

    def get_artist_works(self, artist_id: str) -> list[dict]:
        if artist_id not in self.graph:
            return []
        works = []
        for succ in self.graph.successors(artist_id):
            node = self.graph.nodes[succ]
            if node.get("type") == "work":
                works.append({"work_id": succ, **{k: v for k, v in node.items() if k != "data"}})
        return works

    def resolve_identity(self, name_or_alias: str) -> dict | None:
        for node_id, data in self.graph.nodes(data=True):
            if data.get("type") == "artist":
                artist = data.get("data")
                if artist:
                    if getattr(artist, "name", "").lower() == name_or_alias.lower():
                        return {
                            "artist_id": node_id,
                            **{k: v for k, v in data.items() if k != "data"},
                        }
                    stage_names = getattr(artist, "stage_names", []) or []
                    if name_or_alias.lower() in [s.lower() for s in stage_names]:
                        return {
                            "artist_id": node_id,
                            **{k: v for k, v in data.items() if k != "data"},
                        }
        return None
