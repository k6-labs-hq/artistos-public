from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.artist import Artist
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


def _create_artist() -> str:
    db = _TestSession()
    artist = Artist(id=str(uuid.uuid4()), name="ML Feedback Artist", created_at=datetime.now(timezone.utc))
    db.add(artist)
    db.commit()
    artist_id = artist.id
    db.close()
    return artist_id


def test_feedback_events_update_calibration_with_credible_intervals():
    artist_id = _create_artist()

    for outcome in ["RECOVERED", "SETTLED", "DISMISSED", "RECOVERED"]:
        resp = client.post(
            f"/artists/{artist_id}/intelligence/feedback",
            json={
                "feedback_type": "CLAIM_OUTCOME",
                "outcome": outcome,
                "category": "ROYALTY",
                "subtype": "MISSING_PAYMENT",
                "model_prediction": 0.72,
                "model_version": "ml-hybrid-iforest-v2",
            },
        )
        assert resp.status_code == 200

    calibration = client.get(f"/artists/{artist_id}/intelligence/calibration")
    assert calibration.status_code == 200
    data = calibration.json()

    assert "overall" in data
    assert "credible_interval" in data["overall"]
    assert len(data["overall"]["credible_interval"]) == 2
    assert "by_category" in data
    assert "ROYALTY" in data["by_category"]
    assert data["method"].startswith("beta_binomial")


def test_rank_utility_uses_enhanced_calibration_metadata():
    artist_id = _create_artist()

    for _ in range(3):
        client.post(
            f"/artists/{artist_id}/intelligence/feedback",
            json={
                "feedback_type": "ANOMALY_OUTCOME",
                "outcome": "RECOVERED",
                "category": "PLATFORM",
                "subtype": "RATE_DRIFT_HIGH",
            },
        )

    ranked = client.post(
        f"/artists/{artist_id}/intelligence/rank-utility",
        json={
            "items": [
                {
                    "id": "item-1",
                    "category": "PLATFORM",
                    "subtype": "RATE_DRIFT_HIGH",
                    "estimated_recoverable": 2500,
                    "success_probability": 0.5,
                    "effort_hours": 2,
                }
            ]
        },
    )
    assert ranked.status_code == 200
    row = ranked.json()["ranked"][0]
    assert "calibration" in row
    assert "credible_interval" in row["calibration"]
    assert row["calibration"]["scope"] in {"subtype:RATE_DRIFT_HIGH", "category:PLATFORM", "global"}
