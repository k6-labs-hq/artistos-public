from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.services.founder_program import founder_status_payload

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/founder-status")
def get_founder_status(db: Session = Depends(get_db)):
    return founder_status_payload(db)
