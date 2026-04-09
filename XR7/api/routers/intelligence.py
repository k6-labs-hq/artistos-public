import uuid
from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.intelligence.withholding_estimate import tax_optimizer
from XR7.ml.catalog_auditor import AutomatedRegistrationFixer, CatalogAuditor
from XR7.ml.catalog_valuation import CatalogValuationEngine
from XR7.ml.contract_document_ingestion import ContractDocumentIngestion
from XR7.ml.contract_term_extractor import ContractTermExtractor
from XR7.ml.expected_payout_simulator import ExpectedPayoutSimulator
from XR7.ml.recovery_utility_ranker import RecoveryUtilityRanker
from XR7.ml.royalty_optimizer import RoyaltyOptimizer
from XR7.ml.success_probability_calibrator import SuccessProbabilityCalibrator
from XR7.models.anomaly import Anomaly
from XR7.models.base import get_db
from XR7.models.claim import Claim
from XR7.models.ml_feedback import MLFeedbackEvent, MLFeedbackEventSchema, MLFeedbackType
from XR7.models.recovery_intelligence import (
    ContractTermSnapshot,
    RecoveryOutcomeFeedback,
    RecoveryOutcomeFeedbackSchema,
    RoyaltyLedgerEntry,
    RoyaltyLedgerEntryCreate,
    RoyaltyLedgerEntrySchema,
)
from XR7.models.review_queue import ReviewSourceType
from XR7.registration.auto_fix_agent import AutoFixRegistrationAgent
from XR7.services.branding import (
    branding_metadata,
    get_branding_for_artist,
    inject_branding_metadata,
)
from XR7.services.ml_feedback import ingest_feedback_event
from XR7.services.review_queue import enqueue_review_item
from XR7.tasks.pipeline import aggregate_feedback_calibration, run_catalog_audit
from xr7_common.logging import get_logger

router = APIRouter(tags=["intelligence"])
logger = get_logger(__name__)


def _safe_enqueue_calibration(artist_id: str) -> None:
    try:
        aggregate_feedback_calibration.delay(artist_id)
    except Exception:  # noqa: BLE001
        # Feedback persistence should not fail the request if queue infra is down.
        return


class LedgerIngestRequest(BaseModel):
    entries: list[RoyaltyLedgerEntryCreate]


class ContractExtractRequest(BaseModel):
    contract_id: str | None = None
    contract_text: str
    effective_start: date | None = None
    effective_end: date | None = None
    extracted_from: str | None = None


class SimulatePayoutRequest(BaseModel):
    usage_rows: list[dict]
    fallback_rate: float = 0.004
    default_withholding_rate: float = 0.0
    default_fx_rate: float = 1.0
    payout_currency: str = "USD"
    received_amount: float | None = None
    contract_terms: dict | None = None


class StructuredFeedbackRequest(BaseModel):
    # Backward-compatible fields used by RecoveryOutcomeFeedback
    anomaly_id: str | None = None
    claim_id: str | None = None
    outcome: str | None = None
    recovered_amount: float | None = None
    reason_code: str | None = None
    analyst_note: str | None = None

    # New structured ML feedback payload fields
    feedback_type: MLFeedbackType = MLFeedbackType.CLAIM_OUTCOME
    source_type: str | None = None
    source_id: str | None = None
    subtype: str | None = None
    category: str | None = None
    artist_profile_segment: str | None = None
    model_version: str | None = None
    model_prediction: float | None = None
    human_decision: str | None = None
    estimated_amount: float | None = None
    actual_amount: float | None = None
    payload: dict | None = None


class UtilityRankRequest(BaseModel):
    items: list[dict]
    analyst_hourly_cost: float = 75.0


class PreSignatureContractReviewRequest(BaseModel):
    contract_text: str


class TaxOptimizerRequest(BaseModel):
    gross_amount: float
    us_withholding_rate: float = 0.3
    global_withholding_rate: float = 0.1
    fx_rate: float = 1.0


class OptimizationSimulationRequest(BaseModel):
    changes: dict


@router.get("/artists/{artist_id}/intelligence/calibration")
def get_calibration_health(
    artist_id: str,
    db: Session = Depends(get_db),
):
    get_artist_or_404(artist_id, db)

    calibrator = SuccessProbabilityCalibrator()
    summary = calibrator.calibration_summary(artist_id, db)
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **summary,
    }


@router.post("/artists/{artist_id}/intelligence/ledger/ingest")
def ingest_royalty_ledger(
    artist_id: str,
    payload: LedgerIngestRequest,
    db: Session = Depends(get_db),
):
    get_artist_or_404(artist_id, db)

    created: list[RoyaltyLedgerEntry] = []
    for entry in payload.entries:
        model = RoyaltyLedgerEntry(
            artist_id=artist_id,
            source=entry.source,
            record_type=entry.record_type,
            source_file=entry.source_file,
            source_row=entry.source_row,
            contract_version=entry.contract_version,
            work_id=entry.work_id,
            event_type=entry.event_type,
            period_start=entry.period_start,
            period_end=entry.period_end,
            quantity=entry.quantity,
            rate=entry.rate,
            expected_amount=entry.expected_amount,
            received_amount=entry.received_amount,
            currency=entry.currency,
            fx_rate_used=entry.fx_rate_used,
            territory=entry.territory,
        )
        db.add(model)
        created.append(model)

    db.commit()
    for item in created:
        db.refresh(item)

    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "created_count": len(created),
        "entries": [RoyaltyLedgerEntrySchema.model_validate(e).model_dump() for e in created],
    }


@router.post("/artists/{artist_id}/intelligence/contracts/extract")
def extract_contract_terms(
    artist_id: str,
    payload: ContractExtractRequest,
    db: Session = Depends(get_db),
):
    get_artist_or_404(artist_id, db)

    extractor = ContractTermExtractor()
    terms, highlights = extractor.extract_with_highlights(
        contract_text=payload.contract_text,
        effective_start=payload.effective_start,
        effective_end=payload.effective_end,
    )

    created = []
    for term in terms:
        model = ContractTermSnapshot(
            id=str(uuid.uuid4()),
            artist_id=artist_id,
            contract_id=payload.contract_id,
            term_key=term["term_key"],
            term_value=str(term["term_value"]),
            confidence_score=float(term["confidence_score"]),
            effective_start=term.get("effective_start"),
            effective_end=term.get("effective_end"),
            extracted_from=payload.extracted_from,
        )
        db.add(model)
        created.append(model)

    db.commit()
    for item in created:
        db.refresh(item)

    for item in created:
        if float(item.confidence_score or 1.0) < 0.6:
            enqueue_review_item(
                db,
                artist_id=artist_id,
                source_type=ReviewSourceType.ML_CONFIDENCE,
                source_id=item.id,
                reason="Low-confidence contract term extraction requires analyst review",
                priority_score=1.0 - float(item.confidence_score or 0.0),
                payload={
                    "contract_id": item.contract_id,
                    "term_key": item.term_key,
                    "term_value": item.term_value,
                    "confidence_score": item.confidence_score,
                },
            )

    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "term_count": len(created),
        "highlights": highlights,
        "terms": [
            {
                "id": t.id,
                "term_key": t.term_key,
                "term_value": t.term_value,
                "confidence_score": t.confidence_score,
                "effective_start": t.effective_start,
                "effective_end": t.effective_end,
            }
            for t in created
        ],
    }


@router.post("/artists/{artist_id}/intelligence/contracts/extract-upload")
async def extract_contract_terms_upload(
    artist_id: str,
    file: UploadFile = File(...),
    contract_id: str | None = Form(None),
    effective_start: str | None = Form(None),
    effective_end: str | None = Form(None),
    extracted_from: str | None = Form(None),
    db: Session = Depends(get_db),
):
    get_artist_or_404(artist_id, db)

    if not file.filename:
        raise HTTPException(status_code=400, detail="No contract file provided")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded contract file is empty")

    ingestion = ContractDocumentIngestion()
    extracted = ingestion.extract_text(file.filename, content)
    contract_text = extracted.get("text", "")
    if not contract_text:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Unable to extract contract text from upload.",
                "warnings": extracted.get("warnings", []),
            },
        )

    try:
        start_dt = date.fromisoformat(effective_start) if effective_start else None
        end_dt = date.fromisoformat(effective_end) if effective_end else None
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format in effective_start/effective_end: {exc}",
        ) from exc

    extractor = ContractTermExtractor()
    terms, highlights = extractor.extract_with_highlights(
        contract_text=contract_text,
        effective_start=start_dt,
        effective_end=end_dt,
    )

    created = []
    for term in terms:
        model = ContractTermSnapshot(
            id=str(uuid.uuid4()),
            artist_id=artist_id,
            contract_id=contract_id,
            term_key=term["term_key"],
            term_value=str(term["term_value"]),
            confidence_score=float(term["confidence_score"]),
            effective_start=term.get("effective_start"),
            effective_end=term.get("effective_end"),
            extracted_from=extracted_from or file.filename,
        )
        db.add(model)
        created.append(model)

    db.commit()
    for item in created:
        db.refresh(item)

    for item in created:
        if float(item.confidence_score or 1.0) < 0.6:
            enqueue_review_item(
                db,
                artist_id=artist_id,
                source_type=ReviewSourceType.ML_CONFIDENCE,
                source_id=item.id,
                reason="Low-confidence uploaded contract extraction requires analyst review",
                priority_score=1.0 - float(item.confidence_score or 0.0),
                payload={
                    "contract_id": item.contract_id,
                    "term_key": item.term_key,
                    "term_value": item.term_value,
                    "confidence_score": item.confidence_score,
                },
            )

    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "term_count": len(created),
        "extraction_method": extracted.get("method"),
        "warnings": extracted.get("warnings", []),
        "highlights": highlights,
        "terms": [
            {
                "id": t.id,
                "term_key": t.term_key,
                "term_value": t.term_value,
                "confidence_score": t.confidence_score,
            }
            for t in created
        ],
    }


@router.post("/artists/{artist_id}/intelligence/simulate-expected-payout")
def simulate_expected_payout(
    artist_id: str,
    payload: SimulatePayoutRequest,
    db: Session = Depends(get_db),
):
    get_artist_or_404(artist_id, db)

    simulator = ExpectedPayoutSimulator()
    result = simulator.simulate(
        usage_rows=payload.usage_rows,
        fallback_rate=payload.fallback_rate,
        default_withholding_rate=payload.default_withholding_rate,
        default_fx_rate=payload.default_fx_rate,
        payout_currency=payload.payout_currency,
        received_amount=payload.received_amount,
        contract_terms=payload.contract_terms,
    )
    variance_pct = abs(float(result.get("variance_pct") or 0.0))
    if variance_pct >= 0.35:
        enqueue_review_item(
            db,
            artist_id=artist_id,
            source_type=ReviewSourceType.ML_CONFIDENCE,
            source_id=None,
            reason="Large forecast deviation detected between expected and received payout",
            priority_score=float(abs(result.get("variance") or 0.0)),
            payload={
                "variance": result.get("variance"),
                "variance_pct": result.get("variance_pct"),
                "contract_terms_used": result.get("contract_terms_used"),
            },
        )
    return {"artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)), **result}


@router.post("/artists/{artist_id}/intelligence/feedback", response_model=RecoveryOutcomeFeedbackSchema)
def create_outcome_feedback(
    artist_id: str,
    payload: StructuredFeedbackRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    get_artist_or_404(artist_id, db)

    outcome_value = payload.outcome or "DISMISSED"
    feedback = RecoveryOutcomeFeedback(
        artist_id=artist_id,
        anomaly_id=payload.anomaly_id,
        claim_id=payload.claim_id,
        outcome=outcome_value,
        recovered_amount=payload.recovered_amount,
        reason_code=payload.reason_code,
        analyst_note=payload.analyst_note,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    inferred_subtype = payload.subtype
    inferred_category = payload.category
    if payload.anomaly_id and (inferred_subtype is None or inferred_category is None):
        anomaly = db.query(Anomaly).filter(Anomaly.id == payload.anomaly_id).first()
        if anomaly:
            inferred_subtype = inferred_subtype or anomaly.subtype
            inferred_category = inferred_category or str(anomaly.category)
    if payload.claim_id and inferred_subtype is None:
        claim = db.query(Claim).filter(Claim.id == payload.claim_id).first()
        if claim:
            inferred_subtype = claim.claim_type

    ingest_feedback_event(
        db,
        artist_id=artist_id,
        feedback_type=payload.feedback_type,
        source_type=payload.source_type,
        source_id=payload.source_id,
        anomaly_id=payload.anomaly_id,
        claim_id=payload.claim_id,
        subtype=inferred_subtype,
        category=inferred_category,
        artist_profile_segment=payload.artist_profile_segment,
        model_version=payload.model_version,
        model_prediction=payload.model_prediction,
        human_decision=payload.human_decision,
        outcome=payload.outcome,
        estimated_amount=payload.estimated_amount,
        actual_amount=payload.actual_amount,
        payload=payload.payload,
    )

    # Keep calibration_health warm for downstream reads.
    background_tasks.add_task(_safe_enqueue_calibration, artist_id)
    return feedback


@router.get("/artists/{artist_id}/intelligence/feedback/events", response_model=list[MLFeedbackEventSchema])
def list_feedback_events(
    artist_id: str,
    db: Session = Depends(get_db),
):
    get_artist_or_404(artist_id, db)
    return (
        db.query(MLFeedbackEvent)
        .filter(MLFeedbackEvent.artist_id == artist_id)
        .order_by(MLFeedbackEvent.created_at.desc())
        .limit(500)
        .all()
    )


@router.post("/artists/{artist_id}/intelligence/rank-utility")
def rank_by_expected_utility(
    artist_id: str,
    payload: UtilityRankRequest,
    db: Session = Depends(get_db),
):
    get_artist_or_404(artist_id, db)

    ranker = RecoveryUtilityRanker()
    calibrator = SuccessProbabilityCalibrator()
    calibrated_items = calibrator.calibrate_items(artist_id, payload.items, db)

    items_for_ranking = []
    for item in calibrated_items:
        copy = dict(item)
        copy["success_probability"] = item.get("calibrated_success_probability", 0.5)
        items_for_ranking.append(copy)

    ranked = ranker.rank(items_for_ranking, analyst_hourly_cost=payload.analyst_hourly_cost)
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "ranked": ranked,
        "count": len(ranked),
        "calibration": ranked[0].get("calibration") if ranked else None,
    }


@router.post("/artists/{artist_id}/intelligence/contracts/pre-signature-review")
def pre_signature_contract_review(
    artist_id: str,
    payload: PreSignatureContractReviewRequest,
    db: Session = Depends(get_db),
):
    get_artist_or_404(artist_id, db)

    extractor = ContractTermExtractor()
    review = extractor.pre_signature_review(payload.contract_text)
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **review,
    }


@router.post("/artists/{artist_id}/ml/catalog-audit")
async def run_catalog_audit_on_demand(
    artist_id: str,
    db: Session = Depends(get_db),
):
    get_artist_or_404(artist_id, db)

    audit = await CatalogAuditor(db).run(artist_id)
    db.add(
        MLFeedbackEvent(
            artist_id=artist_id,
            feedback_type=MLFeedbackType.RECOVERY_RESULT.value,
            source_type="catalog_audit",
            source_id=None,
            outcome="CATALOG_AUDIT_COMPLETED",
            payload={
                "catalog_health": audit.get("catalog_health"),
                "signals": audit.get("signals"),
                "issue_count": len(audit.get("issues") or []),
            },
        )
    )
    db.commit()

    try:
        run_catalog_audit.delay(artist_id)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to enqueue run_catalog_audit", extra={"artist_id": artist_id})

    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **audit,
    }


@router.post("/artists/{artist_id}/intelligence/tax-optimizer")
def run_tax_optimizer(artist_id: str, payload: TaxOptimizerRequest, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    result = tax_optimizer(
        artist_id,
        gross_amount=payload.gross_amount,
        us_withholding_rate=payload.us_withholding_rate,
        global_withholding_rate=payload.global_withholding_rate,
        fx_rate=payload.fx_rate,
    )
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **result,
    }


@router.post("/artists/{artist_id}/registration/auto-fix")
def registration_auto_fix(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    agent = AutoFixRegistrationAgent(db)
    issues = agent.scan_registration_gaps(artist_id)
    payload = agent.auto_register_or_prepare_submission(artist_id, issues)
    return inject_branding_metadata(db, {"artist_id": artist_id, "issues": issues, **payload})


@router.get("/artists/{artist_id}/registration/status")
def registration_status(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    issues = AutomatedRegistrationFixer(db).detect_missing_metadata(artist_id)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "open_registration_issues": len(issues),
            "issues": issues,
        },
    )


@router.post("/artists/{artist_id}/ml/catalog-valuation")
async def catalog_valuation(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    engine = CatalogValuationEngine(db)
    value = engine.calculate_catalog_value(artist_id)
    report = await engine.export_valuation_report_with_anchor(artist_id)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "valuation": value,
            "anchored_report": report,
        },
    )


@router.post("/artists/{artist_id}/ml/financing-matches")
def financing_matches(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    engine = CatalogValuationEngine(db)
    value = engine.calculate_catalog_value(artist_id)
    matches = engine.generate_financing_matches(value)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "financing_opportunities": matches,
            "estimated_advance": sum(float(m.get("estimated_advance") or 0.0) for m in matches),
        },
    )


@router.post("/artists/{artist_id}/ml/simulate-optimization")
def simulate_optimization(artist_id: str, payload: OptimizationSimulationRequest, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    opt = RoyaltyOptimizer()
    simulation = opt.simulate_scenario(artist_id, payload.changes)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "simulation": simulation,
            "visualization": opt.visualize_delta(simulation),
        },
    )
