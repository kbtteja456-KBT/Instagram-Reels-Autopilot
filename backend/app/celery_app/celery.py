"""Celery application configuration with Redis broker."""

from celery import Celery
from celery.schedules import crontab
from backend.app.config import settings

celery_app = Celery(
    "instagram_autopilot",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["backend.app.celery_app.tasks"]
)

# Parse slot times (e.g. 07:00, 18:00)
s1_hour, s1_min = map(int, settings.slot1_time.split(":"))
s2_hour, s2_min = map(int, settings.slot2_time.split(":"))

celery_app.conf.update(
    timezone=settings.timezone,
    enable_utc=False,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    beat_schedule={
        "morning-reel-slot-1": {
            "task": "backend.app.celery_app.tasks.run_scheduled_slot_task",
            "schedule": crontab(hour=s1_hour, minute=s1_min),
            "args": (1,)
        },
        "evening-reel-slot-2": {
            "task": "backend.app.celery_app.tasks.run_scheduled_slot_task",
            "schedule": crontab(hour=s2_hour, minute=s2_min),
            "args": (2,)
        },
        "hourly-meta-insights-sync": {
            "task": "backend.app.celery_app.tasks.sync_meta_insights_task",
            "schedule": crontab(minute=0)
        }
    }
)
