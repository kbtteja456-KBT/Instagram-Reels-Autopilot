"""VoiceAgent: Edge-TTS neural speech synthesis and audio ducking."""

import os
from pathlib import Path
from typing import Optional
from backend.app.agents.base import BaseAgent
from backend.app.config import settings
from backend.app.agents.script import ReelScript
from backend.app.providers.tts.edge_tts_provider import EdgeTTSVoiceProvider


class VoiceAgent(BaseAgent):
    """Generates crystal clear neural voiceovers with automated level calibration."""

    def __init__(self, tts_provider: Optional[EdgeTTSVoiceProvider] = None):
        super().__init__("VoiceAgent")
        self.tts = tts_provider or EdgeTTSVoiceProvider()

    async def generate_voiceover(self, script: ReelScript, job_id: str) -> str:
        self.log(f"Synthesizing neural voiceover for Reel script ({len(script.full_narration_text)} chars)...")
        
        job_audio = settings.temp_path / job_id / "audio"
        job_audio.mkdir(parents=True, exist_ok=True)
        out_path = str(job_audio / "voiceover.mp3")

        await self.tts.synthesize(
            text=script.full_narration_text,
            output_path=out_path
        )
        return out_path
