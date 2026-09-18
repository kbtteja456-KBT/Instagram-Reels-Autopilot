"""API router aggregator for AI Instagram Reels Autopilot."""

from fastapi import APIRouter

from backend.app.api.routes_auth import router as auth_router
from backend.app.api.routes_instagram_auth import router as ig_auth_router
from backend.app.api.routes_videos import router as videos_router
from backend.app.api.routes_autopilot import router as autopilot_router
from backend.app.api.routes_settings import router as settings_router
from backend.app.api.routes_activity import router as activity_router
from backend.app.api.routes_media import router as media_router
from backend.app.api.routes_vault import router as vault_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(ig_auth_router)
api_router.include_router(videos_router)
api_router.include_router(autopilot_router)
api_router.include_router(settings_router)
api_router.include_router(activity_router)
api_router.include_router(media_router)
api_router.include_router(vault_router)
