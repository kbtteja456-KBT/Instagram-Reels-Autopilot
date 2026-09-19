"""Generate and post a 15s Countdown + Answer Reveal Reel (Pure Music, Zero Voiceover) to Instagram."""

import asyncio
import os
import sys
import subprocess
from datetime import datetime, timezone
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


async def main():
    logger.info("=== 15-Second Countdown + Answer Reveal Quiz Reel (Pure Music, Zero Voiceover) ===")

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
                "created_at": datetime.now(timezone.utc).isoformat()
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
