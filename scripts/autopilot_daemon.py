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
    """Check how many reels have been published today from MongoDB Atlas or local cache."""
    count = 0
    today_str = now.strftime("%Y-%m-%d")
    start_of_day_utc = datetime(now.year, now.month, now.day, tzinfo=tz).astimezone(timezone.utc)

    try:
        await AsyncMongoDB.connect()
        db = AsyncMongoDB.get_db()
        if db is not None:
            # 1. Check posted_quizzes in MongoDB Atlas
            try:
                quizzes_cursor = db.posted_quizzes.find({
                    "$or": [
                        {"created_at": {"$gte": start_of_day_utc.isoformat()}},
                        {"posted_at": {"$gte": start_of_day_utc.isoformat()}},
                        {"created_at": {"$regex": f"^{today_str}"}},
                        {"posted_at": {"$regex": f"^{today_str}"}}
                    ]
                })
                q_docs = await quizzes_cursor.to_list(length=20)
                count = max(count, len(q_docs))
            except Exception as q_err:
                daemon_logger.warning(f"MongoDB posted_quizzes check note: {q_err}")

            # 2. Check reels in MongoDB Atlas
            try:
                reels_cursor = db.reels.find({
                    "status": "PUBLISHED",
                    "instagram_published_at": {"$gte": start_of_day_utc}
                })
                r_docs = await reels_cursor.to_list(length=20)
                count = max(count, len(r_docs))
            except Exception as r_err:
                daemon_logger.warning(f"MongoDB reels check note: {r_err}")

    except Exception as e:
        daemon_logger.warning(f"MongoDB connection count note: {e}")

    # 3. Fallback to local posted_quizzes.json if DB count is 0
    if count == 0:
        posted_file = Path(settings.media_storage_dir) / "posted_quizzes.json"
        if posted_file.exists():
            import json
            try:
                with open(posted_file, "r", encoding="utf-8") as f:
                    items = json.load(f)
                    for it in items:
                        posted_at = it.get("posted_at", "") or it.get("created_at", "")
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


def is_within_slot_window(now: datetime, slot_time_str: str, window_minutes: int = 45) -> bool:
    """Check if current time is within [slot_time, slot_time + window_minutes]."""
    try:
        sh, sm = map(int, slot_time_str.split(":"))
        slot_dt = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
        diff_sec = (now - slot_dt).total_seconds()
        # Active if from exact time up to window_minutes later (e.g. 0 to 45 mins)
        return 0 <= diff_sec <= (window_minutes * 60)
    except Exception:
        return False


async def run_autopilot_daemon():
    """Main continuous loop running 24/7 with strict slot window validation."""
    daemon_logger.info("=" * 65)
    daemon_logger.info("AI Instagram Reels Autopilot 24/7 Engine Started")
    daemon_logger.info(f"Timezone: {settings.timezone} | Slots: {settings.slot1_time}, {settings.slot2_time}")
    daemon_logger.info("Slot Windows: Active for 45 minutes from each scheduled slot time")
    daemon_logger.info("Rule: No random time publishing when computer wakes up late")
    daemon_logger.info("=" * 65)

    last_trigger_signature = ""

    while True:
        try:
            tz = zoneinfo.ZoneInfo(settings.timezone)
            now = datetime.now(tz)
            today_str = now.strftime("%Y-%m-%d")
            current_hm = now.strftime("%H:%M")

            published_today = await get_published_today_count(tz, now)

            # Check if currently inside Slot 1 window (e.g., 07:00 to 07:45)
            in_slot1_window = is_within_slot_window(now, settings.slot1_time, window_minutes=45)
            # Check if currently inside Slot 2 window (e.g., 18:00 to 18:45)
            in_slot2_window = is_within_slot_window(now, settings.slot2_time, window_minutes=45)

            if in_slot1_window:
                slot_sig = f"{today_str}_slot1"
                if published_today == 0 and last_trigger_signature != slot_sig:
                    daemon_logger.info(
                        f"⏰ Slot 1 Window Active ({settings.slot1_time} {settings.timezone}, current: {current_hm}). "
                        f"Publishing Slot 1 Reel..."
                    )
                    success = await execute_publishing_with_retry()
                    if success:
                        last_trigger_signature = slot_sig

            elif in_slot2_window:
                slot_sig = f"{today_str}_slot2"
                # If slot 2 is active, allow publish if today's count < daily limit (2)
                if published_today < settings.daily_reel_limit and last_trigger_signature != slot_sig:
                    daemon_logger.info(
                        f"⏰ Slot 2 Window Active ({settings.slot2_time} {settings.timezone}, current: {current_hm}). "
                        f"Publishing Slot 2 Reel..."
                    )
                    success = await execute_publishing_with_retry()
                    if success:
                        last_trigger_signature = slot_sig

        except Exception as e:
            daemon_logger.error(f"Autopilot daemon loop error: {e}", exc_info=True)

        # Sleep 30 seconds between checks
        await asyncio.sleep(30)


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    asyncio.run(run_autopilot_daemon())
