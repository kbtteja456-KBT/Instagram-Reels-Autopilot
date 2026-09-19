"""Self-healing catch-up script: checks if any daily slot was missed and auto-publishes."""

import asyncio
import os
import sys
from datetime import datetime, timezone
import zoneinfo
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.db import AsyncMongoDB
from backend.app.pipeline.quiz_manager import QuizManager
from scripts.post_quiz_card_reel import main as post_new_quiz_reel


async def check_and_recover():
    logger.info("=== Fail-Safe Recovery: Checking for missed daily Reel slots ===")
    
    tz = zoneinfo.ZoneInfo(settings.timezone)
    now = datetime.now(tz)
    today_str = now.strftime("%Y-%m-%d")
    current_hour = now.hour

    # Slot 1: 07:00 AM (Hour 7)
    # Slot 2: 06:00 PM (Hour 18)
    slots_due = []
    if current_hour >= 7:
        slots_due.append(1)
    if current_hour >= 18:
        slots_due.append(2)

    logger.info(f"Current Time: {now.strftime('%H:%M:%S')} {settings.timezone} | Slots due so far today: {slots_due}")

    await AsyncMongoDB.connect()
    db = AsyncMongoDB.get_db()

    # Check which slots have already published today
    published_today_count = 0
    if db is not None:
        try:
            start_of_day = datetime(now.year, now.month, now.day, tzinfo=tz).astimezone(timezone.utc)
            cursor = db.reels.find({
                "status": "PUBLISHED",
                "instagram_published_at": {"$gte": start_of_day}
            })
            docs = await cursor.to_list(length=10)
            published_today_count = len(docs)
            logger.info(f"Reels published today on Instagram: {published_today_count}")
        except Exception as e:
            logger.warning(f"DB check note: {e}")

    # Check if a slot was missed
    if published_today_count < len(slots_due):
        missed = len(slots_due) - published_today_count
        logger.warning(f"⚠️ Detected {missed} missed Reel slot(s) for today! Initiating automatic recovery...")
        for i in range(missed):
            logger.info(f"Triggering recovery publish ({i+1}/{missed})...")
            await post_new_quiz_reel()
            logger.info(f"Recovery publish {i+1} completed successfully!")
    else:
        logger.info("✅ All scheduled slots for today have been successfully published. No recovery needed.")


if __name__ == "__main__":
    asyncio.run(check_and_recover())
