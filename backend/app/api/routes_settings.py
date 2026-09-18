"""Autopilot scheduling, timezone, and Zero-Cost settings endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.core.auth import get_optional_current_user
from backend.app.core.logging import logger

router = APIRouter(prefix="/settings", tags=["settings"])


class UpdateSettingsRequest(BaseModel):
    timezone: str = "Asia/Kolkata"
    slot1_time: str = "07:00"
    slot2_time: str = "18:00"
    daily_reel_limit: int = 2
    zero_cost_mode: bool = True
    public_media_base_url: str = "http://localhost:8000"


@router.get("")
async def get_settings(user: Dict[str, Any] = Depends(get_optional_current_user)) -> Dict[str, Any]:
    """Return operational settings."""
    return {
        "timezone": settings.timezone,
        "slot1_time": settings.slot1_time,
        "slot2_time": settings.slot2_time,
        "daily_reel_limit": settings.daily_reel_limit,
        "zero_cost_mode": settings.zero_cost_mode,
        "public_media_base_url": settings.public_media_base_url,
        "meta_app_id": settings.meta_app_id,
        "instagram_api_version": settings.instagram_api_version,
    }


@router.put("")
async def update_settings(
    req: UpdateSettingsRequest,
    user: Dict[str, Any] = Depends(get_optional_current_user)
) -> Dict[str, Any]:
    """Update settings."""
    settings.timezone = req.timezone
    settings.slot1_time = req.slot1_time
    settings.slot2_time = req.slot2_time
    settings.daily_reel_limit = req.daily_reel_limit
    settings.zero_cost_mode = req.zero_cost_mode
    settings.public_media_base_url = req.public_media_base_url

    logger.info(f"[Settings] Updated: timezone={req.timezone}, slots=[{req.slot1_time}, {req.slot2_time}]")
    return {"status": "UPDATED", "settings": req.model_dump()}
