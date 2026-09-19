"""24/7 Fully Autonomous Headless Daemon for AI Instagram Reels Autopilot.

Features:
- Completely headless (runs 24/7 in background, zero user interaction required).
- Self-healing catch-up: if computer was asleep/off at 07:00 or 18:00, auto-publishes immediately upon wake.
- Persistent deduplication synced with MongoDB Atlas and local cache.
- Dedicated logging to media_storage/autopilot_daemon.log.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime, timezone
import zoneinfo
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.config import settings
from backend.app.core.db import AsyncMongoDB
from scripts.post_quiz_card_reel import main as post_quiz_reel

# Setup dedicated file + console logging
LOG_FILE = BASE_DIR / "media_storage" / "autopilot_daemon.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

daemon_logger = logging.getLogger("autopilot_daemon")
daemon_logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

file_h = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_h.setFormatter(formatter)
daemon_logger.addHandler(file_h)

stream_h = logging.StreamHandler(sys.stdout)
stream_h.setFormatter(formatter)
daemon_logger.addHandler(stream_h)


async def get_published_today_count(tz: zoneinfo.ZoneInfo, now: datetime) -> int:
    """Check how many reels have been published today from MongoDB or local cache."""
    count = 0
    try:
        await AsyncMongoDB.connect()
        db = AsyncMongoDB.get_db()
        if db is not None:
            start_of_day = datetime(now.year, now.month, now.day, tzinfo=tz).astimezone(timezone.utc)
            cursor = db.reels.find({
                "status": "PUBLISHED",
                "instagram_published_at": {"$gte": start_of_day}
            })
            docs = await cursor.to_list(length=20)
            count = len(docs)
    except Exception as e:
        daemon_logger.warning(f"MongoDB count note: {e}")

    # Fallback to local posted_quizzes.json if DB unavailable
    if count == 0:
        posted_file = Path(settings.media_storage_dir) / "posted_quizzes.json"
        if posted_file.exists():
            import json
            try:
                with open(posted_file, "r", encoding="utf-8") as f:
                    items = json.load(f)
                    today_str = now.strftime("%Y-%m-%d")
                    for it in items:
                        posted_at = it.get("posted_at", "")
                        if posted_at.startswith(today_str):
                            count += 1
            except Exception:
                pass

    return count


async def execute_publishing_with_retry(max_attempts: int = 3) -> bool:
    """Execute reel creation and publishing with automatic retry on transient failures."""
    for attempt in range(1, max_attempts + 1):
        try:
            daemon_logger.info(f"Initiating autonomous reel publish (Attempt {attempt}/{max_attempts})...")
            await post_quiz_reel()
            daemon_logger.info("Reel published successfully!")
            return True
        except Exception as e:
            daemon_logger.error(f"Publishing attempt {attempt} failed: {e}", exc_info=True)
            if attempt < max_attempts:
                wait_sec = attempt * 40
                daemon_logger.info(f"Retrying in {wait_sec} seconds...")
                await asyncio.sleep(wait_sec)
    return False


async def run_autopilot_daemon():
    """Main continuous loop running 24/7."""
    daemon_logger.info("=" * 65)
    daemon_logger.info("AI Instagram Reels Autopilot 24/7 Engine Started")
    daemon_logger.info(f"Timezone: {settings.timezone} | Slots: {settings.slot1_time}, {settings.slot2_time}")
    daemon_logger.info("Mode: Full Zero-Interaction Autopilot with Self-Healing Catch-Up")
    daemon_logger.info("=" * 65)

    last_trigger_signature = ""

    while True:
        try:
            tz = zoneinfo.ZoneInfo(settings.timezone)
            now = datetime.now(tz)
            today_str = now.strftime("%Y-%m-%d")
            current_hour = now.hour
            current_minute = now.minute
            current_hm = now.strftime("%H:%M")

            # Determine which slots are due so far today:
            # Slot 1 is due if hour >= 7 (07:00 AM)
            # Slot 2 is due if hour >= 18 (06:00 PM)
            slot1_h, slot1_m = map(int, settings.slot1_time.split(":"))
            slot2_h, slot2_m = map(int, settings.slot2_time.split(":"))

            slots_due_count = 0
            if (current_hour > slot1_h) or (current_hour == slot1_h and current_minute >= slot1_m):
                slots_due_count += 1
            if (current_hour > slot2_h) or (current_hour == slot2_h and current_minute >= slot2_m):
                slots_due_count += 1

            published_today = await get_published_today_count(tz, now)

            # 1. Self-Healing Missed Slot Catch-Up
            if published_today < slots_due_count:
                missed = slots_due_count - published_today
                daemon_logger.warning(
                    f"⚠️ Self-Healing Trigger: {missed} missed slot(s) detected today "
                    f"(Due: {slots_due_count}, Published: {published_today}). Auto-publishing now..."
                )
                success = await execute_publishing_with_retry()
                if success:
                    last_trigger_signature = f"{today_str}_{slots_due_count}"

            # 2. Exact Slot Trigger Check
            elif current_hm in [settings.slot1_time, settings.slot2_time]:
                slot_num = 1 if current_hm == settings.slot1_time else 2
                trigger_sig = f"{today_str}_slot{slot_num}"
                if trigger_sig != last_trigger_signature:
                    daemon_logger.info(f"⏰ Exact Scheduled Slot {slot_num} ({current_hm} {settings.timezone}) triggered!")
                    success = await execute_publishing_with_retry()
                    if success:
                        last_trigger_signature = trigger_sig

        except Exception as e:
            daemon_logger.error(f"Autopilot daemon loop error: {e}", exc_info=True)

        # Sleep 45 seconds between checks
        await asyncio.sleep(45)


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    asyncio.run(run_autopilot_daemon())
