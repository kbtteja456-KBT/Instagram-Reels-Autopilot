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

# Curated viral royalty-free background tracks for high-retention Reels
VIRAL_TRACKS = [
    {
        "filename": "incompetech_sneaky_snitch.mp3",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Sneaky%20Snitch.mp3",
        "title": "Sneaky Snitch (Suspense & Thinking Beat)"
    },
    {
        "filename": "incompetech_pixel_peeker_polka.mp3",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Pixel%20Peeker%20Polka%20-%20faster.mp3",
        "title": "Pixel Peeker Polka (8-Bit Fast Tech Beat)"
    },
    {
        "filename": "incompetech_monkeys_spinning.mp3",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Monkeys%20Spinning%20Monkeys.mp3",
        "title": "Monkeys Spinning Monkeys (Upbeat Viral Rhythm)"
    },
    {
        "filename": "incompetech_investigations.mp3",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Investigations.mp3",
        "title": "Investigations (Curiosity & Mystery Beat)"
    },
    {
        "filename": "incompetech_carefree.mp3",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Carefree.mp3",
        "title": "Carefree (Upbeat Fun Beat)"
    }
]

import random


class AudioMixer:
    """Combines neural TTS voiceover with background music using FFmpeg."""

    _track_rotation_index: int = 0

    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_binary()
        self.assets_dir = Path(settings.media_storage_dir) / "assets"
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.music_pool_dir = self.assets_dir / "music_pool"
        self.music_pool_dir.mkdir(parents=True, exist_ok=True)
        self.cached_music_path = self.assets_dir / "lofi_bg_music.mp3"

    def ensure_background_music(self) -> str:
        """Select a fresh, upbeat viral background track from the music pool.
        Falls back to downloading iconic royalty-free tracks if pool is empty.
        """
        # 1. Check local music pool for available MP3s
        available_tracks = sorted(list(self.music_pool_dir.glob("*.mp3")))

        if available_tracks:
            # Rotate across available tracks so each video gets a fresh, exciting vibe
            idx = AudioMixer._track_rotation_index % len(available_tracks)
            AudioMixer._track_rotation_index += 1
            chosen_track = available_tracks[idx]
            logger.info(f"[AudioMixer] Selected upbeat music track ({idx + 1}/{len(available_tracks)}): {chosen_track.name}")
            return str(chosen_track)

        # 2. Check if default cached track exists and is valid
        if self.cached_music_path.exists() and self.cached_music_path.stat().st_size > 50000:
            return str(self.cached_music_path)

        # 3. Download premier viral track (Sneaky Snitch) if pool is empty
        primary = VIRAL_TRACKS[0]
        target_path = self.music_pool_dir / primary["filename"]
        try:
            logger.info(f"[AudioMixer] Downloading viral track '{primary['title']}'...")
            headers = {"User-Agent": "Mozilla/5.0"}
            req = urllib.request.Request(primary["url"], headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(target_path, "wb") as f:
                    f.write(resp.read())
            logger.info(f"[AudioMixer] Saved background music to {target_path}")
            return str(target_path)
        except Exception as e:
            logger.warning(f"[AudioMixer] Failed downloading background music: {e}. Generating procedural ambient beat.")
            fallback_path = str(self.music_pool_dir / "fallback_beat.mp3")
            self._generate_fallback_ambient(fallback_path, duration_sec=40)
            return fallback_path

    def _generate_fallback_ambient(self, out_path: str, duration_sec: int = 40):
        """Generate upbeat rhythmic chord progression using FFmpeg if completely offline."""
        cmd = [
            self.ffmpeg_bin, "-y",
            "-f", "lavfi",
            "-i", f"sine=frequency=440:sample_rate=44100:duration={duration_sec}",
            "-filter_complex", "volume=0.08,lowpass=f=800,atempo=1.2",
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
