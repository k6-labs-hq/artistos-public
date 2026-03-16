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
        "xr7-workflow-incomplete-onboarding": {
            "task": "xr7.workflow.run_onboarding_for_incomplete_artists",
            "schedule": 21600,
        },
        "xr7-workflow-recovery-new-data": {
            "task": "xr7.workflow.run_recovery_for_new_data",
            "schedule": 21600,
        },
        "xr7-workflow-follow-up-readiness": {
            "task": "xr7.workflow.run_follow_up_and_readiness",
            "schedule": 86400,
        },
    },
)

celery_app.autodiscover_tasks(["XR7.tasks"])
