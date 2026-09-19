"""Video and Reel generation, preview, and manual publishing routes."""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel

from backend.app.core.auth import get_optional_current_user
from backend.app.core.db import AsyncMongoDB
from backend.app.core.logging import logger
from backend.app.pipeline.orchestrator import create_default_orchestrator
from backend.app.models.video import Reel

router = APIRouter(prefix="/videos", tags=["videos"])

# In-memory reels fallback for quick response & local runs
_mock_reels_store: List[Dict[str, Any]] = [
    {
        "_id": "reel_001",
        "job_id": "job_init_01",
        "title": "3 Autonomous AI Workflows Changing Coding Forever",
        "caption": "⚡ If you are still writing boilerplate by hand in 2026, stop immediately.\n\nAutonomous agent systems can now plan, compose, and deploy full stack features in minutes. Here's how the top 1% of engineers are using it.\n\n👉 Save this Reel for later!\n#reels #viral #tech #ai #software #developer #future",
        "hashtags": ["#reels", "#viral", "#tech", "#ai", "#software"],
        "file_path": "./media_storage/reels/reel_demo_01.mp4",
        "file_hash": "a1b2c3d4e5f67890",
        "duration_seconds": 44.5,
        "quality_score": 96.0,
        "status": "PUBLISHED",
        "instagram_media_id": "180293847561829",
        "instagram_url": "https://www.instagram.com/reel/C_DemoTech123/",
        "slot_index": 1,
        "slot_date": "2026-09-11",
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "_id": "reel_002",
        "job_id": "job_init_02",
        "title": "The Quantum Computing Shift Nobody Is Talking About",
        "caption": "Microscopic chips operating at absolute zero temperatures are beating supercomputers.\n\nSave this breakdown before it trends!\n#reels #science #quantum #physics #explorepage",
        "hashtags": ["#reels", "#science", "#quantum", "#physics"],
        "file_path": "./media_storage/reels/reel_demo_02.mp4",
        "file_hash": "f6e5d4c3b2a19988",
        "duration_seconds": 42.0,
        "quality_score": 94.5,
        "status": "READY",
        "instagram_media_id": None,
        "instagram_url": None,
        "slot_index": 2,
        "slot_date": "2026-09-11",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
]


class GenerateReelRequest(BaseModel):
    topic: str
    niche: str = "Technology & AI"
    target_duration_sec: float = 45.0
    publish_immediately: bool = False


@router.get("")
async def list_reels(user: Dict[str, Any] = Depends(get_optional_current_user)) -> List[Dict[str, Any]]:
    """Return all rendered Reels for the current workspace."""
    workspace_id = user.get("workspace_id", "default_workspace")
    db = AsyncMongoDB.get_db()
    
    if db is not None:
        try:
            cursor = db.reels.find().sort("created_at", -1)
            docs = await cursor.to_list(length=100)
            if docs:
                for d in docs:
                    d["_id"] = str(d.get("_id"))
                return docs
        except Exception as e:
            logger.warning(f"[VideosAPI] Query failed: {e}")

    return _mock_reels_store


@router.post("/generate")
async def trigger_reel_generation(
    req: GenerateReelRequest,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(get_optional_current_user)
) -> Dict[str, Any]:
    """Trigger the 14-agent pipeline to produce a new Instagram Reel."""
    logger.info(f"[VideosAPI] Triggering Reel generation for topic: '{req.topic}'...")

    orchestrator = create_default_orchestrator()

    async def _run_task():
        try:
            res = await orchestrator.execute_full_flow(
                topic=req.topic,
                niche=req.niche,
                publish_immediately=req.publish_immediately
            )
            # Add to mock store
            _mock_reels_store.insert(0, {
                "_id": f"reel_{res.get('job_id', 'new')}",
                "job_id": res.get("job_id"),
                "title": res.get("title", req.topic),
                "caption": res.get("caption", "High impact breakdown. #reels #viral"),
                "hashtags": ["#reels", "#viral", "#tech"],
                "file_path": res.get("video_path", "./media_storage/reels/reel_new.mp4"),
                "file_hash": "hash_" + res.get("job_id", "gen"),
                "duration_seconds": req.target_duration_sec,
                "quality_score": res.get("quality_score", 95.0),
                "status": res.get("status", "READY"),
                "instagram_media_id": res.get("instagram_media_id"),
                "instagram_url": res.get("instagram_url"),
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        except Exception as err:
            logger.error(f"[VideosAPI] Generation error: {err}", exc_info=True)

    background_tasks.add_task(_run_task)

    return {
        "status": "ACCEPTED",
        "message": f"Autonomous pipeline initiated for '{req.topic}'. Track progress in live activity feed.",
        "topic": req.topic,
        "niche": req.niche
    }


@router.post("/{video_id}/publish")
async def publish_existing_reel(
    video_id: str,
    user: Dict[str, Any] = Depends(get_optional_current_user)
) -> Dict[str, Any]:
    """Publish a READY or RENDERED video to Instagram using the 2-step containerized flow."""
    logger.info(f"[VideosAPI] Publishing Reel {video_id} to Instagram...")
    
    target = None
    db = AsyncMongoDB.get_db()
    
    # 1. Search in MongoDB reels collection
    if db is not None:
        try:
            from bson import ObjectId
            if ObjectId.is_valid(video_id):
                target = await db.reels.find_one({"_id": ObjectId(video_id)})
            if not target:
                target = await db.reels.find_one({"job_id": video_id})
        except Exception as e:
            logger.warning(f"[VideosAPI] DB search failed for {video_id}: {e}")

    # 2. Fallback to mock store
    if not target:
        for r in _mock_reels_store:
            if r["_id"] == video_id or r.get("job_id") == video_id:
                target = r
                break

    if not target:
        raise HTTPException(status_code=404, detail=f"Reel '{video_id}' not found.")

    from backend.app.config import settings
    from backend.app.providers.instagram.instagram_client import InstagramClient
    from backend.app.agents.instagram import InstagramAgent

    client = InstagramClient(
        access_token=settings.effective_instagram_token,
        ig_user_id=settings.effective_instagram_account_id
    )
    agent = InstagramAgent(client)

    file_path = target.get("file_path", "")
    caption = target.get("caption", "Python Quiz Reel #python #coding #quiz")

    result = await agent.publish_reel(
        video_filepath=file_path,
        caption=caption
    )

    # Update MongoDB if connected
    if db is not None and "_id" in target:
        try:
            await db.reels.update_one(
                {"_id": target["_id"]},
                {"$set": {
                    "status": "PUBLISHED",
                    "instagram_media_id": result["instagram_media_id"],
                    "instagram_url": result["instagram_url"],
                    "instagram_published_at": datetime.now(timezone.utc).isoformat()
                }}
            )
        except Exception as e:
            logger.warning(f"[VideosAPI] Failed to update published reel in DB: {e}")

    target["status"] = "PUBLISHED"
    target["instagram_media_id"] = result["instagram_media_id"]
    target["instagram_url"] = result["instagram_url"]

    return {
        "status": "PUBLISHED",
        "instagram_media_id": result["instagram_media_id"],
        "instagram_url": result["instagram_url"]
    }

