import re
from datetime import date


class ContractTermExtractor:
    """Lightweight rule-based contract term extractor for initial term snapshots."""

    _RATE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
    _MIN_GUARANTEE_RE = re.compile(
        r"(?:minimum\s+guarantee|min\.?\s+guarantee)\s*(?:of)?\s*\$?([\d,]+(?:\.\d+)?)",
        re.IGNORECASE,
    )
    _ESCALATOR_RE = re.compile(
        r"(?:escalat(?:or|ion)|step\s*up)\s*(?:to)?\s*(\d+(?:\.\d+)?)\s*%", re.IGNORECASE
    )
    _TERRITORY_RE = re.compile(
        r"\b(worldwide|world wide|us|usa|uk|eu|global|japan|korea|france)\b", re.IGNORECASE
    )
    _RECOUP_RE = re.compile(r"\b(recoup(?:ment)?|reserve)\b", re.IGNORECASE)
    _AUDIT_RE = re.compile(
        r"\b(audit\s+right[s]?|right\s+to\s+audit|books\s+and\s+records)\b", re.IGNORECASE
    )
    _MFN_RE = re.compile(r"\b(most\s+favou?red\s+nation|mfn)\b", re.IGNORECASE)
    _RECOUP_TRAP_RE = re.compile(
        r"\b(cross[-\s]?collateral(?:ization)?|perpetual\s+recoup(?:ment)?)\b", re.IGNORECASE
    )

    def extract_with_highlights(
        self,
        contract_text: str,
        effective_start: date | None = None,
        effective_end: date | None = None,
    ) -> tuple[list[dict], list[dict]]:
        """Return extracted terms plus highlighted clause spans for UI review."""
        text = contract_text or ""
        terms = self.extract(text, effective_start=effective_start, effective_end=effective_end)
        highlights: list[dict] = []

        for match in self._RATE_RE.finditer(text):
            highlights.append(
                {
                    "clause_type": "rate",
                    "matched_text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence_score": 0.75,
                }
            )

        for regex, ctype, conf in (
            (self._RECOUP_RE, "recoupment", 0.65),
            (self._AUDIT_RE, "audit_rights", 0.7),
            (self._MIN_GUARANTEE_RE, "minimum_guarantee", 0.72),
            (self._ESCALATOR_RE, "escalator", 0.68),
        ):
            for match in regex.finditer(text):
                start = max(0, match.start() - 80)
                end = min(len(text), match.end() + 80)
                highlights.append(
                    {
                        "clause_type": ctype,
                        "matched_text": text[start:end],
                        "start": start,
                        "end": end,
                        "confidence_score": conf,
                    }
                )

        return terms, highlights

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

        if self._AUDIT_RE.search(text):
            terms.append(
                {
                    "term_key": "audit_rights_clause",
                    "term_value": "present",
                    "confidence_score": 0.7,
                    "effective_start": effective_start,
                    "effective_end": effective_end,
                }
            )

        for match in self._MIN_GUARANTEE_RE.finditer(text):
            raw = str(match.group(1)).replace(",", "")
            terms.append(
                {
                    "term_key": "minimum_guarantee",
                    "term_value": raw,
                    "confidence_score": 0.72,
                    "effective_start": effective_start,
                    "effective_end": effective_end,
                }
            )

        for match in self._ESCALATOR_RE.finditer(text):
            terms.append(
                {
                    "term_key": "escalator_rate_percent",
                    "term_value": match.group(1),
                    "confidence_score": 0.68,
                    "effective_start": effective_start,
                    "effective_end": effective_end,
                }
            )

        # Deduplicate by key/value to avoid repeated regex hits in long contracts.
        deduped: dict[tuple[str, str], dict] = {}
        for term in terms:
            deduped[(term["term_key"], term["term_value"])] = term
        return list(deduped.values())

    def pre_signature_review(self, contract_text: str) -> dict:
        """Return future-underpayment risk score and redline recommendations."""
        text = contract_text or ""
        terms = self.extract(text)

        rate_values = [
            float(t["term_value"]) for t in terms if t.get("term_key") == "royalty_rate_percent"
        ]
        has_escalator = any(t.get("term_key") == "escalator_rate_percent" for t in terms)
        has_audit = any(t.get("term_key") == "audit_rights_clause" for t in terms) or bool(
            self._AUDIT_RE.search(text)
        )
        has_mfn = bool(self._MFN_RE.search(text))
        has_recoup_clause = any(t.get("term_key") == "recoupment_clause" for t in terms)
        has_recoup_trap = bool(self._RECOUP_TRAP_RE.search(text))

        low_rate_flag = bool(rate_values) and min(rate_values) < 12.0
        royalty_rate_anomaly = low_rate_flag or (
            bool(rate_values) and max(rate_values) - min(rate_values) > 20.0
        )

        risk = 0.25
        if not has_audit:
            risk += 0.2
        if not has_escalator:
            risk += 0.15
        if has_recoup_clause:
            risk += 0.15
        if has_recoup_trap:
            risk += 0.2
        if royalty_rate_anomaly:
            risk += 0.15
        if not has_mfn:
            risk += 0.05

        redlines: list[str] = []
        if not has_audit:
            redlines.append(
                "Add explicit annual audit rights with 30-day access to books and records."
            )
        if not has_escalator:
            redlines.append("Add an escalator clause tied to stream/consumption thresholds.")
        if has_recoup_clause:
            redlines.append(
                "Cap recoupment and prohibit non-transparent reserves without aging schedule."
            )
        if has_recoup_trap:
            redlines.append("Remove cross-collateralization/perpetual recoupment language.")
        if royalty_rate_anomaly:
            redlines.append(
                "Normalize royalty rates to market benchmarks and define territory exceptions."
            )
        if not has_mfn:
            redlines.append("Add MFN protection for key royalty and audit terms.")

        return {
            "future_underpayment_risk_score": round(max(0.0, min(1.0, risk)), 6),
            "recommended_redlines": redlines,
            "signals": {
                "escalator_detected": has_escalator,
                "audit_rights_classification": "present" if has_audit else "missing",
                "mfn_detected": has_mfn,
                "recoupment_traps_detected": has_recoup_trap,
                "royalty_rate_anomalies_detected": royalty_rate_anomaly,
            },
        }
