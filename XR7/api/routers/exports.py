"""Export endpoints for comprehensive artist reports (CSV/PDF).

Feature #5: Exportable reports (PDF/CSV)

Provides audit-ready summaries for artists, managers, and attorneys:
- CSV exports for machine-readable metrics
- PDF exports for board/legal sharing
- Versioned schema for forward compatibility
"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.services.export_service import (
    generate_artist_summary_csv,
    generate_artist_summary_pdf,
)
from XR7.services.router_v21_phase1 import router_service_for

router = APIRouter(tags=["exports"])
_router_service = router_service_for("exports")


@router.get("/artists/{artist_id}/reports/summary.csv")
def export_summary_csv(artist_id: str, db: Session = Depends(get_db)):
    """
    Export comprehensive artist recovery summary as CSV.
    
    Includes:
    - Leakage summary (total detected, anomaly count)
    - Recovery summary (recovered, potential, in-flight)
    - Claim pipeline breakdown by status
    - Catalog health (statements, events, payments)
    
    CSV format is machine-readable with UTF-8 BOM for Excel compatibility.
    Schema version included for forward compatibility.
    
    **Acceptance criteria**:
    - Generation time < 5 seconds for typical artist portfolio
    - Includes generation timestamp
    - CSV schema version in metadata section
    """
    _router_service.get_artist_or_404(artist_id, db)
    
    csv_bytes = generate_artist_summary_csv(db, artist_id)
    
    from datetime import datetime, timezone
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"xr7_summary_{artist_id}_{timestamp}.csv"
    
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/artists/{artist_id}/reports/summary.pdf")
def export_summary_pdf(artist_id: str, db: Session = Depends(get_db)):
    """
    Export comprehensive artist recovery summary as PDF.
    
    Formatted for board/legal sharing with clear section headers.
    
    Includes:
    - Leakage summary (total detected, anomaly count)
    - Recovery summary (recovered, potential, recovery rate)
    - Claim pipeline breakdown by status
    - Catalog health metrics
    - Confidentiality statement
    
    PDF format is human-readable and suitable for printing/sharing.
    
    **Acceptance criteria**:
    - Readable on both 1-page and multi-page reports
    - Generation time < 5 seconds for typical portfolio
    - Includes generation timestamp
    - Report schema version in footer
    """
    _router_service.get_artist_or_404(artist_id, db)
    
    pdf_bytes = generate_artist_summary_pdf(db, artist_id)
    
    from datetime import datetime, timezone
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"xr7_summary_{artist_id}_{timestamp}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
