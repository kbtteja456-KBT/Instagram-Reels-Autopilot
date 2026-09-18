"""MediaAgent: Vertical 9:16 video asset collector and compositor."""

import os
from pathlib import Path
from typing import Optional
from backend.app.agents.base import BaseAgent
from backend.app.config import settings
from backend.app.models.video import Storyboard
from backend.app.providers.media.pexels_provider import PexelsMediaProvider


class MediaAgent(BaseAgent):
    """Collects 9:16 vertical b-roll footage for each storyboard scene."""

    def __init__(self, media_provider: Optional[PexelsMediaProvider] = None):
        super().__init__("MediaAgent")
        self.media_provider = media_provider or PexelsMediaProvider()

    async def collect_scene_assets(self, storyboard: Storyboard, job_id: str) -> Storyboard:
        self.log(f"Collecting vertical video assets for {len(storyboard.scenes)} scenes (Job: {job_id})...")
        
        job_temp = settings.temp_path / job_id / "media"
        job_temp.mkdir(parents=True, exist_ok=True)

        for scene in storyboard.scenes:
            out_file = str(job_temp / f"scene_{scene.scene_number}.mp4")
            if not os.path.exists(out_file):
                clip_path = await self.media_provider.search_and_download_clip(
                    query=scene.visual_direction,
                    duration_sec=scene.duration_sec,
                    output_path=out_file
                )
                scene.asset_path = clip_path
            else:
                scene.asset_path = out_file

        return storyboard
