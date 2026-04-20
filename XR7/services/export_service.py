"""Export service for generating comprehensive artist reports (CSV/PDF).

Feature #5: Exportable reports for artists, managers, and attorneys.

This service generates audit-ready summaries including:
- Total leakage detected and estimated recovery value  
- Recovered vs potential trajectory
- Claim pipeline with status breakdowns
- Catalog health and coverage breakdown

Supports both CSV (machine-readable) and PDF (board/legal sharing) formats.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.event import Event
from XR7.models.payment import Payment
from XR7.models.statement import Statement
from XR7.services.pdf_builder import build_simple_pdf, safe_pdf_text

if TYPE_CHECKING:
    pass


def generate_artist_summary_csv(db: Session, artist_id: str) -> bytes:
    """
    Generate CSV export with comprehensive artist recovery summary.
    
    Sections:
    - Leakage summary (total detected, by category)
    - Recovery summary (total recovered, potential, in flight)
    - Claim pipeline (by status)
    - Catalog health (statements uploaded, coverage periods)
    
    Args:
        db: Database session
        artist_id: Artist identifier
    
    Returns:
        CSV bytes with UTF-8 BOM for Excel compatibility
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise ValueError(f"Artist {artist_id} not found")
    
    # Aggregate metrics
    anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    statements = db.query(Statement).filter(Statement.artist_id == artist_id).all()
    payments = db.query(Payment).filter(Payment.artist_id == artist_id).all()
    
    total_leakage = sum(a.amount or 0 for a in anomalies)
    total_recovered = sum(c.amount_recovered or 0 for c in claims)
    total_potential = sum(c.amount_claimed or 0 for c in claims)
    in_flight = sum(
        c.amount_claimed or 0
        for c in claims
        if c.status not in {ClaimStatus.PAID, ClaimStatus.CLOSED}
    )
    
    # Claim status breakdown
    claim_status_counts = {}
    for claim in claims:
        status = claim.status.value if hasattr(claim.status, "value") else str(claim.status)
        claim_status_counts[status] = claim_status_counts.get(status, 0) + 1
    
    # Catalog coverage
    statement_count = len(statements)
    total_events = db.query(func.count(Event.id)).filter(Event.artist_id == artist_id).scalar() or 0
    total_payments_count = len(payments)
    
    # Write CSV
    buf = io.StringIO()
    writer = csv.writer(buf)
    
    # Metadata section
    writer.writerow(["XR7 Artist Recovery Report"])
    writer.writerow(["Generated", datetime.now(timezone.utc).isoformat()])
    writer.writerow(["Artist ID", artist_id])
    writer.writerow(["Artist Name", getattr(artist, "stage_name", None) or artist_id])
    writer.writerow([])
    
    # Leakage summary
    writer.writerow(["LEAKAGE SUMMARY"])
    writer.writerow(["Total Detected", f"${total_leakage:,.2f}"])
    writer.writerow(["Anomalies Identified", len(anomalies)])
    writer.writerow([])
    
    # Recovery summary
    writer.writerow(["RECOVERY SUMMARY"])
    writer.writerow(["Total Recovered", f"${total_recovered:,.2f}"])
    writer.writerow(["Total Potential", f"${total_potential:,.2f}"])
    writer.writerow(["In Flight", f"${in_flight:,.2f}"])
    writer.writerow(["Recovery Rate", f"{(total_recovered / total_potential * 100):.1f}%" if total_potential > 0 else "N/A"])
    writer.writerow([])
    
    # Claim pipeline
    writer.writerow(["CLAIM PIPELINE"])
    writer.writerow(["Status", "Count"])
    for status, count in sorted(claim_status_counts.items()):
        writer.writerow([status, count])
    writer.writerow([])
    
    # Catalog health
    writer.writerow(["CATALOG HEALTH"])
    writer.writerow(["Statements Uploaded", statement_count])
    writer.writerow(["Events Ingested", total_events])
    writer.writerow(["Payments Tracked", total_payments_count])
    writer.writerow([])
    
    # Schema version for future compatibility
    writer.writerow(["METADATA"])
    writer.writerow(["Report Schema Version", "1.0"])
    writer.writerow(["Export Format", "CSV"])
    
    # Return with UTF-8 BOM for Excel compatibility
    return ("\ufeff" + buf.getvalue()).encode("utf-8")


def generate_artist_summary_pdf(db: Session, artist_id: str) -> bytes:
    """
    Generate PDF export with comprehensive artist recovery summary.
    
    Formatted for board/legal sharing with clear section headers and metrics.
    
    Args:
        db: Database session
        artist_id: Artist identifier
    
    Returns:
        PDF bytes
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise ValueError(f"Artist {artist_id} not found")
    
    # Aggregate metrics (same as CSV)
    anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    statements = db.query(Statement).filter(Statement.artist_id == artist_id).all()
    payments = db.query(Payment).filter(Payment.artist_id == artist_id).all()
    
    total_leakage = sum(a.amount or 0 for a in anomalies)
    total_recovered = sum(c.amount_recovered or 0 for c in claims)
    total_potential = sum(c.amount_claimed or 0 for c in claims)
    in_flight = sum(
        c.amount_claimed or 0
        for c in claims
        if c.status not in {ClaimStatus.PAID, ClaimStatus.CLOSED}
    )
    
    # Claim status breakdown
    claim_status_counts = {}
    for claim in claims:
        status = claim.status.value if hasattr(claim.status, "value") else str(claim.status)
        claim_status_counts[status] = claim_status_counts.get(status, 0) + 1
    
    # Catalog coverage
    statement_count = len(statements)
    total_events = db.query(func.count(Event.id)).filter(Event.artist_id == artist_id).scalar() or 0
    total_payments_count = len(payments)
    
    recovery_rate = (total_recovered / total_potential * 100) if total_potential > 0 else 0
    
    # Build PDF content
    lines = [
        "XR7 ARTIST RECOVERY REPORT",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Artist: {getattr(artist, 'stage_name', None) or artist_id}",
        "",
        "LEAKAGE SUMMARY",
        f"  Total Detected: ${total_leakage:,.2f}",
        f"  Anomalies Identified: {len(anomalies)}",
        "",
        "RECOVERY SUMMARY",
        f"  Total Recovered: ${total_recovered:,.2f}",
        f"  Total Potential: ${total_potential:,.2f}",
        f"  In Flight: ${in_flight:,.2f}",
        f"  Recovery Rate: {recovery_rate:.1f}%",
        "",
        "CLAIM PIPELINE",
    ]
    
    for status, count in sorted(claim_status_counts.items()):
        lines.append(f"  {status}: {count}")
    
    lines.extend([
        "",
        "CATALOG HEALTH",
        f"  Statements Uploaded: {statement_count}",
        f"  Events Ingested: {total_events}",
        f"  Payments Tracked: {total_payments_count}",
        "",
        "---",
        "This report is confidential and intended for artist/legal review only.",
        f"Report schema version: 1.0",
    ])
    
    return build_simple_pdf(lines)
