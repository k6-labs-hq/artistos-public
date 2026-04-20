"""Unit tests for clause_extraction_service.py (Feature #6: Contract OCR + clause highlighting).

Test regex-based clause extraction without file I/O dependencies.
"""

import pytest
from XR7.services.clause_extraction_service import (
    extract_clauses,
    flag_low_confidence_review,
)


class TestClauseExtractionService:
    """Unit tests for contract clause extraction."""
    
    def test_extract_rate_clause_percentage(self):
        """Test extraction of royalty rate clauses with percentages."""
        # Arrange
        contract_text = (
            "Artist shall receive 15% of net streaming revenues from all "
            "digital service providers, calculated quarterly."
        )
        
        # Act
        clauses = extract_clauses(contract_text)
        
        # Assert
        rate_clauses = [c for c in clauses if c["clause_type"] == "rate"]
        assert len(rate_clauses) > 0
        assert rate_clauses[0]["confidence"] >= 0.80
        assert "15%" in rate_clauses[0]["metadata"]["matched_value"]
    
    def test_extract_recoupment_clause(self):
        """Test extraction of advance recoupment clauses."""
        # Arrange
        contract_text = (
            "The advance shall be recouped from artist royalties before "
            "any further payments are made. The unrecouped balance as of "
            "December 31, 2025 was $50,000."
        )
        
        # Act
        clauses = extract_clauses(contract_text)
        
        # Assert
        recoupment_clauses = [c for c in clauses if c["clause_type"] == "recoupment"]
        assert len(recoupment_clauses) >= 2  # "shall be recouped" and "unrecouped balance"
        assert any("recoup" in c["metadata"]["matched_value"].lower() for c in recoupment_clauses)
    
    def test_extract_audit_rights_clause(self):
        """Test extraction of audit rights clauses."""
        # Arrange
        contract_text = (
            "Artist or Artist's representative may inspect books and records "
            "once per calendar year upon 30 days written notice."
        )
        
        # Act
        clauses = extract_clauses(contract_text)
        
        # Assert
        audit_clauses = [c for c in clauses if c["clause_type"] == "audit_right"]
        assert len(audit_clauses) >= 2  # "inspect books and records" and "once per calendar year"
        assert any(c["confidence"] >= 0.75 for c in audit_clauses)
    
    def test_deduplication_of_overlapping_matches(self):
        """Test that overlapping clause matches are deduplicated (keep highest confidence)."""
        # Arrange: Text that could match multiple patterns
        contract_text = (
            "royalty rate of 20% of net receipts from all sources"
        )
        
        # Act
        clauses = extract_clauses(contract_text)
        
        # Assert: Should not have duplicate overlapping matches
        rate_clauses = [c for c in clauses if c["clause_type"] == "rate"]
        if len(rate_clauses) > 1:
            # Check that positions don't overlap
            for i, clause1 in enumerate(rate_clauses):
                for clause2 in rate_clauses[i+1:]:
                    # No overlap: clause1 ends before clause2 starts OR clause2 ends before clause1 starts
                    assert (clause1["end_pos"] <= clause2["start_pos"] or 
                            clause2["end_pos"] <= clause1["start_pos"])
    
    def test_flag_low_confidence_review(self):
        """Test low-confidence flagging for manual review."""
        # Arrange: Mock clauses with varying confidence
        clauses = [
            {"clause_type": "rate", "confidence": 0.95, "start_pos": 0, "end_pos": 10, 
             "text": "high confidence", "metadata": {"matched_value": "15%"}},
            {"clause_type": "audit_right", "confidence": 0.70, "start_pos": 20, "end_pos": 30, 
             "text": "low confidence", "metadata": {"matched_value": "audit"}},
            {"clause_type": "recoupment", "confidence": 0.60, "start_pos": 40, "end_pos": 50, 
             "text": "very low confidence", "metadata": {"matched_value": "recoup"}},
        ]
        
        # Act
        warnings = flag_low_confidence_review(clauses, threshold=0.80)
        
        # Assert
        assert len(warnings) == 2  # Two clauses below 0.80 threshold
        assert "0.70" in warnings[0]
        assert "0.60" in warnings[1]
        assert "audit_right" in warnings[0]
        assert "recoupment" in warnings[1]
    
    def test_extract_clauses_returns_sorted_by_position(self):
        """Test that extracted clauses are sorted by document position."""
        # Arrange: Contract with clauses at different positions
        contract_text = (
            "Section 1: Artist shall receive 15% royalty rate. "
            "Section 2: The advance shall be recouped from royalties. "
            "Section 3: Artist may inspect books and records once per year."
        )
        
        # Act
        clauses = extract_clauses(contract_text)
        
        # Assert: Clauses should be in document order
        positions = [c["start_pos"] for c in clauses]
        assert positions == sorted(positions)
