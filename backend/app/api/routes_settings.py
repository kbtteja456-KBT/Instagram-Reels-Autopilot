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
    niche: str = "python program quiz card reels"
    custom_content_prompt: str = ""
    target_audience: str = "Programmers, Students & Python Developers"
    preferred_format: str = "auto"
    default_duration_sec: int = 45


@router.get("")
async def get_settings(user: Dict[str, Any] = Depends(get_optional_current_user)) -> Dict[str, Any]:
    """Return operational settings from DB or memory fallback."""
    from backend.app.core.db import AsyncMongoDB
    db = AsyncMongoDB.get_db()
    if db is not None:
        try:
            doc = await db.settings.find_one({"workspace_id": "default_workspace"})
            if doc:
                return {
                    "timezone": doc.get("timezone", settings.timezone),
                    "slot1_time": doc.get("slot1_time", settings.slot1_time),
                    "slot2_time": doc.get("slot2_time", settings.slot2_time),
                    "daily_reel_limit": doc.get("daily_reel_limit", settings.daily_reel_limit),
                    "zero_cost_mode": doc.get("zero_cost_mode", settings.zero_cost_mode),
                    "public_media_base_url": doc.get("public_media_base_url", settings.public_media_base_url),
                    "meta_app_id": settings.meta_app_id,
                    "instagram_api_version": settings.instagram_api_version,
                    "niche": doc.get("niche", getattr(settings, "niche", "python program quiz card reels")),
                    "custom_content_prompt": doc.get("custom_content_prompt", getattr(settings, "custom_content_prompt", "")),
                    "target_audience": doc.get("target_audience", getattr(settings, "target_audience", "Programmers, Students & Python Developers")),
                    "preferred_format": doc.get("preferred_format", getattr(settings, "preferred_format", "auto")),
                    "default_duration_sec": doc.get("default_duration_sec", getattr(settings, "default_duration_sec", 45))
                }
        except Exception as e:
            logger.warning(f"[Settings] Error fetching settings from DB: {e}")

    return {
        "timezone": settings.timezone,
        "slot1_time": settings.slot1_time,
        "slot2_time": settings.slot2_time,
        "daily_reel_limit": settings.daily_reel_limit,
        "zero_cost_mode": settings.zero_cost_mode,
        "public_media_base_url": settings.public_media_base_url,
        "meta_app_id": settings.meta_app_id,
        "instagram_api_version": settings.instagram_api_version,
        "niche": getattr(settings, "niche", "python program quiz card reels"),
        "custom_content_prompt": getattr(settings, "custom_content_prompt", ""),
        "target_audience": getattr(settings, "target_audience", "Programmers, Students & Python Developers"),
        "preferred_format": getattr(settings, "preferred_format", "auto"),
        "default_duration_sec": getattr(settings, "default_duration_sec", 45)
    }


@router.put("")
async def update_settings(
    req: UpdateSettingsRequest,
    user: Dict[str, Any] = Depends(get_optional_current_user)
) -> Dict[str, Any]:
    """Update settings in memory and persist in MongoDB."""
    settings.timezone = req.timezone
    settings.slot1_time = req.slot1_time
    settings.slot2_time = req.slot2_time
    settings.daily_reel_limit = req.daily_reel_limit
    settings.zero_cost_mode = req.zero_cost_mode
    settings.public_media_base_url = req.public_media_base_url
    settings.niche = req.niche
    settings.custom_content_prompt = req.custom_content_prompt
    settings.target_audience = req.target_audience
    settings.preferred_format = req.preferred_format
    settings.default_duration_sec = req.default_duration_sec

    from backend.app.core.db import AsyncMongoDB
    db = AsyncMongoDB.get_db()
    if db is not None:
        try:
            payload = req.model_dump()
            payload["workspace_id"] = "default_workspace"
            await db.settings.update_one(
                {"workspace_id": "default_workspace"},
                {"$set": payload},
                upsert=True
            )
            logger.info(f"[Settings] Persisted settings to MongoDB: niche='{req.niche}'")
        except Exception as e:
            logger.warning(f"[Settings] Failed to persist settings to DB: {e}")

    logger.info(f"[Settings] Updated: timezone={req.timezone}, niche={req.niche}, slots=[{req.slot1_time}, {req.slot2_time}]")
    return {"status": "UPDATED", "settings": req.model_dump()}
