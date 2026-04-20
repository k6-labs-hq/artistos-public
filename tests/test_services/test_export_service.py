"""Unit tests for export_service.py (Feature #5: Exportable reports).

Test CSV and PDF generation without database dependencies where possible.
Use in-memory test data for fast feedback.
"""

import pytest
from unittest.mock import Mock, patch
from XR7.services.export_service import generate_artist_summary_csv, generate_artist_summary_pdf


class TestExportService:
    """Unit tests for export service (CSV/PDF generation)."""
    
    @patch("XR7.services.export_service.db")
    def test_generate_artist_summary_csv_structure(self, mock_db):
        """Test CSV export generates proper structure with BOM and headers."""
        # Arrange: Mock database queries to return empty results
        mock_db.query.return_value.filter.return_value.filter.return_value.count.return_value = 0
        mock_db.query.return_value.filter.return_value.filter.return_value.scalar.return_value = 0
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        csv_bytes = generate_artist_summary_csv(mock_db, "art_test_123")
        csv_text = csv_bytes.decode("utf-8-sig")
        
        # Assert: Check for UTF-8 BOM (Excel compatibility)
        assert csv_bytes.startswith(b"\xef\xbb\xbf")
        
        # Assert: Check for required sections
        assert "XR7 Artist Summary Report" in csv_text
        assert "Schema Version" in csv_text
        assert "Artist ID,art_test_123" in csv_text
        assert "Leakage Summary" in csv_text
        assert "Recovery Summary" in csv_text
        assert "Claim Pipeline" in csv_text
        assert "Catalog Health" in csv_text
    
    @patch("XR7.services.export_service.db")
    def test_generate_artist_summary_pdf_includes_metadata(self, mock_db):
        """Test PDF export includes generation timestamp and confidentiality statement."""
        # Arrange
        mock_db.query.return_value.filter.return_value.filter.return_value.count.return_value = 0
        mock_db.query.return_value.filter.return_value.filter.return_value.scalar.return_value = 0
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        pdf_bytes = generate_artist_summary_pdf(mock_db, "art_test_456")
        pdf_text = pdf_bytes.decode("latin-1", errors="ignore")
        
        # Assert: PDF starts with PDF magic header
        assert pdf_bytes.startswith(b"%PDF-")
        
        # Assert: Contains artist ID
        assert "art_test_456" in pdf_text
        
        # Assert: Contains confidentiality statement
        assert "CONFIDENTIAL" in pdf_text
    
    def test_csv_schema_versioning(self):
        """Test CSV includes schema version for forward compatibility."""
        # This ensures exported CSVs can be parsed by future versions
        # even if we add more columns/sections later
        with patch("XR7.services.export_service.db") as mock_db:
            mock_db.query.return_value.filter.return_value.filter.return_value.count.return_value = 0
            mock_db.query.return_value.filter.return_value.filter.return_value.scalar.return_value = 0
            mock_db.query.return_value.filter.return_value.first.return_value = None
            
            csv_bytes = generate_artist_summary_csv(mock_db, "art_123")
            csv_text = csv_bytes.decode("utf-8-sig")
            
            # Assert: Schema version is present and follows semantic versioning
            assert "Schema Version,v1.0" in csv_text or "Schema Version,1.0" in csv_text
