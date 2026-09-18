"""Video, Reel, Scene, Storyboard, and Quality Control models."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.app.models.base import MongoBaseModel


class Scene(BaseModel):
    scene_number: int
    narration_chunk: str
    visual_direction: str
    duration_sec: float
    asset_path: Optional[str] = None
    asset_type: str = "video"  # "video" or "image"


class Storyboard(BaseModel):
    scenes: List[Scene] = Field(default_factory=list)
    total_duration_sec: float = 0.0


class QCReport(BaseModel):
    passed: bool
    score: float
    details: Dict[str, Any] = Field(default_factory=dict)
    remediation_notes: str = ""


class Reel(MongoBaseModel):
    workspace_id: Optional[str] = "default_workspace"
    job_id: str
    title: str
    caption: str
    hashtags: List[str] = Field(default_factory=list)
    file_path: str
    file_hash: str
    cover_image_path: Optional[str] = None
    duration_seconds: float = 0.0
    quality_score: float = 0.0
    qc_report: Optional[QCReport] = None
    
    # Instagram publishing fields
    instagram_media_id: Optional[str] = None
    instagram_url: Optional[str] = None
    instagram_published_at: Optional[datetime] = None
    
    slot_index: Optional[int] = None
    slot_date: Optional[str] = None
    status: str = "READY"  # GENERATING, READY, PUBLISHING, PUBLISHED, FAILED
