"""Settings and Autopilot configuration models."""

from typing import List
from pydantic import BaseModel, Field
from backend.app.models.base import MongoBaseModel


class ZeroCostConfig(BaseModel):
    enabled: bool = True
    llm_provider: str = "openrouter_free"
    tts_provider: str = "edge_tts"
    stt_provider: str = "faster_whisper"
    stock_provider: str = "pexels"


class AutopilotConfig(MongoBaseModel):
    workspace_id: str = "default_workspace"
    is_active: bool = True
    timezone: str = "Asia/Kolkata"
    slot1_time: str = "07:00"
    slot2_time: str = "18:00"
    daily_reel_limit: int = 2
    default_niche: str = "Technology & AI"
    target_duration_sec: float = 45.0
    zero_cost: ZeroCostConfig = Field(default_factory=ZeroCostConfig)
    banned_keywords: List[str] = Field(default_factory=list)
    public_media_base_url: str = "http://localhost:8000"
