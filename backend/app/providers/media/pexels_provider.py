"""Vertical 9:16 stock video provider with Pexels API and dynamic 1080x1920 generative fallback."""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx
import numpy as np
import cv2

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider


class PexelsMediaProvider(BaseProvider):
    """Pexels vertical 9:16 stock b-roll provider and procedural canvas compositor."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__("pexels")
        self.api_key = api_key or settings.pexels_api_key

    async def health_check(self) -> Dict[str, Any]:
        return {
            "provider": self.name,
            "status": "HEALTHY",
            "has_key": bool(self.api_key),
            "zero_cost": True
        }

    async def search_and_download_clip(self, query: str, duration_sec: float, output_path: str) -> str:
        """Download vertical clip from Pexels or synthesize a dynamic 1080x1920 generative background."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if self.api_key and not self.api_key.startswith("mock_"):
            try:
                headers = {
                    "Authorization": self.api_key,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page=5"
                async with httpx.AsyncClient(timeout=25.0) as client:
                    resp = await client.get(url, headers=headers)
                    data = resp.json()
                    videos = data.get("videos", [])
                    if videos:
                        video_files = videos[0].get("video_files", [])
                        # Look for HD vertical portrait
                        target_file = next(
                            (f for f in video_files if f.get("width", 0) < f.get("height", 0)),
                            video_files[0] if video_files else None
                        )
                        if target_file and "link" in target_file:
                            dl_resp = await client.get(target_file["link"], headers={"User-Agent": headers["User-Agent"]}, follow_redirects=True)
                            with open(output_path, "wb") as f:
                                f.write(dl_resp.content)
                            logger.info(f"[Pexels] Downloaded vertical stock clip for '{query}': {output_path}")
                            return output_path
            except Exception as e:
                logger.warning(f"[Pexels] Query '{query}' failed: {e}. Falling back to procedural canvas generator.")

        # Zero-Cost / Offline mode: Generate a dynamic 1080x1920 vertical canvas clip
        return self._generate_procedural_vertical_clip(query, duration_sec, output_path)

    def _generate_procedural_vertical_clip(self, query: str, duration_sec: float, output_path: str) -> str:
        """Procedurally generate a 1080x1920 30fps vertical video clip with tech gradients and particle glow."""
        width, height = 1080, 1920
        fps = 30
        total_frames = int(fps * max(duration_sec, 2.0))

        # FourCC for mp4
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Seed variations based on query
        q_hash = sum(ord(c) for c in query)
        hue_base = (q_hash % 180)

        logger.info(f"[MediaProvider] Generating 1080x1920 procedural vertical scene ({duration_sec:.1f}s) for '{query}'...")

        # Pre-generate 30 moving particles
        np.random.seed(q_hash % 1000)
        particles_x = np.random.uniform(50, width - 50, 40)
        particles_y = np.random.uniform(100, height - 100, 40)
        particles_speed = np.random.uniform(1.5, 4.0, 40)
        particles_radius = np.random.randint(4, 12, 40)

        for f in range(total_frames):
            progress = f / total_frames

            # Cyber gradient background
            h = int((hue_base + progress * 20) % 180)
            top_color = (int(15 + 10 * np.sin(progress * 3)), 15, int(30 + 20 * np.cos(progress * 2)))
            bottom_color = (int(5 + 5 * np.cos(progress * 3)), 5, int(15 + 10 * np.sin(progress * 2)))

            # Vertical gradient
            img = np.zeros((height, width, 3), dtype=np.uint8)
            y_indices = np.linspace(0, 1, height)[:, None]
            for c in range(3):
                img[:, :, c] = (top_color[c] * (1 - y_indices) + bottom_color[c] * y_indices).astype(np.uint8)

            # Draw subtle cybernetic grid lines
            grid_spacing = 120
            grid_offset = int((progress * 60) % grid_spacing)
            cv2.line(img, (0, 300 + grid_offset), (width, 300 + grid_offset), (30, 40, 60), 1)
            cv2.line(img, (0, 800 + grid_offset), (width, 800 + grid_offset), (30, 40, 60), 1)
            cv2.line(img, (0, 1300 + grid_offset), (width, 1300 + grid_offset), (30, 40, 60), 1)

            # Render glowing particles
            for p in range(len(particles_x)):
                py = int((particles_y[p] - f * particles_speed[p]) % (height - 100)) + 50
                px = int(particles_x[p] + 20 * np.sin((f + p * 10) * 0.05))
                rad = particles_radius[p]
                
                # Glow halo
                cv2.circle(img, (px, py), rad * 2, (60, 100, 140), -1)
                # Core bright particle
                cv2.circle(img, (px, py), rad, (140, 210, 255), -1)

            # Central tech emblem
            cx, cy = width // 2, height // 2 - 100
            pulse_rad = int(180 + 20 * np.sin(progress * np.pi * 4))
            cv2.circle(img, (cx, cy), pulse_rad, (45, 85, 120), 2)
            cv2.circle(img, (cx, cy), pulse_rad - 30, (30, 60, 90), 1)

            writer.write(img)

        writer.release()
        return output_path
