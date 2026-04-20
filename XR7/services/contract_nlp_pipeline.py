from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from XR7.ml.contract_document_ingestion import ContractDocumentIngestion
from XR7.ml.contract_term_extractor import ContractTermExtractor


@dataclass(frozen=True)
class ContractExtractionResult:
    text: str
    method: str
    warnings: list[str]
    terms: list[dict]
    highlights: list[dict]


class ContractNLPPipeline:
    """Phase 2 contract intelligence pipeline (PDF text + OCR fallback + NLP extraction)."""

    def __init__(self) -> None:
        self._ingestion = ContractDocumentIngestion()
        self._extractor = ContractTermExtractor()

    def parse_uploaded_contract(
        self,
        *,
        filename: str,
        content: bytes,
        effective_start: date | None,
        effective_end: date | None,
    ) -> ContractExtractionResult:
        extracted = self._ingestion.extract_text(filename, content)
        text = str(extracted.get("text") or "")
        method = str(extracted.get("method") or "unknown")
        warnings = list(extracted.get("warnings") or [])
        terms, highlights = self._extractor.extract_with_highlights(
            contract_text=text,
            effective_start=effective_start,
            effective_end=effective_end,
        )
        return ContractExtractionResult(
            text=text,
            method=method,
            warnings=warnings,
            terms=terms,
            highlights=highlights,
        )
