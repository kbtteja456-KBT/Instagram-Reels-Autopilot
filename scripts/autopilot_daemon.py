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
    """Accurately check how many unique reels have been published today in the specified timezone."""
    published_reels = set()
    today_date = now.date()

    try:
        await AsyncMongoDB.connect()
        db = AsyncMongoDB.get_db()
        if db is not None:
            # 1. Check posted_quizzes in MongoDB Atlas
            try:
                async for doc in db.posted_quizzes.find():
                    media_id = str(doc.get("media_id") or "").strip()
                    if not media_id or media_id == "None" or media_id.startswith("mock"):
                        continue
                    ts_val = doc.get("posted_at_utc") or doc.get("posted_at") or doc.get("created_at")
                    if not ts_val:
                        continue
                    try:
                        if isinstance(ts_val, datetime):
                            dt = ts_val
                        else:
                            dt = datetime.fromisoformat(str(ts_val))
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        local_dt = dt.astimezone(tz)
                        if local_dt.date() == today_date:
                            published_reels.add(doc.get("quiz_id") or media_id)
                    except Exception:
                        pass
            except Exception as q_err:
                daemon_logger.warning(f"MongoDB posted_quizzes check note: {q_err}")

            # 2. Check reels in MongoDB Atlas
            try:
                async for doc in db.reels.find({"status": "PUBLISHED"}):
                    pub_at = doc.get("instagram_published_at")
                    if not pub_at:
                        continue
                    try:
                        if isinstance(pub_at, datetime):
                            dt = pub_at
                        else:
                            dt = datetime.fromisoformat(str(pub_at))
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        local_dt = dt.astimezone(tz)
                        if local_dt.date() == today_date:
                            published_reels.add(str(doc.get("id", doc.get("_id"))))
                    except Exception:
                        pass
            except Exception as r_err:
                daemon_logger.warning(f"MongoDB reels check note: {r_err}")

    except Exception as e:
        daemon_logger.warning(f"MongoDB connection count note: {e}")

    # 3. Check local posted_quizzes.json if DB has 0
    if not published_reels:
        posted_file = Path(settings.media_storage_dir) / "posted_quizzes.json"
        if posted_file.exists():
            import json
            try:
                with open(posted_file, "r", encoding="utf-8") as f:
                    items = json.load(f)
                    for it in items:
                        media_id = str(it.get("media_id") or "").strip()
                        if not media_id or media_id == "None" or media_id.startswith("mock"):
                            continue
                        ts_val = it.get("posted_at_utc") or it.get("posted_at") or it.get("created_at")
                        if not ts_val:
                            continue
                        try:
                            if isinstance(ts_val, datetime):
                                dt = ts_val
                            else:
                                dt = datetime.fromisoformat(str(ts_val))
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            local_dt = dt.astimezone(tz)
                            if local_dt.date() == today_date:
                                published_reels.add(it.get("quiz_id") or media_id)
                        except Exception:
                            pass
            except Exception:
                pass

    return len(published_reels)


async def execute_publishing_with_retry(max_attempts: int = 3, force: bool = False) -> bool:
    """Execute reel creation and publishing with automatic retry on transient failures."""
    for attempt in range(1, max_attempts + 1):
        try:
            daemon_logger.info(f"Initiating autonomous reel publish (Attempt {attempt}/{max_attempts})...")
            await post_quiz_reel(force=force)
            daemon_logger.info("Reel published successfully!")
            return True
        except Exception as e:
            daemon_logger.error(f"Publishing attempt {attempt} failed: {e}", exc_info=True)
            if attempt < max_attempts:
                wait_sec = attempt * 40
                daemon_logger.info(f"Retrying in {wait_sec} seconds...")
                await asyncio.sleep(wait_sec)
    return False


def is_within_slot_window(now: datetime, slot_time_str: str, window_minutes: int = 120) -> bool:
    """Check if current time is within [slot_time, slot_time + window_minutes]."""
    try:
        sh, sm = map(int, slot_time_str.split(":"))
        slot_dt = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
        diff_sec = (now - slot_dt).total_seconds()
        # Active if from exact time up to window_minutes later (e.g. 0 to 120 mins)
        return 0 <= diff_sec <= (window_minutes * 60)
    except Exception:
        return False


async def run_autopilot_daemon():
    """Main continuous loop running 24/7 with strict slot window validation."""
    daemon_logger.info("=" * 65)
    daemon_logger.info("AI Instagram Reels Autopilot 24/7 Engine Started")
    daemon_logger.info(f"Timezone: {settings.timezone} | Slots: {settings.slot1_time}, {settings.slot2_time}")
    daemon_logger.info("Slot Windows: Active for 120 minutes from each scheduled slot time")
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

            # Check if currently inside Slot 1 window (e.g., 07:00 to 09:00)
            in_slot1_window = is_within_slot_window(now, settings.slot1_time, window_minutes=120)
            # Check if currently inside Slot 2 window (e.g., 18:00 to 20:00)
            in_slot2_window = is_within_slot_window(now, settings.slot2_time, window_minutes=120)

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
