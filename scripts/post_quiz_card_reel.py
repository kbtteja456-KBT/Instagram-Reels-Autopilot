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
from backend.app.pipeline.quiz_card_renderer import QuizCardRenderer
from backend.app.pipeline.audio_mixer import AudioMixer
from backend.app.pipeline.quiz_manager import QuizManager
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
                logger.warning(f"MongoDB posted_quizzes check note: {q_err}")

            # 2. Check reels in MongoDB Atlas
            try:
                reels_cursor = db.reels.find({
                    "status": "PUBLISHED",
                    "instagram_published_at": {"$gte": start_of_day_utc}
                })
                r_docs = await reels_cursor.to_list(length=20)
                count = max(count, len(r_docs))
            except Exception as r_err:
                logger.warning(f"MongoDB reels check note: {r_err}")
    except Exception as e:
        logger.warning(f"MongoDB count connection note: {e}")

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


async def main():
    parser = argparse.ArgumentParser(description="15s Countdown + Answer Reveal Quiz Reel Publisher")
    parser.add_argument("--force", action="store_true", help="Force publish regardless of time slot or daily limit")
    args = parser.parse_args()

    logger.info("=== 15-Second Countdown + Answer Reveal Quiz Reel Autopilot Engine ===")

    try:
        tz = zoneinfo.ZoneInfo(settings.timezone)
    except Exception as tz_err:
        logger.warning(f"Timezone resolution note: {tz_err}")
        tz = timezone.utc

    now = datetime.now(tz)
    today_str = now.strftime("%Y-%m-%d")
    current_hm = now.strftime("%H:%M")
    logger.info(f"Current time: {current_hm} {now.tzname()} | Target slots: Slot 1={settings.slot1_time}, Slot 2={settings.slot2_time} ({settings.timezone})")

    if not args.force:
        # Slot 1 window: e.g. 07:00 IST -> 06:25 to 08:00 IST
        in_slot1 = is_within_slot_window(now, settings.slot1_time, before_mins=35, after_mins=60)
        # Slot 2 window: e.g. 18:00 IST -> 17:25 to 19:00 IST
        in_slot2 = is_within_slot_window(now, settings.slot2_time, before_mins=35, after_mins=60)

        if not (in_slot1 or in_slot2):
            logger.warning(
                f"[Autopilot Guard] Current time {current_hm} {now.tzname()} is outside scheduled slots "
                f"(Slot 1: {settings.slot1_time}, Slot 2: {settings.slot2_time} {settings.timezone}). "
                f"Skipping execution to prevent unwanted posting at afternoon 12 or late night."
            )
            return

        published_today = await get_published_today_count(tz, now)
        logger.info(f"[Autopilot Guard] Reels published today ({today_str}): {published_today}/{settings.daily_reel_limit}")

        if in_slot1:
            if published_today >= 1:
                logger.info(
                    f"[Autopilot Guard] Slot 1 Reel already published today ({published_today} reel(s) posted). "
                    f"Skipping duplicate Slot 1 post."
                )
                return
            logger.info(f"[Autopilot Guard] Slot 1 Active ({settings.slot1_time} {settings.timezone}). Proceeding to publish morning Reel...")

        elif in_slot2:
            if published_today >= settings.daily_reel_limit:
                logger.info(
                    f"[Autopilot Guard] Daily reel limit ({settings.daily_reel_limit}) already reached for today "
                    f"({published_today} reel(s) posted). Skipping Slot 2 post."
                )
                return
            logger.info(f"[Autopilot Guard] Slot 2 Active ({settings.slot2_time} {settings.timezone}). Proceeding to publish evening Reel...")
    else:
        logger.warning("[Force Mode] Bypassing slot schedule and daily count checks.")

    quiz_mgr = QuizManager()
    quiz = quiz_mgr.get_next_unposted_quiz()
    quiz_id = quiz["quiz_id"]
    logger.info(f"Selected Fresh Quiz: '{quiz_id}' - {quiz['title']}")

    # Setup directories
    temp_dir = settings.temp_path / f"quiz_{quiz_id}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    reels_dir = settings.reels_output_path
    reels_dir.mkdir(parents=True, exist_ok=True)

    music_track_path = str(temp_dir / f"{quiz_id}_music.mp3")
    video_track_path = str(temp_dir / f"{quiz_id}_video_track.mp4")
    final_mp4_path = str(reels_dir / f"reel_{quiz_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")

    # 1. Audio: Pure Lo-Fi Music (Zero Voiceover), 20 seconds with smooth fade-out
    total_duration = 20.0
    countdown_duration = 15.0

    mixer = AudioMixer()
    logger.info(f"[1/3] Preparing pure lo-fi music track ({total_duration}s, zero voiceover)...")
    mixer.prepare_pure_music(duration_sec=total_duration, output_path=music_track_path, volume=0.90)

    # 2. Video Rendering: 15s Countdown + 5s Answer Reveal
    logger.info(f"[2/3] Rendering 1080x1920 video: 15s Countdown + 5s Answer Reveal (600 frames)...")
    renderer = QuizCardRenderer()
    renderer.render_quiz_video(
        output_video_path=video_track_path,
        quiz_data=quiz,
        total_duration_sec=total_duration,
        options_start_t=0.0,
        countdown_start_t=0.0,
        countdown_end_t=countdown_duration,
        reveal_start_t=countdown_duration,
        fps=30
    )

    logger.info("Muxing video with pure lo-fi music track...")
    renderer.assemble_final_reel(video_track_path, music_track_path, final_mp4_path)
    file_size_mb = os.path.getsize(final_mp4_path) / (1024 * 1024)
    logger.info(f"Final Reel Produced: {final_mp4_path} ({file_size_mb:.2f} MB)")

    # 3. Instagram Publishing
    logger.info("[3/3] Publishing Reel to Instagram via Meta Graph API...")
    client = InstagramClient(
        access_token=settings.effective_instagram_token,
        ig_user_id=settings.effective_instagram_account_id
    )
    agent = InstagramAgent(client)

    pub_result = await agent.publish_reel(
        video_filepath=final_mp4_path,
        caption=quiz["caption"]
    )

    instagram_url = pub_result.get("instagram_url")
    media_id = pub_result.get("instagram_media_id")

    # 4. Anti-Duplicate Registration
    quiz_mgr.record_posted_quiz(
        quiz_id=quiz_id,
        title=quiz["title"],
        media_id=str(media_id),
        instagram_url=str(instagram_url),
        file_path=final_mp4_path
    )

    try:
        now_local = datetime.now(tz)
    except Exception:
        now_local = datetime.now()

    try:
        db = AsyncMongoDB.get_db()
        if db is not None:
            await db.posted_quizzes.insert_one({
                "quiz_id": quiz_id,
                "title": quiz["title"],
                "caption": quiz["caption"],
                "file_path": final_mp4_path,
                "duration_seconds": total_duration,
                "status": "PUBLISHED",
                "instagram_media_id": media_id,
                "instagram_url": instagram_url,
                "posted_at": now_local.isoformat(),
                "posted_at_utc": datetime.now(timezone.utc).isoformat(),
                "local_time_display": now_local.strftime("%I:%M %p %Z"),
                "created_at": now_local.isoformat()
            })
    except Exception as e:
        logger.warning(f"MongoDB persistence note: {e}")

    print("\n" + "="*60)
    print("15s COUNTDOWN + ANSWER REEL PUBLISHED SUCCESSFULLY!")
    print(f"Quiz ID: {quiz_id}")
    print(f"Title: {quiz['title']}")
    print(f"Video file: {final_mp4_path}")
    print(f"Instagram Media ID: {media_id}")
    print(f"Instagram URL: {instagram_url}")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
