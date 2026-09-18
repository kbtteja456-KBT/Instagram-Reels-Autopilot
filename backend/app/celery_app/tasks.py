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
        orchestrator = create_default_orchestrator()
        return await orchestrator.execute_full_flow(
            topic="Top 3 Breakthrough Technologies Shaping 2026",
            niche="Technology & AI",
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
