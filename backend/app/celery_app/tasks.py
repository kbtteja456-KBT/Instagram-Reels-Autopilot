"""Celery background tasks for scheduled video production and Meta insights sync."""

import asyncio
from backend.app.celery_app.celery import celery_app
from backend.app.core.logging import logger
from backend.app.pipeline.orchestrator import create_default_orchestrator
from backend.app.agents.analytics import AnalyticsAgent


@celery_app.task(name="backend.app.celery_app.tasks.run_scheduled_slot_task")
def run_scheduled_slot_task(slot_index: int):
    """Execute autonomous Reel creation and publishing for a scheduled slot."""
    logger.info(f"[Celery] Executing scheduled slot {slot_index} Reel pipeline...")
    
    async def _async_exec():
        from backend.app.config import settings
        from backend.app.agents.idea import IdeaAgent
        
        active_niche = getattr(settings, "niche", "python program quiz card reels")
        try:
            from backend.app.core.db import AsyncMongoDB
            db = AsyncMongoDB.get_db()
            if db is not None:
                doc = await db.settings.find_one({"workspace_id": "default_workspace"})
                if doc and doc.get("niche"):
                    active_niche = doc["niche"]
        except Exception:
            pass

        idea_agent = IdeaAgent()
        ideas = await idea_agent.generate_ideas(niche=active_niche, count=3)
        topic = "Tricky Python Quiz: What does print([1, 2] * 2) output?"
        if ideas and isinstance(ideas, list) and len(ideas) > 0:
            topic = ideas[0].get("topic", topic)

        orchestrator = create_default_orchestrator()
        return await orchestrator.execute_full_flow(
            topic=topic,
            niche=active_niche,
            publish_immediately=True,
            slot_index=slot_index
        )

    loop = asyncio.get_event_loop()
    if loop.is_running():
        res = asyncio.run_coroutine_threadsafe(_async_exec(), loop).result()
    else:
        res = asyncio.run(_async_exec())

    logger.info(f"[Celery] Slot {slot_index} completed with status: {res.get('status')}")
    return res


@celery_app.task(name="backend.app.celery_app.tasks.sync_meta_insights_task")
def sync_meta_insights_task():
    """Hourly sync of Instagram followers and Reel plays from Meta Graph API."""
    logger.info("[Celery] Executing hourly Meta Graph API insights sync...")
    
    async def _async_sync():
        agent = AnalyticsAgent()
        return await agent.sync_account_insights()

    res = asyncio.run(_async_sync())
    logger.info(f"[Celery] Meta insights synced: {res}")
    return res
