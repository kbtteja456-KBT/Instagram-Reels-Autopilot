"""Autonomous background daily slot scheduler for 24/7 Instagram Reels production."""

import asyncio
import zoneinfo
from datetime import datetime, time as dtime
from typing import Optional
from backend.app.config import settings
from backend.app.core.logging import logger

_scheduler_task: Optional[asyncio.Task] = None
_is_running = False


async def run_slot_pipeline(slot_index: int) -> None:
    """Trigger the autonomous pipeline for a scheduled slot."""
    logger.info(f"[AutopilotScheduler] Triggering scheduled Reel for Slot {slot_index}...")
    try:
        from backend.app.pipeline.orchestrator import create_default_orchestrator
        orchestrator = create_default_orchestrator()
        result = await orchestrator.execute_full_flow(
            topic="Top Tech & AI Breakthroughs Changing The World",
            niche="Technology & AI",
            publish_immediately=True,
            slot_index=slot_index
        )
        logger.info(f"[AutopilotScheduler] Slot {slot_index} Reel published! Status: {result.get('status')}")
    except Exception as e:
        logger.error(f"[AutopilotScheduler] Slot {slot_index} pipeline error: {e}", exc_info=True)


async def scheduler_loop() -> None:
    """Loop checking every 30 seconds if current time matches Slot 1 or Slot 2."""
    global _is_running
    logger.info(f"[AutopilotScheduler] Started in timezone {settings.timezone} (Slots: {settings.slot1_time}, {settings.slot2_time})")
    
    last_triggered_date = ""
    last_triggered_slot = -1

    while _is_running:
        try:
            tz = zoneinfo.ZoneInfo(settings.timezone)
            now = datetime.now(tz)
            today_str = now.strftime("%Y-%m-%d")
            current_hm = now.strftime("%H:%M")

            if current_hm == settings.slot1_time and (today_str != last_triggered_date or last_triggered_slot != 1):
                last_triggered_date = today_str
                last_triggered_slot = 1
                asyncio.create_task(run_slot_pipeline(1))

            elif current_hm == settings.slot2_time and (today_str != last_triggered_date or last_triggered_slot != 2):
                last_triggered_date = today_str
                last_triggered_slot = 2
                asyncio.create_task(run_slot_pipeline(2))

        except Exception as e:
            logger.error(f"[AutopilotScheduler] Loop error: {e}")

        await asyncio.sleep(30)


def start_autopilot_scheduler() -> None:
    global _scheduler_task, _is_running
    if _scheduler_task is None or _scheduler_task.done():
        _is_running = True
        _scheduler_task = asyncio.create_task(scheduler_loop())
        logger.info("[AutopilotScheduler] Scheduler daemon spawned.")


def stop_autopilot_scheduler() -> None:
    global _scheduler_task, _is_running
    _is_running = False
    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
        logger.info("[AutopilotScheduler] Scheduler daemon cancelled.")
