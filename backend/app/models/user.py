"""User and Tenant Workspace models."""

from typing import Optional, List
from pydantic import Field
from backend.app.models.base import MongoBaseModel


class Workspace(MongoBaseModel):
    name: str = "Default Workspace"
    owner_id: str
    plan: str = "pro"
    is_active: bool = True
    settings: dict = Field(default_factory=dict)


class User(MongoBaseModel):
    email: str
    hashed_password: str
    workspace_id: str
    full_name: Optional[str] = None
    role: str = "owner"  # owner, admin, editor
    is_active: bool = True
