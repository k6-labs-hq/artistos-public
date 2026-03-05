from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.legal.terms import TERMS_VERSION
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.payment import Payment, PaymentType
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


def _create_artist() -> str:
    db = _TestSession()
    artist = Artist(
        id=str(uuid.uuid4()),
        name="Expansion Test Artist",
        created_at=datetime.now(timezone.utc),
    )
    db.add(artist)
    db.commit()
    artist_id = artist.id
    db.close()

    resp = client.post(
        f"/artists/{artist_id}/terms/accept",
        json={"terms_version": TERMS_VERSION, "agreed": True},
    )
    assert resp.status_code == 201
    return artist_id


def test_summary_report_csv_and_pdf_exports():
    artist_id = _create_artist()
    db = _TestSession()

    anomaly = Anomaly(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        status=AnomalyStatus.OPEN,
        confidence_score=0.9,
        estimated_recoverable=1500.0,
        created_at=datetime.now(timezone.utc),
    )
    payment = Payment(
        id=str(uuid.uuid4()),
        payment_type=PaymentType.ROYALTY,
        artist_id=artist_id,
        amount=300.0,
        currency="USD",
        source="Test Source",
        received_at=datetime.now(timezone.utc),
    )
    claim = Claim(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        anomaly_id=anomaly.id,
        claim_type="ROYALTY",
        status=ClaimStatus.IDENTIFIED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(anomaly)
    db.add(payment)
    db.add(claim)
    db.commit()
    db.close()

    csv_resp = client.get(f"/artists/{artist_id}/reports/summary", params={"format": "csv"})
    assert csv_resp.status_code == 200
    assert csv_resp.headers["content-type"].startswith("text/csv")
    assert "metric,value" in csv_resp.text

    pdf_resp = client.get(f"/artists/{artist_id}/reports/summary", params={"format": "pdf"})
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"].startswith("application/pdf")
    assert pdf_resp.content.startswith(b"%PDF-")


def test_batch_upload_endpoint_processes_multiple_csvs():
    artist_id = _create_artist()

    csv_one = (
        "Month,Store,Country,Title,ISRC,Quantity,Earnings\n"
        "2024-01,Spotify,US,Song A,USAAA1234567,1000,4.00\n"
    ).encode("utf-8")
    csv_two = (
        "Month,Store,Country,Title,ISRC,Quantity,Earnings\n"
        "2024-02,Apple Music,US,Song B,USBBB1234567,2000,7.50\n"
    ).encode("utf-8")

    files = [
        ("files", ("jan.csv", io.BytesIO(csv_one), "text/csv")),
        ("files", ("feb.csv", io.BytesIO(csv_two), "text/csv")),
    ]

    resp = client.post(f"/artists/{artist_id}/statements/upload-batch", files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert body["requested"] == 2
    assert body["processed_count"] == 2
    assert body["failed_count"] == 0


def test_dashboard_charts_and_team_access_endpoints():
    artist_id = _create_artist()

    charts_resp = client.get(f"/artists/{artist_id}/dashboard/charts")
    assert charts_resp.status_code == 200
    chart_body = charts_resp.json()
    assert chart_body["artist_id"] == artist_id
    assert "leakage_by_month" in chart_body
    assert "recovered_by_month" in chart_body
    assert "forecast_confidence_bands" in chart_body

    create_member = client.post(
        f"/artists/{artist_id}/team/members",
        json={"user_email": "manager@example.com", "role": "manager"},
    )
    assert create_member.status_code == 201
    member_id = create_member.json()["id"]

    list_members = client.get(f"/artists/{artist_id}/team/members")
    assert list_members.status_code == 200
    assert any(m["id"] == member_id for m in list_members.json())

    delete_member = client.delete(f"/artists/{artist_id}/team/members/{member_id}")
    assert delete_member.status_code == 200
    assert delete_member.json()["deleted"] is True
