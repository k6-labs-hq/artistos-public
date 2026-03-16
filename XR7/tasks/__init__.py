"""Celery task package for XR7."""

# Import task modules for side-effect registration with Celery.
from XR7.tasks import celery_tasks as _celery_tasks  # noqa: F401
from XR7.tasks import hubspot as _hubspot  # noqa: F401
from XR7.tasks import pipeline as _pipeline  # noqa: F401
from XR7.tasks import sync_jobs as _sync_jobs  # noqa: F401
