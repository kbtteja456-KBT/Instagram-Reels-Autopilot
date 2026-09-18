"""Activity stream event log models for Server-Sent Events (SSE)."""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ActivityLog(BaseModel):
    event_id: str
    workspace_id: str = "default_workspace"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    level: str = "INFO"  # INFO, WARNING, ERROR, SUCCESS
    stage: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
