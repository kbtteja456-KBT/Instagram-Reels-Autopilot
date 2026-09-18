"""Instagram Account and OAuth Token storage models."""

from datetime import datetime, timezone
from typing import Optional, List
from pydantic import Field
from backend.app.models.base import MongoBaseModel


class InstagramAccount(MongoBaseModel):
    workspace_id: str
    page_id: Optional[str] = None
    page_name: Optional[str] = None
    instagram_user_id: str
    username: str
    name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    followers_count: int = 0
    follows_count: int = 0
    media_count: int = 0
    total_reel_plays: int = 0
    is_connected: bool = True
    last_synced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OAuthTokenRecord(MongoBaseModel):
    workspace_id: str
    instagram_user_id: str
    page_id: Optional[str] = None
    encrypted_long_lived_token: str
    encrypted_page_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    scopes: List[str] = Field(default_factory=list)
