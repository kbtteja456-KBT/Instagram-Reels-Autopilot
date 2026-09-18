"""Autopilot daemon status, control, and manual slot triggers."""

import zoneinfo
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.core.auth import get_optional_current_user
from backend.app.core.logging import logger
from backend.app.core.cron_scheduler import run_slot_pipeline

router = APIRouter(prefix="/autopilot", tags=["autopilot"])

_autopilot_active = True


def get_next_slot_info() -> Dict[str, Any]:
    """Compute the next upcoming slot (Slot 1 or Slot 2) and countdown."""
    try:
        tz = zoneinfo.ZoneInfo(settings.timezone)
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()

    today_s1 = now.replace(hour=int(settings.slot1_time.split(":")[0]), minute=int(settings.slot1_time.split(":")[1]), second=0, microsecond=0)
    today_s2 = now.replace(hour=int(settings.slot2_time.split(":")[0]), minute=int(settings.slot2_time.split(":")[1]), second=0, microsecond=0)

    if now < today_s1:
        next_slot = 1
        target = today_s1
    elif now < today_s2:
        next_slot = 2
        target = today_s2
    else:
        next_slot = 1
        target = today_s1 + timedelta(days=1)

    diff = int((target - now).total_seconds())
    hours = diff // 3600
    minutes = (diff % 3600) // 60

    return {
        "next_slot_index": next_slot,
        "next_slot_time": target.strftime("%H:%M"),
        "countdown_seconds": diff,
        "countdown_human": f"{hours:02d}h {minutes:02d}m"
    }


@router.get("/status")
async def get_autopilot_status(user: Dict[str, Any] = Depends(get_optional_current_user)) -> Dict[str, Any]:
    """Return status of 24/7 autonomous daemon."""
    slot_info = get_next_slot_info()
    return {
        "is_active": _autopilot_active,
        "timezone": settings.timezone,
        "slot1_time": settings.slot1_time,
        "slot2_time": settings.slot2_time,
        "daily_reel_limit": settings.daily_reel_limit,
        "zero_cost_mode": settings.zero_cost_mode,
        "next_slot": slot_info
    }


@router.post("/toggle")
async def toggle_autopilot(user: Dict[str, Any] = Depends(get_optional_current_user)) -> Dict[str, Any]:
    """Enable or pause the 24/7 autonomous scheduling daemon."""
    global _autopilot_active
    _autopilot_active = not _autopilot_active
    logger.info(f"[Autopilot] Daemon toggled to: {'ACTIVE' if _autopilot_active else 'PAUSED'}")
    return {"is_active": _autopilot_active}


@router.post("/trigger/{slot_index}")
async def trigger_manual_slot_run(
    slot_index: int,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(get_optional_current_user)
) -> Dict[str, Any]:
    """Force run a specific slot generation and publish."""
    logger.info(f"[Autopilot] Manual trigger requested for Slot {slot_index}...")
    background_tasks.add_task(run_slot_pipeline, slot_index)
    return {
        "status": "ACCEPTED",
        "message": f"Slot {slot_index} autonomous pipeline started in background."
    }
