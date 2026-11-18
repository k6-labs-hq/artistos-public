"""Public-metadata sources used to resolve ISRC -> work -> ISWC/writers.

These adapters supply *evidence* for the reconciliation layer. They never
write to the catalog directly; callers decide what to do with a result.
"""

from XR7.ingestion.metadata_sources.models import (
    ResolvedWork,
    WorkContributor,
)
from XR7.ingestion.metadata_sources.musicbrainz import MusicBrainzClient
from XR7.ingestion.metadata_sources.reconcile import (
    MetadataFinding,
    StatementLine,
    reconcile_statement_lines,
)

__all__ = [
    "MusicBrainzClient",
    "ResolvedWork",
    "WorkContributor",
    "MetadataFinding",
    "StatementLine",
    "reconcile_statement_lines",
]
