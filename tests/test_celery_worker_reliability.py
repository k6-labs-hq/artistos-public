"""
Test Celery worker reliability configuration.

CRITICAL PRODUCTION SETTINGS: These tests verify that Celery workers are
configured to prevent task loss and duplication during pod restarts.

Without these settings:
- Tasks can be lost when workers crash mid-execution
- Tasks can be duplicated when pods restart
- Work can be permanently lost without acknowledgment
- K8s rolling deployments cause data loss

With proper configuration:
- task_acks_late=True: Tasks acknowledged AFTER completion
- task_reject_on_worker_lost=True: Tasks re-queued if worker dies
- worker_prefetch_multiplier=4: Balanced throughput (not too aggressive)
"""

from __future__ import annotations

import pytest


def test_celery_task_acks_late_enabled():
    """
    Verify task_acks_late=True to prevent task loss on worker crash.

    Without this setting:
    - Worker crashes after receiving task but before completing it
    - Task is already acknowledged to broker
    - Work is permanently lost

    With task_acks_late=True:
    - Worker completes task execution
    - THEN acknowledges to broker
    - If worker crashes, broker knows task wasn't completed
    - Broker re-queues the task for another worker
    """
    from XR7.celery_app import celery_app

    assert celery_app.conf.task_acks_late is True, (
        "task_acks_late must be True to prevent task loss during pod restarts. "
        "Tasks should be acknowledged AFTER completion, not on receipt."
    )


def test_celery_task_reject_on_worker_lost_enabled():
    """
    Verify task_reject_on_worker_lost=True to re-queue tasks if worker dies.

    Without this setting:
    - Worker dies with in-flight tasks
    - Tasks are removed from queue (lost forever)
    - No retry, no recovery

    With task_reject_on_worker_lost=True:
    - Worker dies with in-flight tasks
    - Broker detects worker loss
    - Tasks are automatically returned to queue
    - Another worker picks them up
    """
    from XR7.celery_app import celery_app

    assert celery_app.conf.task_reject_on_worker_lost is True, (
        "task_reject_on_worker_lost must be True to recover from worker crashes. "
        "Tasks should be re-queued if worker dies unexpectedly."
    )


def test_celery_worker_prefetch_multiplier_configured():
    """
    Verify worker_prefetch_multiplier=4 for balanced throughput.

    This setting controls how many tasks a worker fetches from the broker
    at once. Too low = inefficient (constant broker roundtrips). Too high =
    unfair distribution (one worker hoards all tasks).

    worker_prefetch_multiplier=4 is a balanced setting:
    - Reduces broker roundtrip overhead
    - Allows fair distribution across workers
    - Limits task loss if worker crashes (max 4 tasks lost)
    """
    from XR7.celery_app import celery_app

    assert celery_app.conf.worker_prefetch_multiplier == 4, (
        "worker_prefetch_multiplier should be 4 for balanced throughput. "
        "This prevents one worker from hoarding all tasks while allowing efficient batching."
    )


def test_celery_reliability_settings_work_together():
    """
    Integration test: All three settings must work together.

    These settings form a reliability triad:
    1. task_acks_late: Don't acknowledge until done
    2. task_reject_on_worker_lost: Re-queue if worker dies
    3. worker_prefetch_multiplier: Limit blast radius (max 4 tasks lost per worker)

    Together they ensure:
    - Pod restarts don't lose work
    - K8s rolling deployments are safe
    - Worker crashes trigger automatic recovery
    - Tasks execute exactly once (or retry with idempotency)
    """
    from XR7.celery_app import celery_app

    config = celery_app.conf

    # All three critical settings must be enabled
    assert config.task_acks_late is True
    assert config.task_reject_on_worker_lost is True
    assert config.worker_prefetch_multiplier == 4

    # Verify other essential settings still present
    assert config.task_serializer == "json"
    assert config.result_serializer == "json"
    assert config.timezone == "UTC"
    assert config.task_track_started is True


@pytest.mark.parametrize(
    "setting_name,expected_value,reason",
    [
        (
            "task_acks_late",
            True,
            "Prevents task loss when worker crashes mid-execution",
        ),
        (
            "task_reject_on_worker_lost",
            True,
            "Returns tasks to queue if worker dies unexpectedly",
        ),
        (
            "worker_prefetch_multiplier",
            4,
            "Balances throughput with fair task distribution",
        ),
    ],
)
def test_celery_reliability_setting_present(
    setting_name: str, expected_value: bool | int, reason: str
):
    """
    Parametrized test for each reliability setting.

    This test documents WHY each setting matters and verifies it's configured.
    """
    from XR7.celery_app import celery_app

    actual_value = getattr(celery_app.conf, setting_name)
    assert actual_value == expected_value, (
        f"{setting_name} must be {expected_value}. "
        f"Reason: {reason}. "
        f"Current value: {actual_value}"
    )


def test_celery_app_broker_connection_retry():
    """
    Verify broker connection retry is enabled (existing setting).

    This prevents worker crash-loops if Redis/RabbitMQ is temporarily down.
    Workers should retry connection instead of failing fast.
    """
    from XR7.celery_app import celery_app

    assert celery_app.conf.broker_connection_retry_on_startup is True, (
        "broker_connection_retry_on_startup must be True to handle Redis downtime. "
        "Workers should retry connection instead of crashing."
    )
