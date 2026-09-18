"""FastAPI backend application entrypoint for AI Instagram Reels Autopilot."""

import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.resources import resource_guard
from backend.app.core.db import AsyncMongoDB
from backend.app.api import api_router
from backend.app.core.cron_scheduler import start_autopilot_scheduler, stop_autopilot_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hooks."""
    logger.info("Initializing AI Instagram Reels Autopilot backend...")
    
    # 1. Verify encryption key
    from backend.app.core.security import get_encryption_key
    get_encryption_key()

    # 2. Ensure media storage paths exist
    settings.storage_path
    settings.temp_path
    settings.reels_output_path

    # 3. Connect to MongoDB
    await AsyncMongoDB.connect()

    # 4. Check hardware resource safety
    safe, warnings = resource_guard.verify_safe_to_render()
    if not safe:
        logger.warning(f"Resource safeguard warning: {', '.join(warnings)}")
    else:
        logger.info("System resources verified safe for rendering.")

    logger.info(f"Zero-Cost Mode: {'ACTIVE' if settings.zero_cost_mode else 'DISABLED'}")
    logger.info(f"Publishing Schedule: {settings.slot1_time} & {settings.slot2_time} ({settings.timezone})")
    logger.info(f"Meta Graph API Target Version: {settings.instagram_api_version}")

    # 5. Start background autonomous scheduler
    if settings.enable_internal_scheduler:
        start_autopilot_scheduler()

    yield

    logger.info("Shutting down AI Instagram Reels Autopilot backend...")
    stop_autopilot_scheduler()
    await AsyncMongoDB.disconnect()


app = FastAPI(
    title="AI Instagram Reels Autopilot API",
    description="Autonomous, local-first, zero-cost-by-default Instagram Reels publishing engine powered by Meta Graph API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local Vite development and custom domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main aggregated API routes under /api
app.include_router(api_router)

# Mount local media directory for serving preview MP4s
_media_dir = Path(settings.media_storage_dir).resolve()
_media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(_media_dir)), name="media")


@app.get("/health")
@app.get("/api/health")
async def health_check() -> dict[str, Any]:
    """Primary system health check returning hardware and operational stats."""
    metrics = resource_guard.get_system_metrics()
    return {
        "status": "HEALTHY",
        "app": "AI Instagram Reels Autopilot",
        "version": "1.0.0",
        "zero_cost_mode": settings.zero_cost_mode,
        "timezone": settings.timezone,
        "daily_reel_limit": settings.daily_reel_limit,
        "instagram_api_version": settings.instagram_api_version,
        "public_media_base_url": settings.public_media_base_url,
        "system_resources": metrics,
        "timestamp": time.time()
    }
