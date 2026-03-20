from __future__ import annotations

import csv
import io
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from XR7.services.enterprise_historical_analysis import analyze_historical_portfolio

router = APIRouter(prefix="/enterprise/historical", tags=["enterprise"])


class EnterpriseHistoricalAnalysisRequest(BaseModel):
    organization_name: str
    entity_type: str = "Talent Agency"
    records: list[dict[str, Any]] = Field(default_factory=list)


@router.post("/analyze")
def analyze_enterprise_historical(payload: EnterpriseHistoricalAnalysisRequest):
    if not payload.records:
        raise HTTPException(status_code=400, detail="Portfolio record list is empty")
    return analyze_historical_portfolio(
        organization_name=payload.organization_name,
        entity_type=payload.entity_type,
        records=payload.records,
    )


@router.post("/analyze-file")
async def analyze_enterprise_historical_file(
    organization_name: str = Form(...),
    entity_type: str = Form("Talent Agency"),
    file: UploadFile = File(...),
):
    filename = (file.filename or "").lower()
    if not filename.endswith((".csv", ".tsv")):
        raise HTTPException(status_code=400, detail="Only CSV/TSV files are supported")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    text = raw.decode("utf-8", errors="ignore")
    delimiter = "\t" if filename.endswith(".tsv") else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    rows = [dict(r) for r in reader]
    if not rows:
        raise HTTPException(status_code=400, detail="No parseable rows found in uploaded file")

    return analyze_historical_portfolio(
        organization_name=organization_name,
        entity_type=entity_type,
        records=rows,
    )
