from __future__ import annotations

from celery import Celery

from xr7_common.settings import settings

celery_app = Celery(
    "xr7",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    beat_schedule={
        "xr7-requeue-due-sync-jobs": {
            "task": "xr7.sync_jobs.requeue_due",
            "schedule": max(15, int(settings.sync_requeue_seconds or 60)),
        },
        "xr7-aggregate-feedback-calibration": {
            "task": "xr7.pipeline.aggregate_feedback_calibration_all",
            "schedule": 900,
        },
        "xr7-auto-escalate-claims": {
            "task": "xr7.pipeline.auto_escalate_claims",
            "schedule": 1800,
        },
        "xr7-notify-deadline-risk": {
            "task": "xr7.pipeline.notify_deadline_risk",
            "schedule": 3600,
        },
        "xr7-weekly-artist-digest": {
            "task": "xr7.pipeline.weekly_artist_digest",
            "schedule": 604800,
        },
        "xr7-nightly-advance-ensemble": {
            "task": "xr7.pipeline.nightly_advance_ensemble",
            "schedule": 86400,
        },
        "xr7-two-agent-nightly-preparation-scan": {
            "task": "xr7.workflow.run_nightly_preparation_scan",
            "schedule": 86400,
        },
        "xr7-two-agent-daily-recovery-scan": {
            "task": "xr7.workflow.run_daily_recovery_scan",
            "schedule": 86400,
        },
        "xr7-workflow-soundcloud-sync-daily": {
            "task": "xr7.workflow.run_soundcloud_sync_daily",
            "schedule": 86400,
        },
        "xr7-workflow-soundcloud-healthcheck-hourly": {
            "task": "xr7.workflow.run_soundcloud_healthcheck_hourly",
            "schedule": 3600,
        },
        # ── Fingerprinting subsystem ────────────────────────────────────────
        "fp-provider-health-check-hourly": {
            "task": "fp.provider_health_check_all",
            "schedule": 3600,
        },
        "fp-reprocess-failed-jobs-every-15min": {
            "task": "fp.reprocess_failed_jobs",
            "schedule": 900,
        },
        "fp-anomaly-detection-sweep-nightly": {
            "task": "fp.anomaly_detection_sweep",
            "schedule": 86400,
        },
        # ── Black-box / unclaimed royalties ────────────────────────────────
        "xr7-blackbox-weekly-sweep": {
            "task": "xr7.tasks.blackbox.scan_all_artists_blackbox",
            "schedule": 604800,  # weekly
        },
        # ── Ops: backup / restore validation ─────────────────────────────
        "xr7-ops-backup-restore-validation-weekly": {
            "task": "xr7.tasks.ops.validate_backup_restore",
            "schedule": 604800,  # weekly
        },
        "xr7-ops-backup-database-to-s3-daily": {
            "task": "xr7.tasks.ops.backup_database_to_s3",
            "schedule": 86400,  # daily
        },
        "xr7-pipeline-monthly-recovery-report": {
            "task": "xr7.pipeline.monthly_recovery_report",
            "schedule": 2592000,  # ~30 days
        },
        "xr7-webhooks-redeliver-failed": {
            "task": "xr7.webhooks.redeliver_failed",
            "schedule": 300,
        },
        # ── XR7 Engine 2 — new modules ────────────────────────────────────
        "xr7-black-box-countdown-hourly": {
            "task": "xr7.modules.black_box_countdown.refresh_countdowns_all",
            "schedule": 3600,  # hourly
        },
        "xr7-payer-health-score-weekly": {
            "task": "xr7.modules.payer_health.refresh_scores_all",
            "schedule": 604800,  # weekly
        },
        "xr7-contract-drift-quarterly": {
            "task": "xr7.modules.contract_drift.run_quarterly_analysis_all",
            "schedule": 7776000,  # ~90 days
        },
        "xr7-recovery-score-daily": {
            "task": "xr7.modules.recovery_score.recalculate_all",
            "schedule": 86400,  # daily
        },
    },
)

celery_app.autodiscover_tasks(["XR7.tasks", "XR7.fingerprinting", "XR7.modules"])
