"""Publishing job state machine enums and models."""

from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.app.models.base import MongoBaseModel


class JobState(str, Enum):
    IDLE = "IDLE"
    IDEA = "IDEA"
    RESEARCHING = "RESEARCHING"
    SCRIPTING = "SCRIPTING"
    STORYBOARDING = "STORYBOARDING"
    GENERATING_MEDIA = "GENERATING_MEDIA"
    GENERATING_VOICE = "GENERATING_VOICE"
    GENERATING_CAPTIONS = "GENERATING_CAPTIONS"
    GENERATED = "GENERATED"
    RENDERING = "RENDERING"
    RENDERED = "RENDERED"
    QUALITY_CHECK = "QUALITY_CHECK"
    QC_PASSED = "QC_PASSED"
    QC_FAILED = "QC_FAILED"
    CAPTION_WRITING = "CAPTION_WRITING"
    READY = "READY"
    UPLOADING_CONTAINER = "UPLOADING_CONTAINER"
    POLLING_CONTAINER = "POLLING_CONTAINER"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class JobStageLog(BaseModel):
    stage: JobState
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    duration_ms: int = 0
    status: str = "COMPLETED"  # RUNNING, COMPLETED, FAILED
    details: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class PublishingJob(MongoBaseModel):
    workspace_id: str = "default_workspace"
    topic: str
    niche: str = "Technology & AI"
    state: JobState = JobState.IDLE
    slot_index: Optional[int] = None
    slot_date: Optional[str] = None
    current_stage: str = "IDLE"
    error_message: Optional[str] = None
    stage_logs: List[JobStageLog] = Field(default_factory=list)
    video_id: Optional[str] = None
    instagram_media_id: Optional[str] = None
    instagram_url: Optional[str] = None
    published_at: Optional[datetime] = None
