"""Microsoft Edge-TTS zero-cost neural voice synthesis provider."""

import asyncio
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import edge_tts

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider


class EdgeTTSVoiceProvider(BaseProvider):
    """Zero-cost neural text-to-speech using Microsoft Edge TTS."""

    DEFAULT_VOICE = "en-US-ChristopherNeural"

    def __init__(self, voice: Optional[str] = None):
        super().__init__("edge_tts")
        self.voice = voice or self.DEFAULT_VOICE

    async def health_check(self) -> Dict[str, Any]:
        return {
            "provider": self.name,
            "status": "HEALTHY",
            "voice": self.voice,
            "zero_cost": True
        }

    async def synthesize(self, text: str, output_path: str, rate: str = "+0%", pitch: str = "+0Hz") -> str:
        """Synthesize text into MP3 audio file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(text=text, voice=self.voice, rate=rate, pitch=pitch)
        await communicate.save(output_path)
        logger.info(f"[EdgeTTS] Generated voiceover: {output_path}")
        return output_path
