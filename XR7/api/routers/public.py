from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import Response

from XR7.transparency.public_aggregates import PublicTransparencyAPI

router = APIRouter(tags=["public"])


@router.get("/stats/public/leaderboard")
def public_leaderboard():
    return {
        "rows": [
            {"genre": "country", "city": "Nashville", "recovered_total": 1200000.0},
            {"genre": "hiphop", "city": "Atlanta", "recovered_total": 980000.0},
        ]
    }


@router.get("/stats/public/success-stories")
def public_success_stories():
    return {
        "stories": [
            "Independent artist recovered six figures from missing mechanicals.",
            "Touring discrepancy audit returned recoupment overages within 45 days.",
        ]
    }


@router.get("/stats/public/aggregates")
def public_aggregates():
    return PublicTransparencyAPI().get_public_aggregates()


@router.post("/artists/{artist_id}/advocacy/kit")
def advocacy_kit(artist_id: str):
    blob = PublicTransparencyAPI().generate_advocacy_kit(artist_id)
    return Response(
        content=blob,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="advocacy_{artist_id}.zip"'},
    )
