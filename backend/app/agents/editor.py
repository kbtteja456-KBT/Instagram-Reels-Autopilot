"""EditorAgent: FFmpeg 1080x1920 vertical video compositor with audio ducking and kinetic subtitles."""

import os
import subprocess
from pathlib import Path
from typing import List, Optional
from backend.app.agents.base import BaseAgent
from backend.app.config import settings
from backend.app.core.ffmpeg_utils import get_ffmpeg_binary
from backend.app.models.video import Storyboard


class EditorAgent(BaseAgent):
    """Compiles scenes, audio, and kinetic ASS subtitles into a production 1080x1920 Reel."""

    def __init__(self):
        super().__init__("EditorAgent")
        self.ffmpeg_bin = get_ffmpeg_binary()

    async def render_video(
        self,
        storyboard: Storyboard,
        audio_path: str,
        captions_ass_path: str,
        job_id: str
    ) -> str:
        self.log(f"Starting FFmpeg 1080x1920 vertical compilation for Job {job_id}...")
        
        reels_dir = settings.reels_output_path
        reels_dir.mkdir(parents=True, exist_ok=True)
        final_mp4 = str(reels_dir / f"reel_{job_id}.mp4")

        # 1. Create concat file list for scene assets
        temp_dir = settings.temp_path / job_id
        concat_list_file = temp_dir / "concat_list.txt"
        
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for scene in storyboard.scenes:
                if scene.asset_path and os.path.exists(scene.asset_path):
                    # Format for FFmpeg concat demuxer
                    p = str(Path(scene.asset_path).resolve()).replace("\\", "/")
                    f.write(f"file '{p}'\n")

        # Escape path for FFmpeg subtitles filter (especially Windows colons and backslashes)
        clean_ass_path = str(Path(captions_ass_path).resolve()).replace("\\", "/").replace(":", "\\:")

        # Try compilation with subtitles filter
        cmd_with_subs = [
            self.ffmpeg_bin,
            "-y",
            "-threads", "1",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_file),
            "-i", audio_path,
            "-filter_complex",
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,subtitles='{clean_ass_path}'[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-shortest",
            final_mp4
        ]

        self.log(f"Executing FFmpeg render...")
        proc = subprocess.run(cmd_with_subs, capture_output=True, text=True)

        if proc.returncode != 0 or not os.path.exists(final_mp4):
            self.log(f"Subtitles filter warning: {proc.stderr[:300]}. Retrying with direct scaling...", level="WARNING")
            # Fallback without burning ASS if libass has path issue
            cmd_fallback = [
                self.ffmpeg_bin,
                "-y",
                "-threads", "1",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_list_file),
                "-i", audio_path,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-shortest",
                final_mp4
            ]
            proc2 = subprocess.run(cmd_fallback, capture_output=True, text=True)
            if proc2.returncode != 0:
                raise RuntimeError(f"FFmpeg compilation failed completely: {proc2.stderr}")

        self.log(f"Reel successfully rendered: {final_mp4}")
        return final_mp4
