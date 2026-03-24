"""
XR7 Engine 2 — Celery tasks for new modules.
Registered under the xr7.modules.* task namespace.
"""
from __future__ import annotations

from XR7.celery_app import celery_app
from XR7.models.artist import Artist
from XR7.models.base import SessionLocal
from xr7_common.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Per-artist task wrappers
# ---------------------------------------------------------------------------

@celery_app.task(name="xr7.modules.earnings_time_machine.run_analysis", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def task_run_earnings_time_machine(self, artist_id: str, granularity: str = "year") -> dict:  # noqa: ANN001
    from XR7.modules.earnings_time_machine import run_analysis
    return run_analysis(artist_id, granularity=granularity)


@celery_app.task(name="xr7.modules.ghost_catalog.run_scan", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def task_run_ghost_catalog_scan(self, artist_id: str) -> dict:  # noqa: ANN001
    from XR7.modules.ghost_catalog_detector import run_scan
    return run_scan(artist_id)


@celery_app.task(name="xr7.modules.black_box_countdown.refresh_countdowns", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def task_refresh_black_box_countdowns(self, artist_id: str) -> dict:  # noqa: ANN001
    from XR7.modules.black_box_countdown import refresh_countdowns
    return refresh_countdowns(artist_id)


@celery_app.task(name="xr7.modules.royalty_dna.generate_profile", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def task_generate_royalty_dna(self, artist_id: str) -> dict:  # noqa: ANN001
    from XR7.modules.royalty_dna_profile import generate_profile
    return generate_profile(artist_id)


@celery_app.task(name="xr7.modules.payer_health.refresh_scores", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def task_refresh_payer_health(self, artist_id: str) -> dict:  # noqa: ANN001
    from XR7.modules.payer_health_score import refresh_scores
    return refresh_scores(artist_id)


@celery_app.task(name="xr7.modules.contract_drift.run_quarterly_analysis", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def task_run_contract_drift_analysis(self, artist_id: str) -> dict:  # noqa: ANN001
    from XR7.modules.contract_drift_monitor import run_quarterly_analysis
    return run_quarterly_analysis(artist_id)


@celery_app.task(name="xr7.modules.catalog_value.run_appraisal", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def task_run_catalog_value_appraisal(self, artist_id: str) -> dict:  # noqa: ANN001
    from XR7.modules.catalog_value_appraiser import run_appraisal
    return run_appraisal(artist_id)


@celery_app.task(name="xr7.modules.recovery_score.recalculate", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def task_recalculate_recovery_score(self, artist_id: str) -> dict:  # noqa: ANN001
    from XR7.modules.recovery_credit_score import recalculate
    return recalculate(artist_id)


# ---------------------------------------------------------------------------
# All-artists sweep tasks (called by beat schedule)
# ---------------------------------------------------------------------------

def _iter_artist_ids(db) -> list[str]:
    artists = db.query(Artist).all()
    return [str(a.id) for a in artists]


@celery_app.task(name="xr7.modules.black_box_countdown.refresh_countdowns_all", bind=True)
def task_refresh_all_countdowns(self) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        ids = _iter_artist_ids(db)
    finally:
        db.close()
    for artist_id in ids:
        task_refresh_black_box_countdowns.delay(artist_id)
    logger.info("Dispatched black-box countdown refresh for %d artists", len(ids))
    return {"dispatched": len(ids)}


@celery_app.task(name="xr7.modules.payer_health.refresh_scores_all", bind=True)
def task_refresh_all_payer_scores(self) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        ids = _iter_artist_ids(db)
    finally:
        db.close()
    for artist_id in ids:
        task_refresh_payer_health.delay(artist_id)
    return {"dispatched": len(ids)}


@celery_app.task(name="xr7.modules.contract_drift.run_quarterly_analysis_all", bind=True)
def task_run_all_contract_drift(self) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        ids = _iter_artist_ids(db)
    finally:
        db.close()
    for artist_id in ids:
        task_run_contract_drift_analysis.delay(artist_id)
    return {"dispatched": len(ids)}


@celery_app.task(name="xr7.modules.recovery_score.recalculate_all", bind=True)
def task_recalculate_all_recovery_scores(self) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        ids = _iter_artist_ids(db)
    finally:
        db.close()
    for artist_id in ids:
        task_recalculate_recovery_score.delay(artist_id)
    return {"dispatched": len(ids)}
