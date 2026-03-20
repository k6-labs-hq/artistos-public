from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from XR7.ingestion.statement_parser import parse_csv
from XR7.ingestion.universal_schema import to_universal_royalty_event


@dataclass
class ParserOutput:
    parser_type: str
    event_count: int
    events: list[dict[str, Any]]
    warnings: list[str]


class BaseStatementParser:
    parser_type = "base"

    def parse(self, content: bytes, artist_id: str, filename: str) -> ParserOutput:
        raise RuntimeError("BaseStatementParser.parse must be implemented by a concrete parser")


class DistributorStatementParser(BaseStatementParser):
    parser_type = "distributor"

    def parse(self, content: bytes, artist_id: str, filename: str) -> ParserOutput:
        if filename.lower().endswith(".csv"):
            parsed = parse_csv(content, artist_id)
            events = [
                to_universal_royalty_event(
                    artist_id=artist_id,
                    source_type="distributor",
                    source_name=e.get("platform") or "distributor",
                    record_type="STATEMENT",
                    event_type=e.get("event_type", "STREAM"),
                    amount=float((e.get("unit_value") or 0.0) * (e.get("quantity") or 0.0)),
                    quantity=float(e.get("quantity") or 0.0),
                    currency=e.get("currency", "USD"),
                    territory=e.get("territory"),
                    isrc=e.get("isrc"),
                    work_title=e.get("work_title"),
                    metadata=e,
                )
                for e in parsed.events
            ]
            return ParserOutput(self.parser_type, len(events), events, parsed.errors)
        return ParserOutput(self.parser_type, 0, [], ["Unsupported distributor file type"]) 


class PROStatementParser(BaseStatementParser):
    parser_type = "pro"

    def parse(self, content: bytes, artist_id: str, filename: str) -> ParserOutput:
        return DistributorStatementParser().parse(content, artist_id, filename)


class PublisherStatementParser(BaseStatementParser):
    parser_type = "publisher"

    def parse(self, content: bytes, artist_id: str, filename: str) -> ParserOutput:
        return DistributorStatementParser().parse(content, artist_id, filename)


class MLCStatementParser(BaseStatementParser):
    parser_type = "mlc"

    def parse(self, content: bytes, artist_id: str, filename: str) -> ParserOutput:
        return DistributorStatementParser().parse(content, artist_id, filename)


def get_statement_parser(parser_type: str) -> BaseStatementParser:
    key = parser_type.strip().lower()
    mapping: dict[str, BaseStatementParser] = {
        "distributor": DistributorStatementParser(),
        "pro": PROStatementParser(),
        "publisher": PublisherStatementParser(),
        "mlc": MLCStatementParser(),
    }
    if key not in mapping:
        raise ValueError(f"Unsupported parser type '{parser_type}'")
    return mapping[key]
