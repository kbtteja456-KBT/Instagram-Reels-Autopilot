"""Audio mixer for Reel production: voiceover synthesis + background music ducking."""

import os
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional
import edge_tts

from backend.app.config import settings
from backend.app.core.ffmpeg_utils import get_ffmpeg_binary
from backend.app.core.logging import logger

# Royalty-free chill lo-fi background music URL
LOFI_MUSIC_URL = "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=lofi-study-112191.mp3"


class AudioMixer:
    """Combines neural TTS voiceover with background music using FFmpeg."""

    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_binary()
        self.assets_dir = Path(settings.media_storage_dir) / "assets"
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.cached_music_path = self.assets_dir / "lofi_bg_music.mp3"

    def ensure_background_music(self) -> str:
        """Download and cache background lo-fi music if not already present."""
        if not self.cached_music_path.exists() or self.cached_music_path.stat().st_size < 10000:
            logger.info("[AudioMixer] Downloading royalty-free lo-fi background music...")
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                req = urllib.request.Request(LOFI_MUSIC_URL, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    with open(self.cached_music_path, "wb") as f:
                        f.write(resp.read())
                logger.info(f"[AudioMixer] Saved background music to {self.cached_music_path}")
            except Exception as e:
                logger.warning(f"[AudioMixer] Failed downloading background music: {e}. Generating procedural ambient tone.")
                self._generate_fallback_ambient(str(self.cached_music_path), duration_sec=40)
        return str(self.cached_music_path)

    def _generate_fallback_ambient(self, out_path: str, duration_sec: int = 40):
        """Generate subtle chill ambient audio using FFmpeg aevalsrc if offline."""
        cmd = [
            self.ffmpeg_bin, "-y",
            "-f", "lavfi",
            "-i", f"sine=frequency=220:sample_rate=44100:duration={duration_sec}",
            "-filter_complex", "volume=0.08,lowpass=f=400",
            out_path
        ]
        subprocess.run(cmd, capture_output=True)

    async def synthesize_voiceover(self, text: str, output_path: str, voice: str = "en-US-ChristopherNeural") -> str:
        """Synthesize neural voiceover using Edge-TTS."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(text=text, voice=voice, rate="+3%", pitch="+0Hz")
        await communicate.save(output_path)
        logger.info(f"[AudioMixer] Synthesized voiceover: {output_path}")
        return output_path

    def mix_voice_and_music(
        self,
        voiceover_path: str,
        music_path: str,
        output_path: str,
        music_volume: float = 0.16,
        voice_volume: float = 1.05
    ) -> str:
        """Mix voiceover and background music with ducking so voice is prominent."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.ffmpeg_bin, "-y",
            "-i", voiceover_path,
            "-i", music_path,
            "-filter_complex",
            f"[0:a]volume={voice_volume}[v_audio];"
            f"[1:a]volume={music_volume},aloop=loop=-1:size=2e+09[bg_music];"
            f"[v_audio][bg_music]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "[aout]",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            output_path
        ]

        logger.info("[AudioMixer] Executing FFmpeg audio ducking mix...")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0 or not os.path.exists(output_path):
            logger.warning(f"[AudioMixer] Mix failed ({proc.stderr[:200]}), falling back to raw voiceover.")
            return voiceover_path

        logger.info(f"[AudioMixer] Final mixed audio created: {output_path}")
        return output_path

    def prepare_pure_music(
        self,
        duration_sec: float,
        output_path: str,
        volume: float = 0.85
    ) -> str:
        """Prepare pure lo-fi music suited for Reels with fade-out and zero voiceover."""
        music_path = self.ensure_background_music()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fade_start = max(0.0, duration_sec - 1.5)

        cmd = [
            self.ffmpeg_bin, "-y",
            "-i", music_path,
            "-t", str(duration_sec),
            "-filter_complex",
            f"volume={volume},afade=t=out:st={fade_start:.2f}:d=1.5",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            output_path
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0 or not os.path.exists(output_path):
            raise RuntimeError(f"Failed preparing background music: {proc.stderr}")
        logger.info(f"[AudioMixer] Prepared pure music track ({duration_sec}s): {output_path}")
        return output_path
