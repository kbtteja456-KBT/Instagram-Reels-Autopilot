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


def is_within_slot_window(now: datetime, slot_time_str: str, window_minutes: int = 45) -> bool:
    """Check if current time is within [slot_time, slot_time + window_minutes]."""
    try:
        sh, sm = map(int, slot_time_str.split(":"))
        slot_dt = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
        diff_sec = (now - slot_dt).total_seconds()
        return 0 <= diff_sec <= (window_minutes * 60)
    except Exception:
        return False


async def get_slots_published_today(now: datetime, tz: zoneinfo.ZoneInfo) -> int:
    """Check MongoDB to see how many reels/quizzes have been published today."""
    count = 0
    today_str = now.strftime("%Y-%m-%d")
    start_of_day_utc = datetime(now.year, now.month, now.day, tzinfo=tz).astimezone(datetime.now(timezone.utc).tzinfo)
    try:
        from backend.app.core.db import AsyncMongoDB
        db = AsyncMongoDB.get_db()
        if db is not None:
            # Check reels collection
            r_count = await db.reels.count_documents({
                "status": "PUBLISHED",
                "instagram_published_at": {"$gte": start_of_day_utc}
            })
            # Check posted_quizzes collection
            q_count = await db.posted_quizzes.count_documents({
                "$or": [
                    {"created_at": {"$gte": start_of_day_utc.isoformat()}},
                    {"posted_at": {"$gte": start_of_day_utc.isoformat()}},
                    {"created_at": {"$regex": f"^{today_str}"}},
                    {"posted_at": {"$regex": f"^{today_str}"}}
                ]
            })
            count = max(r_count, q_count)
    except Exception as e:
        logger.warning(f"[AutopilotScheduler] DB check note: {e}")
    return count


async def scheduler_loop() -> None:
    """Loop checking every 30 seconds if current time falls into Slot 1 or Slot 2 posting windows."""
    global _is_running
    logger.info(f"[AutopilotScheduler] Started in timezone {settings.timezone} (Slots: {settings.slot1_time}, {settings.slot2_time})")
    
    last_triggered_signature = ""

    while _is_running:
        try:
            tz = zoneinfo.ZoneInfo(settings.timezone)
            now = datetime.now(tz)
            today_str = now.strftime("%Y-%m-%d")
            current_hm = now.strftime("%H:%M")

            in_slot1 = is_within_slot_window(now, settings.slot1_time, window_minutes=45)
            in_slot2 = is_within_slot_window(now, settings.slot2_time, window_minutes=45)

            if in_slot1:
                sig = f"{today_str}_slot1"
                if sig != last_triggered_signature:
                    pub_count = await get_slots_published_today(now, tz)
                    if pub_count == 0:
                        last_triggered_signature = sig
                        logger.info(f"[AutopilotScheduler] Triggering Slot 1 Reel at {current_hm} {settings.timezone}...")
                        asyncio.create_task(run_slot_pipeline(1))

            elif in_slot2:
                sig = f"{today_str}_slot2"
                if sig != last_triggered_signature:
                    pub_count = await get_slots_published_today(now, tz)
                    if pub_count < settings.daily_reel_limit:
                        last_triggered_signature = sig
                        logger.info(f"[AutopilotScheduler] Triggering Slot 2 Reel at {current_hm} {settings.timezone}...")
                        asyncio.create_task(run_slot_pipeline(2))

        except Exception as e:
            logger.error(f"[AutopilotScheduler] Loop error: {e}", exc_info=True)

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
