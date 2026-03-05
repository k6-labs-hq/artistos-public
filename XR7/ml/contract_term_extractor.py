import re
from datetime import date


class ContractTermExtractor:
    """Lightweight rule-based contract term extractor for initial term snapshots."""

    _RATE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
    _TERRITORY_RE = re.compile(r"\b(worldwide|world wide|us|usa|uk|eu|global|japan|korea|france)\b", re.IGNORECASE)
    _RECOUP_RE = re.compile(r"\b(recoup(?:ment)?|reserve)\b", re.IGNORECASE)

    def extract(
        self,
        contract_text: str,
        effective_start: date | None = None,
        effective_end: date | None = None,
    ) -> list[dict]:
        terms: list[dict] = []
        text = contract_text or ""

        for match in self._RATE_RE.finditer(text):
            terms.append(
                {
                    "term_key": "royalty_rate_percent",
                    "term_value": match.group(1),
                    "confidence_score": 0.75,
                    "effective_start": effective_start,
                    "effective_end": effective_end,
                }
            )

        for match in self._TERRITORY_RE.finditer(text):
            terms.append(
                {
                    "term_key": "territory",
                    "term_value": match.group(1).upper().replace(" ", ""),
                    "confidence_score": 0.7,
                    "effective_start": effective_start,
                    "effective_end": effective_end,
                }
            )

        if self._RECOUP_RE.search(text):
            terms.append(
                {
                    "term_key": "recoupment_clause",
                    "term_value": "present",
                    "confidence_score": 0.65,
                    "effective_start": effective_start,
                    "effective_end": effective_end,
                }
            )

        # Deduplicate by key/value to avoid repeated regex hits in long contracts.
        deduped: dict[tuple[str, str], dict] = {}
        for term in terms:
            deduped[(term["term_key"], term["term_value"])] = term
        return list(deduped.values())
