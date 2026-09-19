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
    """Trigger the autonomous pipeline for a scheduled slot with dynamic niche and ideas."""
    logger.info(f"[AutopilotScheduler] Triggering scheduled Reel for Slot {slot_index}...")
    try:
        # 1. Resolve current active niche from MongoDB or configuration
        active_niche = getattr(settings, "niche", "python program quiz card reels")
        custom_prompt = getattr(settings, "custom_content_prompt", "")
        
        try:
            from backend.app.core.db import AsyncMongoDB
            db = AsyncMongoDB.get_db()
            if db is not None:
                doc = await db.settings.find_one({"workspace_id": "default_workspace"})
                if doc and doc.get("niche"):
                    active_niche = doc["niche"]
                if doc and doc.get("custom_content_prompt"):
                    custom_prompt = doc["custom_content_prompt"]
        except Exception as e:
            logger.warning(f"[AutopilotScheduler] Note reading settings: {e}")

        logger.info(f"[AutopilotScheduler] Active Niche for Slot {slot_index}: '{active_niche}'")

        # 2. Dynamically brainstorm ideas for this niche using IdeaAgent
        from backend.app.agents.idea import IdeaAgent
        idea_agent = IdeaAgent()
        ideas = await idea_agent.generate_ideas(niche=active_niche, count=3)
        
        topic = f"Tricky Python Quiz: What does print([1, 2] * 2) output?"
        if ideas and isinstance(ideas, list) and len(ideas) > 0:
            topic = ideas[0].get("topic", topic)
        elif custom_prompt:
            topic = custom_prompt

        logger.info(f"[AutopilotScheduler] Slot {slot_index} Selected Topic: '{topic}'")

        from backend.app.pipeline.orchestrator import create_default_orchestrator
        orchestrator = create_default_orchestrator()
        result = await orchestrator.execute_full_flow(
            topic=topic,
            niche=active_niche,
            publish_immediately=True,
            slot_index=slot_index
        )
        logger.info(f"[AutopilotScheduler] Slot {slot_index} Reel finished! Status: {result.get('status')}")
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
