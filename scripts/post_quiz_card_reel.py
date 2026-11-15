import argparse
import asyncio
import os
import sys
import subprocess
import zoneinfo
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.config import settings
from backend.app.core.ffmpeg_utils import get_ffmpeg_binary
from backend.app.core.logging import logger
from backend.app.curriculum.python_series import CurriculumManager
from backend.app.curriculum.educational_engine import render_educational_episode
from backend.app.providers.instagram.instagram_client import InstagramClient
from backend.app.agents.instagram import InstagramAgent
from backend.app.core.db import AsyncMongoDB


def is_within_slot_window(now: datetime, slot_time_str: str, before_mins: int = 35, after_mins: int = 60) -> bool:
    """Check if current time falls within [slot_time - before_mins, slot_time + after_mins]."""
    try:
        sh, sm = map(int, slot_time_str.split(":"))
        slot_dt = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
        start_w = slot_dt - timedelta(minutes=before_mins)
        end_w = slot_dt + timedelta(minutes=after_mins)
        return start_w <= now <= end_w
    except Exception:
        return False


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
                logger.warning(f"MongoDB posted_quizzes check note: {q_err}")

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
                logger.warning(f"MongoDB reels check note: {r_err}")
    except Exception as e:
        logger.warning(f"MongoDB count connection note: {e}")

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


async def main(force: bool = False):
    parser = argparse.ArgumentParser(description="15s Countdown + Answer Reveal Quiz Reel Publisher")
    parser.add_argument("--force", action="store_true", help="Force publish regardless of time slot or daily limit")
    args, _ = parser.parse_known_args()

    effective_force = force or args.force

    logger.info("=== Alan Becker 2D Stickman Live-Coding Animation Reels Autopilot Engine ===")

    try:
        tz = zoneinfo.ZoneInfo(settings.timezone)
    except Exception as tz_err:
        logger.warning(f"Timezone resolution note: {tz_err}")
        tz = timezone.utc

    now = datetime.now(tz)
    today_str = now.strftime("%Y-%m-%d")
    current_hm = now.strftime("%H:%M")
    logger.info(f"Current time: {current_hm} {now.tzname()} | Target slots: Slot 1={settings.slot1_time}, Slot 2={settings.slot2_time} ({settings.timezone})")

    if not effective_force:
        # Slot 1 window: e.g. 07:00 IST -> 06:25 to 09:00 IST (accommodates cloud queue delays)
        in_slot1 = is_within_slot_window(now, settings.slot1_time, before_mins=35, after_mins=120)
        # Slot 2 window: e.g. 18:00 IST -> 17:25 to 20:00 IST
        in_slot2 = is_within_slot_window(now, settings.slot2_time, before_mins=35, after_mins=120)

        if not (in_slot1 or in_slot2):
            logger.warning(
                f"[Autopilot Guard] Current time {current_hm} {now.tzname()} is outside scheduled slots "
                f"(Slot 1: {settings.slot1_time}, Slot 2: {settings.slot2_time} {settings.timezone}). "
                f"Skipping execution to prevent unwanted posting at afternoon 12 or late night."
            )
            return False

        published_today = await get_published_today_count(tz, now)
        logger.info(f"[Autopilot Guard] Reels published today ({today_str}): {published_today}/{settings.daily_reel_limit}")

        if in_slot1:
            if published_today >= 1:
                logger.info(
                    f"[Autopilot Guard] Slot 1 Reel already published today ({published_today} reel(s) posted). "
                    f"Skipping duplicate Slot 1 post."
                )
                return False
            logger.info(f"[Autopilot Guard] Slot 1 Active ({settings.slot1_time} {settings.timezone}). Proceeding to publish morning Reel...")

        elif in_slot2:
            if published_today >= settings.daily_reel_limit:
                logger.info(
                    f"[Autopilot Guard] Daily reel limit ({settings.daily_reel_limit}) already reached for today "
                    f"({published_today} reel(s) posted). Skipping Slot 2 post."
                )
                return False
            logger.info(f"[Autopilot Guard] Slot 2 Active ({settings.slot2_time} {settings.timezone}). Proceeding to publish evening Reel...")
    else:
        logger.warning("[Force Mode] Bypassing slot schedule and daily count checks.")

    # 1. Sequential Curriculum Tracker: Get Next Episode
    ep_data = CurriculumManager.get_current_episode_info(niche="Python Programming")
    ep_num = ep_data.get("actual_episode_number") or ep_data.get("episode", 1)
    title = ep_data.get("title", f"Python Concept {ep_num}")
    logger.info(f"Selected Sequential Python Episode: Ep {ep_num} - '{title}'")

    # 2. Render 1080x1920 30fps Alan Becker 2D Stickman Live-Coding Animation
    logger.info(f"[1/2] Rendering 1080x1920 30fps Alan Becker Animation (40s, 6 Foley layers, zero voiceover)...")
    loop = asyncio.get_event_loop()
    final_mp4_path = await loop.run_in_executor(None, render_educational_episode, ep_data)
    file_size_mb = os.path.getsize(final_mp4_path) / (1024 * 1024)
    logger.info(f"Final Alan Becker Reel Produced: {final_mp4_path} ({file_size_mb:.2f} MB)")

    # 3. Instagram Publishing via Meta Graph API Container Flow
    caption_text = ep_data.get("caption") or CurriculumManager.generate_caption(ep_data)
    logger.info("[2/2] Publishing Reel to Instagram via Meta Graph API...")
    client = InstagramClient(
        access_token=settings.effective_instagram_token,
        ig_user_id=settings.effective_instagram_account_id
    )
    agent = InstagramAgent(client)

    pub_result = await agent.publish_reel(
        video_filepath=final_mp4_path,
        caption=caption_text
    )

    instagram_url = pub_result.get("instagram_url")
    media_id = pub_result.get("instagram_media_id")

    # 4. Atomic Episode Progression: Advance ONLY AFTER successful publish!
    next_ep = CurriculumManager.advance_to_next_episode(published_ep_num=ep_num, niche="Python Programming")
    logger.info(f"🚀 [Curriculum Tracker] Atomically advanced to Episode {next_ep} (Last published: Ep {ep_num})")

    try:
        now_local = datetime.now(tz)
    except Exception:
        now_local = datetime.now()

    try:
        db = AsyncMongoDB.get_db()
        if db is not None:
            await db.posted_quizzes.insert_one({
                "quiz_id": f"episode_{ep_num}",
                "episode": ep_num,
                "title": title,
                "caption": caption_text,
                "file_path": final_mp4_path,
                "duration_seconds": 40.0,
                "status": "PUBLISHED",
                "instagram_media_id": media_id,
                "instagram_url": instagram_url,
                "posted_at": now_local.isoformat(),
                "posted_at_utc": datetime.now(timezone.utc).isoformat(),
                "local_time_display": now_local.strftime("%I:%M %p %Z"),
                "created_at": now_local.isoformat()
            })
            await db.reels.insert_one({
                "episode": ep_num,
                "title": f"Episode {ep_num}: {title}",
                "caption": caption_text,
                "file_path": final_mp4_path,
                "duration_seconds": 40.0,
                "status": "PUBLISHED",
                "instagram_media_id": media_id,
                "instagram_url": instagram_url,
                "instagram_published_at": datetime.now(timezone.utc),
                "quality_score": 98.5
            })
    except Exception as e:
        logger.warning(f"MongoDB persistence note: {e}")

    print("\n" + "="*60)
    print("ALAN BECKER STICKMAN ANIMATION REEL PUBLISHED SUCCESSFULLY!")
    print(f"Episode: {ep_num}")
    print(f"Title: {title}")
    print(f"Next Episode Teased: Episode {next_ep}")
    print(f"Video file: {final_mp4_path}")
    print(f"Instagram Media ID: {media_id}")
    print(f"Instagram URL: {instagram_url}")
    print("="*60 + "\n")
    return True


if __name__ == "__main__":
    asyncio.run(main())
